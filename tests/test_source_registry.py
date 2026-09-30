from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.database.models import Source
from app.ingestion.source_registry import (
    register_source,
    sync_sources,
)
from app.ingestion.sources import SourceDefinition


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


def test_register_source_creates_source():
    Session = create_test_database()
    db = Session()

    definition = SourceDefinition(
        name="Test Source",
        feed_url="https://example.com/feed.xml",
        category="TEST",
        website_url="https://example.com/",
    )

    source = register_source(
        db=db,
        definition=definition,
    )

    db.commit()

    sources = db.scalars(
        select(Source)
    ).all()

    assert source.name == "Test Source"
    assert len(sources) == 1
    assert sources[0].feed_url == "https://example.com/feed.xml"

    db.close()


def test_register_source_does_not_duplicate():
    Session = create_test_database()
    db = Session()

    definition = SourceDefinition(
        name="Test Source",
        feed_url="https://example.com/feed.xml",
        category="TEST",
        website_url="https://example.com/",
    )

    register_source(
        db=db,
        definition=definition,
    )

    register_source(
        db=db,
        definition=definition,
    )

    db.commit()

    sources = db.scalars(
        select(Source)
    ).all()

    assert len(sources) == 1

    db.close()


def test_register_source_updates_existing_source():
    Session = create_test_database()
    db = Session()

    original = SourceDefinition(
        name="Test Source",
        feed_url="https://example.com/old-feed.xml",
        category="TEST",
        website_url="https://example.com/",
    )

    updated = SourceDefinition(
        name="Test Source",
        feed_url="https://example.com/new-feed.xml",
        category="SPACE",
        website_url="https://example.com/new/",
    )

    register_source(
        db=db,
        definition=original,
    )

    register_source(
        db=db,
        definition=updated,
    )

    db.commit()

    sources = db.scalars(
        select(Source)
    ).all()

    assert len(sources) == 1
    assert sources[0].feed_url == "https://example.com/new-feed.xml"
    assert sources[0].category == "SPACE"
    assert sources[0].website_url == "https://example.com/new/"

    db.close()
    
def test_sync_sources_registers_multiple_sources():
    Session = create_test_database()
    db = Session()

    definitions = [
        SourceDefinition(
            name="Source A",
            feed_url="https://example.com/a.xml",
            category="SPACE",
            website_url="https://example.com/a/",
        ),
        SourceDefinition(
            name="Source B",
            feed_url="https://example.com/b.xml",
            category="TECH",
            website_url="https://example.com/b/",
        ),
        SourceDefinition(
            name="Source C",
            feed_url="https://example.com/c.xml",
            category="SPACE",
            website_url="https://example.com/c/",
        ),
    ]

    sources = sync_sources(
        db=db,
        definitions=definitions,
    )

    db.commit()

    assert len(sources) == 3

    database_sources = db.scalars(
        select(Source)
    ).all()

    assert len(database_sources) == 3

    db.close()