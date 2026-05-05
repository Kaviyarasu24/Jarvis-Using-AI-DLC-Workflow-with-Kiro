"""
NewsModule — fetches headlines from Google News RSS feed.
No API key required. Uses stdlib urllib + xml.etree only.
"""

import logging
import re
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

GOOGLE_NEWS_RSS = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
TOPIC_FEEDS = {
    "top":         "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "technology":  "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pKVGlnQVAB",
    "science":     "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pKVGlnQVAB",
    "business":    "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pKVGlnQVAB",
    "health":      "https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ",
    "sports":      "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pKVGlnQVAB",
    "world":       "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pKVGlnQVAB",
}


@dataclass
class NewsItem:
    title: str
    link: str
    source: str
    published: str   # ISO 8601
    published_ago: str  # "2h ago"


def _clean_title(title: str) -> str:
    """Remove source suffix like ' - BBC News' from Google News titles."""
    return re.sub(r'\s*-\s*[^-]+$', '', title).strip()


def _time_ago(pub_str: str) -> str:
    """Convert RFC 2822 date string to relative time."""
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(pub_str)
        now = datetime.now(timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "just now"
        if seconds < 3600:
            return f"{seconds // 60}m ago"
        if seconds < 86400:
            return f"{seconds // 3600}h ago"
        return f"{seconds // 86400}d ago"
    except Exception:
        return ""


def fetch_news(topic: str = "top", max_items: int = 20) -> list[dict]:
    """Fetch news headlines from Google News RSS. Returns list of dicts."""
    url = TOPIC_FEEDS.get(topic, TOPIC_FEEDS["top"])
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (JARVIS News Reader)"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read()

        root = ET.fromstring(xml_data)
        channel = root.find("channel")
        if channel is None:
            return []

        items = []
        for item in channel.findall("item")[:max_items]:
            title_el = item.find("title")
            link_el = item.find("link")
            pub_el = item.find("pubDate")
            source_el = item.find("source")

            title = _clean_title(title_el.text or "") if title_el is not None else ""
            link = link_el.text or "" if link_el is not None else ""
            pub_raw = pub_el.text or "" if pub_el is not None else ""
            source = source_el.text or "" if source_el is not None else ""

            if not title:
                continue

            items.append({
                "title": title,
                "link": link,
                "source": source,
                "published": pub_raw,
                "published_ago": _time_ago(pub_raw),
            })

        return items

    except Exception as e:
        logger.error(f"News fetch failed: {e}")
        return []
