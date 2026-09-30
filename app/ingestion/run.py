from app.database.connection import SessionLocal
from app.ingestion.rss import fetch_feed, save_feed_entries
from app.ingestion.source_health import (
    mark_source_failure,
    mark_source_success,
)
from app.ingestion.source_registry import sync_sources
from app.ingestion.sources import SOURCES


def run_ingestion() -> None:
    db = SessionLocal()

    try:
        registered_sources = sync_sources(
            db=db,
            definitions=SOURCES,
        )

        total_inserted = 0

        for source in registered_sources:
            print(f"Fetching: {source.name}")

            try:
                feed = fetch_feed(
                    source.feed_url
                )

                inserted = save_feed_entries(
                    db=db,
                    feed=feed,
                    source_name=source.name,
                    category=source.category,
                )

                mark_source_success(
                    db=db,
                    source=source,
                )

                db.commit()

                print(
                    f"  New articles: {inserted}"
                )

                total_inserted += inserted

            except Exception as exc:
                db.rollback()

                mark_source_failure(
                    db=db,
                    source=source,
                    error=exc,
                )

                db.commit()

                print(
                    f"  ERROR: {exc}"
                )

        print(
            f"\nTotal new articles: {total_inserted}"
        )

    finally:
        db.close()


if __name__ == "__main__":
    run_ingestion()