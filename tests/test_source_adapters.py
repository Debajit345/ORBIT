import httpx
import pytest

from orbit.sources import (
    JSONAPIAdapter,
    RSSAdapter,
    SitemapAdapter,
    WebPageAdapter,
)


def transport_for(body: str, content_type: str = "text/plain") -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=body.encode(),
            headers={"content-type": content_type},
        )

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_rss_adapter_normalizes_entries() -> None:
    feed = """<?xml version="1.0"?><rss version="2.0"><channel>
    <item><title>Headline</title><link>https://example.com/a</link>
    <description>Summary</description></item></channel></rss>"""

    items = await RSSAdapter(
        "https://example.com/feed",
        "Example",
        transport=transport_for(feed, "application/rss+xml"),
    ).collect()

    assert items[0].title == "Headline"
    assert items[0].metadata["source_type"] == "rss"


@pytest.mark.asyncio
async def test_sitemap_json_and_web_adapters_normalize_items() -> None:
    sitemap = "<urlset><url><loc>https://example.com/a</loc></url></urlset>"
    sitemap_items = await SitemapAdapter(
        "https://example.com/sitemap.xml",
        "Example",
        transport=transport_for(sitemap, "application/xml"),
    ).collect()
    assert sitemap_items[0].url == "https://example.com/a"

    api = JSONAPIAdapter(
        "https://example.com/api",
        "Example",
        transport=transport_for(
            '{"items": [{"title": "API item", "url": "https://example.com/api/1"}]}',
            "application/json",
        ),
    )
    assert (await api.collect())[0].title == "API item"

    web = WebPageAdapter(
        "https://example.com/page",
        "Example",
        transport=transport_for(
            "<html><title>Page</title><script>bad()</script>Text</html>",
            "text/html",
        ),
    )
    item = (await web.collect())[0]
    assert item.title == "Page"
    assert "bad" not in item.content