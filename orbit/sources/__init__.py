"""Normalized source collection adapters for ORBIT."""

from .adapters import (
    CollectedItem,
    JSONAPIAdapter,
    RSSAdapter,
    SitemapAdapter,
    WebPageAdapter,
)

__all__ = [
    "CollectedItem",
    "JSONAPIAdapter",
    "RSSAdapter",
    "SitemapAdapter",
    "WebPageAdapter",
]
