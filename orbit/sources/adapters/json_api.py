"""Simple JSON API source adapter."""

from typing import Any

import httpx

from .base import CollectedItem


class JSONAPIAdapter:
    """Normalize a JSON list endpoint into collected items."""

    def __init__(
        self,
        url: str,
        source_name: str,
        *,
        items_key: str = "items",
        title_key: str = "title",
        url_key: str = "url",
        content_key: str = "content",
        timeout: float = 20.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.url = url
        self.source_name = source_name
        self.items_key = items_key
        self.title_key = title_key
        self.url_key = url_key
        self.content_key = content_key
        self.timeout = timeout
        self.transport = transport

    async def collect(self) -> list[CollectedItem]:
        async with httpx.AsyncClient(
            timeout=self.timeout,
            transport=self.transport,
        ) as client:
            response = await client.get(self.url)
            response.raise_for_status()
            payload = response.json()

        raw_items = payload.get(self.items_key, payload)
        if not isinstance(raw_items, list):
            raise RuntimeError(f"JSON API field '{self.items_key}' is not a list")

        return [
            _item(
                raw,
                source_name=self.source_name,
                title_key=self.title_key,
                url_key=self.url_key,
                content_key=self.content_key,
            )
            for raw in raw_items
            if isinstance(raw, dict) and raw.get(self.url_key)
        ]


def _item(
    raw: dict[str, Any],
    *,
    source_name: str,
    title_key: str,
    url_key: str,
    content_key: str,
) -> CollectedItem:
    return CollectedItem(
        title=str(raw.get(title_key, "Untitled")),
        url=str(raw[url_key]),
        content=str(raw.get(content_key, "")),
        source_name=source_name,
        metadata={"source_type": "json_api", "raw": raw},
    )