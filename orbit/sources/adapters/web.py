"""Web page extraction adapter."""

import httpx
from bs4 import BeautifulSoup

from .base import CollectedItem


class WebPageAdapter:
    """Extract readable text from a web page without executing scripts."""

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
            follow_redirects=True,
            transport=self.transport,
        ) as client:
            response = await client.get(self.url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for element in soup(["script", "style", "noscript"]):
            element.decompose()

        title = soup.title.get_text(strip=True) if soup.title else self.url
        content = " ".join(soup.get_text(" ").split())

        return [
            CollectedItem(
                title=title,
                url=str(response.url),
                content=content,
                source_name=self.source_name,
                metadata={"source_type": "web"},
            )
        ]