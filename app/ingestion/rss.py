import hashlib
from datetime import datetime, timezone

import feedparser
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Article, Source


def generate_fingerprint(title: str, url: str) -> str:
    """
    Generate a stable SHA-256 fingerprint for an article.
    """

    normalized = f"{title.strip().lower()}|{url.strip().lower()}"

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def parse_published_date(entry) -> datetime | None:
    """
    Convert an RSS published date into a timezone-aware datetime.
    """

    if not getattr(entry, "published_parsed", None):
        return None

    return datetime(
        *entry.published_parsed[:6],
        tzinfo=timezone.utc,
    )


def fetch_feed(feed_url: str):
    """
    Fetch and parse an RSS feed.
    """

    feed = feedparser.parse(feed_url)

    if feed.bozo and not feed.entries:
        raise RuntimeError(
            f"Failed to parse RSS feed: {feed_url}"
        )

    return feed


def save_feed_entries(
    db: Session,
    feed,
    source_name: str,
    category: str,
) -> int:
    """
    Save new RSS entries into the database.

    Returns the number of newly inserted articles.
    """

    source = db.scalar(
        select(Source).where(
            Source.name == source_name
        )
    )

    if source is None:
        raise ValueError(
            f"Source '{source_name}' does not exist in the database."
        )

    inserted = 0

    for entry in feed.entries:

        title = getattr(
            entry,
            "title",
            "Untitled",
        ).strip()

        url = getattr(
            entry,
            "link",
            "",
        ).strip()

        if not url:
            continue

        fingerprint = generate_fingerprint(
            title,
            url,
        )

        existing = db.scalar(
            select(Article).where(
                Article.fingerprint == fingerprint
            )
        )

        if existing:
            continue

        summary = getattr(
            entry,
            "summary",
            None,
        )

        author = getattr(
            entry,
            "author",
            None,
        )

        article = Article(
            title=title,
            url=url,
            source_id=source.id,
            category=category,
            author=author,
            published_at=parse_published_date(entry),
            summary=summary,
            content=None,
            fingerprint=fingerprint,
        )

        db.add(article)
        inserted += 1

    

    return inserted