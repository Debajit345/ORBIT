"""Source adapters with a common normalized output."""

from .base import CollectedItem
from .json_api import JSONAPIAdapter
from .rss import RSSAdapter
from .sitemap import SitemapAdapter
from .web import WebPageAdapter

__all__ = [
    "CollectedItem",
    "JSONAPIAdapter",
    "RSSAdapter",
    "SitemapAdapter",
    "WebPageAdapter",
]
