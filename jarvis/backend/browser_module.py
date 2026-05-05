"""
BrowserModule — web search and information retrieval using browser-use.
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from .config_manager import ConfigManager

logger = logging.getLogger(__name__)

SEARCH_TIMEOUT = 60  # seconds


@dataclass
class BrowserResult:
    success: bool
    query: str
    summary: str
    sources: list = field(default_factory=list)
    error: Optional[str] = None


class BrowserModule:
    """
    Handles web search and information retrieval via browser-use.
    Falls back gracefully if browser-use is unavailable.
    """

    def __init__(self, config: ConfigManager, ai_core=None) -> None:
        self._config = config
        self._ai_core = ai_core  # Used to summarize results
        self._browser_available = self._check_browser_use()

    def _check_browser_use(self) -> bool:
        try:
            import browser_use  # noqa: F401
            return True
        except ImportError:
            logger.warning("browser-use not installed — web search disabled.")
            return False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def handle(self, message: str) -> dict:
        """Parse search intent from message and execute search."""
        intent = self._extract_query(message)
        result = await self.search(intent.query)

        if result.success:
            text = result.summary
            if result.sources:
                sources_text = "\n\nSources:\n" + "\n".join(f"• {s}" for s in result.sources[:3])
                text += sources_text
            return {"text": text, "message_type": "text"}
        return {"text": f"Web search failed: {result.error}", "message_type": "text"}

    async def search(self, query: str) -> BrowserResult:
        """Execute a web search for the given query."""
        if not self._browser_available:
            return BrowserResult(
                success=False,
                query=query,
                summary="",
                error="Web search is not available. Please install browser-use: pip install browser-use",
            )

        try:
            result = await asyncio.wait_for(
                self._run_browser_search(query),
                timeout=SEARCH_TIMEOUT,
            )
            return result
        except asyncio.TimeoutError:
            logger.warning(f"Browser search timed out for query: {query!r}")
            return BrowserResult(
                success=False,
                query=query,
                summary="",
                error="Search timed out. Please try again.",
            )
        except Exception as e:
            logger.error(f"Browser search failed: {e}")
            return BrowserResult(
                success=False,
                query=query,
                summary="",
                error="Web search failed. Please check your internet connection.",
            )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _run_browser_search(self, query: str) -> BrowserResult:
        """Run browser-use agent to search and extract content."""
        try:
            from browser_use import Agent
            from langchain_ollama import ChatOllama

            llm = ChatOllama(
                model=self._config.ollama_model,
                base_url=self._config.ollama_base_url,
            )

            task = (
                f"Search the web for: {query}\n"
                f"Extract the most relevant information and return a clear, concise summary. "
                f"Also list the URLs of the sources you used."
            )

            loop = asyncio.get_event_loop()
            agent = Agent(task=task, llm=llm)

            # Run in executor since browser-use may block
            raw_result = await loop.run_in_executor(None, lambda: asyncio.run(agent.run()))

            # Extract text and sources from result
            result_text = str(raw_result) if raw_result else ""
            sources = re.findall(r'https?://[^\s\)\"\']+', result_text)

            # Summarize with AICore if available
            if self._ai_core and result_text:
                summary_prompt = (
                    f"Summarize the following web search results for the query '{query}' "
                    f"in a clear, concise way:\n\n{result_text[:3000]}"
                )
                summary = await self._ai_core.chat(summary_prompt)
            else:
                summary = result_text[:1000] if result_text else "No results found."

            return BrowserResult(
                success=True,
                query=query,
                summary=summary,
                sources=list(dict.fromkeys(sources))[:5],  # deduplicate, max 5
            )

        except Exception as e:
            raise RuntimeError(f"browser-use agent failed: {e}") from e

    def _extract_query(self, message: str) -> "SearchIntent":
        """Extract search query from natural language message."""
        patterns = [
            r"search(?:\s+for)?\s+(.+)",
            r"find\s+(?:information\s+(?:about|on)\s+)?(.+)",
            r"look\s+up\s+(.+)",
            r"what\s+is\s+(.+)",
            r"who\s+is\s+(.+)",
            r"how\s+to\s+(.+)",
            r"browse\s+(?:to\s+)?(.+)",
            r"google\s+(.+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                query = match.group(1).strip().rstrip("?.")
                return SearchIntent(query=query, is_url=False)

        # Direct URL
        if message.strip().startswith("http"):
            return SearchIntent(query=message.strip(), is_url=True)

        # Fallback: use full message
        return SearchIntent(query=message.strip(), is_url=False)


@dataclass
class SearchIntent:
    query: str
    is_url: bool = False
