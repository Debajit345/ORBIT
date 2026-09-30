from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.database.models import Source
from app.ingestion.source_health import (
    mark_source_failure,
    mark_source_success,
)


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


def create_test_source(db):
    source = Source(
        name="Test Source",
        feed_url="https://example.com/feed.xml",
        category="TEST",
        source_type="RSS",
        website_url="https://example.com/",
        active=True,
        consecutive_failures=0,
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


def test_mark_source_success():
    Session = create_test_database()
    db = Session()

    source = create_test_source(db)

    source.consecutive_failures = 3
    source.last_error = "Previous failure"

    mark_source_success(
        db=db,
        source=source,
    )

    assert source.consecutive_failures == 0
    assert source.last_error is None
    assert source.last_checked_at is not None
    assert source.last_success_at is not None

    db.close()


def test_mark_source_failure():
    Session = create_test_database()
    db = Session()

    source = create_test_source(db)

    error = RuntimeError(
        "Test feed failure"
    )

    mark_source_failure(
        db=db,
        source=source,
        error=error,
    )

    assert source.consecutive_failures == 1
    assert source.last_error == "Test feed failure"
    assert source.last_checked_at is not None
    assert source.last_success_at is None

    db.close()