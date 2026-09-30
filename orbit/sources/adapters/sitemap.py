"""XML sitemap source adapter."""

import xml.etree.ElementTree as ET

import httpx

from .base import CollectedItem


class SitemapAdapter:
    """Collect URLs from an XML sitemap."""

    def __init__(
        self,
        url: str,
        source_name: str,
        *,
        timeout: float = 20.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.url = url
        self.source_name = source_name
        self.timeout = timeout
        self.transport = transport

    async def collect(self) -> list[CollectedItem]:
        async with httpx.AsyncClient(
            timeout=self.timeout,
            transport=self.transport,
        ) as client:
            response = await client.get(self.url)
            response.raise_for_status()

        root = ET.fromstring(response.content)
        urls = [
            element.text.strip()
            for element in root.iter()
            if element.tag.split("}")[-1] == "loc" and element.text
        ]

        return [
            CollectedItem(
                title=url.rsplit("/", maxsplit=1)[-1] or url,
                url=url,
                content="",
                source_name=self.source_name,
                metadata={"source_type": "sitemap"},
            )
            for url in urls
        ]