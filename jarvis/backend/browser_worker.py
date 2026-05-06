"""
browser_worker.py — standalone script executed as a subprocess by BrowserModule.

Runs in its own Python process with a clean ProactorEventLoop (Windows default),
completely isolated from FastAPI's event loop.  Reads a JSON task from stdin,
writes a JSON result to stdout.

Usage (internal — called by BrowserModule):
    python -m backend.browser_worker
    stdin:  {"query": "...", "model": "...", "base_url": "..."}
    stdout: {"success": true, "text": "...", "sources": [...]}
         or {"success": false, "error": "..."}
"""

import asyncio
import json
import re
import sys


async def run(query: str, model: str, base_url: str) -> dict:
    try:
        from browser_use import Agent
        from langchain_ollama import ChatOllama

        llm = ChatOllama(model=model, base_url=base_url)
        task = (
            f"Search the web for: {query}\n"
            f"Extract the most relevant information and return a clear, concise summary. "
            f"Also list the URLs of the sources you used."
        )
        agent = Agent(task=task, llm=llm)
        result = await agent.run()
        raw = str(result) if result else ""
        sources = list(dict.fromkeys(re.findall(r'https?://[^\s\)\"\']+', raw)))[:5]
        return {"success": True, "text": raw, "sources": sources}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    payload = json.loads(sys.stdin.read())
    result = asyncio.run(run(
        query=payload["query"],
        model=payload["model"],
        base_url=payload["base_url"],
    ))
    sys.stdout.write(json.dumps(result))
    sys.stdout.flush()
