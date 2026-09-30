"""RSS and Atom source adapter."""

from datetime import datetime, timezone

import feedparser
import httpx

from .base import CollectedItem


class RSSAdapter:
    """Collect RSS or Atom entries through feedparser."""

    def __init__(self, url: str, source_name: str, *, timeout: float = 20.0, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.url = url
        self.source_name = source_name
        self.timeout = timeout
        self.transport = transport

    async def collect(self) -> list[CollectedItem]:
        async with httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client:
            response = await client.get(self.url)
            response.raise_for_status()

        feed = feedparser.parse(response.content)
        if feed.bozo and not feed.entries:
            raise RuntimeError(f"Failed to parse feed: {self.url}")

        return [
            CollectedItem(
                title=getattr(entry, "title", "Untitled").strip(),
                url=getattr(entry, "link", "").strip(),
                content=getattr(entry, "summary", "").strip(),
                source_name=self.source_name,
                published_at=_published_at(entry),
                metadata={"source_type": "rss"},
            )
            for entry in feed.entries
            if getattr(entry, "link", "").strip()
        ]


def _published_at(entry) -> datetime | None:
    parsed = getattr(entry, "published_parsed", None)
    if not parsed:
        return None

    return datetime(*parsed[:6], tzinfo=timezone.utc)
