from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Source
from app.ingestion.sources import SourceDefinition


def register_source(
    db: Session,
    definition: SourceDefinition,
) -> Source:
    """
    Register a source in the database if it does not already exist.

    If the source already exists, update its configuration.

    Returns the database Source object.
    """

    source = db.scalar(
        select(Source).where(
            Source.name == definition.name
        )
    )

    if source is None:
        source = Source(
            name=definition.name,
            feed_url=definition.feed_url,
            category=definition.category,
            source_type=definition.source_type,
            website_url=definition.website_url,
            active=True,
        )

        db.add(source)

    else:
        source.feed_url = definition.feed_url
        source.category = definition.category
        source.source_type = definition.source_type
        source.website_url = definition.website_url
        source.active = True

    db.flush()
    db.refresh(source)

    return source


def sync_sources(
    db: Session,
    definitions: list[SourceDefinition],
) -> list[Source]:
    """
    Synchronize configured source definitions with the database.
    """

    registered_sources = []

    for definition in definitions:
        source = register_source(
            db=db,
            definition=definition,
        )

        registered_sources.append(source)

    return registered_sources