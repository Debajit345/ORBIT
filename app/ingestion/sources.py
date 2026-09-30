from dataclasses import dataclass


@dataclass(frozen=True)
class SourceDefinition:
    name: str
    feed_url: str
    category: str
    website_url: str
    source_type: str = "RSS"


SOURCES = [
    SourceDefinition(
        name="NASA",
        feed_url="https://www.nasa.gov/rss/dyn/breaking_news.rss",
        category="SPACE",
        website_url="https://www.nasa.gov/",
    ),
]