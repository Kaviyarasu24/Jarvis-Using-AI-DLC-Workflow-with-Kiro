"""
BrowserModule — web search using DuckDuckGo + direct HTTP page fetching.

Replaces browser-use (which requires an LLM to drive a real browser) with a
lightweight pipeline:
  1. DuckDuckGo Lite HTML search  →  extract top result URLs
  2. Fetch each page with httpx    →  extract readable text via BeautifulSoup
  3. Summarize with Ollama AICore  →  return clean answer to chat

No Playwright, no subprocess, no event-loop conflicts.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from .config_manager import ConfigManager

logger = logging.getLogger(__name__)

# How many search result pages to fetch and read
MAX_PAGES = 3
# Max characters of page text to feed into the summarizer
MAX_TEXT_PER_PAGE = 1500
# httpx timeout for each request
HTTP_TIMEOUT = 15

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class BrowserResult:
    success: bool
    query: str
    summary: str
    sources: list = field(default_factory=list)
    error: Optional[str] = None


class BrowserModule:
    """
    Handles web search and information retrieval.
    Uses DuckDuckGo Lite + httpx — no browser binary required.
    """

    def __init__(self, config: ConfigManager, ai_core=None) -> None:
        self._config = config
        self._ai_core = ai_core

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def handle(self, message: str) -> dict:
        query = self._extract_query(message)
        result = await self.search(query)
        if result.success:
            text = result.summary
            if result.sources:
                text += "\n\nSources:\n" + "\n".join(f"• {s}" for s in result.sources[:3])
            return {"text": text, "message_type": "text"}
        return {"text": f"Web search failed: {result.error}", "message_type": "text"}

    async def search(self, query: str) -> BrowserResult:
        logger.info(f"Web search: {query!r}")
        try:
            urls = await self._ddg_search(query)
            if not urls:
                return BrowserResult(
                    success=False, query=query, summary="",
                    error="No search results found. Try rephrasing your query.",
                )

            # Fetch and extract text from top pages
            pages: list[dict] = []
            async with httpx.AsyncClient(
                headers=HEADERS,
                timeout=HTTP_TIMEOUT,
                follow_redirects=True,
            ) as client:
                for url in urls[:MAX_PAGES]:
                    text = await self._fetch_page_text(client, url)
                    if text:
                        pages.append({"url": url, "text": text})

            if not pages:
                return BrowserResult(
                    success=False, query=query, summary="",
                    error="Could not retrieve content from search results.",
                )

            # Build context for summarizer
            context = ""
            sources = []
            for page in pages:
                context += f"\n\n--- Source: {page['url']} ---\n{page['text']}"
                if page["url"]:  # guard against empty URLs
                    sources.append(page["url"])

            summary = await self._summarize(query, context)
            return BrowserResult(success=True, query=query, summary=summary, sources=sources)

        except Exception as e:
            logger.error(f"Web search error: {e}", exc_info=True)
            return BrowserResult(
                success=False, query=query, summary="",
                error="Web search failed. Check your internet connection.",
            )

    # ------------------------------------------------------------------
    # Internal: DuckDuckGo Lite search
    # ------------------------------------------------------------------

    async def _ddg_search(self, query: str) -> list[str]:
        """Search DuckDuckGo Lite and return a list of result URLs."""
        try:
            async with httpx.AsyncClient(
                headers=HEADERS, timeout=HTTP_TIMEOUT, follow_redirects=True
            ) as client:
                resp = await client.post(
                    "https://lite.duckduckgo.com/lite/",
                    data={"q": query, "kl": "us-en"},
                )
                resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            urls = []

            # DDG Lite result links are in <a class="result-link"> or plain <a> inside result rows
            for a in soup.find_all("a", class_="result-link"):
                href = a.get("href", "")
                if href.startswith("http") and not _is_junk_url(href):
                    urls.append(href)

            # Fallback: any link that looks like a real result
            if not urls:
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("http") and not _is_junk_url(href):
                        urls.append(href)

            # Deduplicate while preserving order
            seen = set()
            deduped = []
            for u in urls:
                if u not in seen:
                    seen.add(u)
                    deduped.append(u)

            logger.info(f"DDG returned {len(deduped)} URLs for {query!r}")
            return deduped[:MAX_PAGES + 2]  # fetch a few extras in case some fail

        except Exception as e:
            logger.warning(f"DDG search failed: {e}")
            return []

    # ------------------------------------------------------------------
    # Internal: page fetching + text extraction
    # ------------------------------------------------------------------

    async def _fetch_page_text(self, client: httpx.AsyncClient, url: str) -> str:
        """Fetch a URL and return clean readable text (truncated)."""
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            ct = resp.headers.get("content-type", "")
            if "html" not in ct:
                return ""

            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove noise
            for tag in soup(["script", "style", "nav", "footer", "header",
                              "aside", "form", "noscript", "iframe"]):
                tag.decompose()

            # Prefer article / main content blocks
            for selector in ["article", "main", '[role="main"]', ".content",
                              "#content", ".post-body", ".entry-content"]:
                block = soup.select_one(selector)
                if block:
                    text = block.get_text(separator=" ", strip=True)
                    if len(text) > 200:
                        return _clean_text(text)[:MAX_TEXT_PER_PAGE]

            # Fallback: all body text
            body = soup.find("body")
            if body:
                return _clean_text(body.get_text(separator=" ", strip=True))[:MAX_TEXT_PER_PAGE]

            return ""
        except Exception as e:
            logger.debug(f"Failed to fetch {url}: {e}")
            return ""

    # ------------------------------------------------------------------
    # Internal: summarization
    # ------------------------------------------------------------------

    async def _summarize(self, query: str, context: str) -> str:
        if self._ai_core:
            try:
                # Use _ollama_chat directly — bypasses conversation history so the
                # web scrape context doesn't pollute the chat and doesn't overflow
                # the model's context window with prior messages.
                # Keep the prompt short: query + trimmed context only.
                trimmed = context[:2500]
                prompt = (
                    f"Answer this query using only the search results below. "
                    f"Be direct and factual. Include key numbers if relevant.\n\n"
                    f"Query: {query}\n\n"
                    f"Search results:{trimmed}"
                )
                import asyncio
                summary = await asyncio.wait_for(
                    self._ai_core._ollama_chat(
                        messages=[{"role": "user", "content": prompt}],
                        system="You are a helpful assistant that summarizes web search results concisely.",
                    ),
                    timeout=25.0,
                )
                return summary
            except asyncio.TimeoutError:
                logger.warning("Summarization timed out — returning formatted raw extract")
            except Exception as e:
                logger.warning(f"Summarization failed: {e}")

        return _format_raw_context(context)

    # ------------------------------------------------------------------
    # Internal: query extraction
    # ------------------------------------------------------------------

    def _extract_query(self, message: str) -> str:
        patterns = [
            r"search(?:\s+for)?\s+(.+)",
            r"find\s+(?:information\s+(?:about|on)\s+)?(.+)",
            r"look\s+up\s+(.+)",
            r"what\s+(?:is|are)\s+(.+)",
            r"who\s+is\s+(.+)",
            r"how\s+to\s+(.+)",
            r"browse\s+(?:to\s+)?(.+)",
            r"google\s+(.+)",
        ]
        for pattern in patterns:
            m = re.search(pattern, message, re.IGNORECASE)
            if m:
                return m.group(1).strip().rstrip("?.")
        return message.strip()


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _is_junk_url(url: str) -> bool:
    """Filter out ad networks, trackers, and DDG internal links."""
    junk = ("duckduckgo.com", "doubleclick", "googlesyndication",
            "amazon-adsystem", "javascript:", "mailto:")
    return any(j in url for j in junk)


def _clean_text(text: str) -> str:
    """Collapse whitespace and remove very short lines."""
    lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 30]
    return " ".join(lines)


def _format_raw_context(context: str) -> str:
    """
    Format raw multi-source context into a readable fallback response
    when Ollama summarization is unavailable or timed out.
    """
    sections = []
    # Split on the source markers we inserted
    parts = re.split(r'--- Source: (https?://[^\s-]+[^\s]*) ---', context)
    # parts alternates: [pre, url1, text1, url2, text2, ...]
    i = 1
    while i + 1 < len(parts):
        url = parts[i].strip()
        text = parts[i + 1].strip()[:400]
        if text:
            sections.append(f"**{url}**\n{text}")
        i += 2

    if sections:
        return "\n\n".join(sections)
    return context[:600].strip()
