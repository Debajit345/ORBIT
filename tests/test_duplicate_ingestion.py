from types import SimpleNamespace

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.database.models import Article, Source
from app.ingestion.rss import save_feed_entries


def create_test_database():
    engine = create_engine(
        "sqlite:///:memory:",
    )

    Base.metadata.create_all(
        bind=engine,
    )

    Session = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    return Session


def test_duplicate_article_is_not_inserted():
    Session = create_test_database()

    db = Session()

    source = Source(
        name="Test Source",
        feed_url="https://example.com/feed.xml",
        category="TEST",
        source_type="RSS",
        website_url="https://example.com/",
        active=True,
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    entry = SimpleNamespace(
        title="Test Article",
        link="https://example.com/article-1",
        summary="Test summary",
        author="Test Author",
        published_parsed=None,
    )

    feed = SimpleNamespace(
        entries=[entry],
    )

    first_inserted = save_feed_entries(
        db=db,
        feed=feed,
        source_name="Test Source",
        category="TEST",
    )

    db.commit()

    second_inserted = save_feed_entries(
        db=db,
        feed=feed,
        source_name="Test Source",
        category="TEST",
    )

    db.commit()

    articles = db.scalars(
        select(Article)
    ).all()

    assert first_inserted == 1
    assert second_inserted == 0
    assert len(articles) == 1

    db.close()