from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.models import Source


def mark_source_success(
    db: Session,
    source: Source,
) -> None:
    """
    Record a successful source fetch.
    """

    now = datetime.now(timezone.utc)

    source.last_checked_at = now
    source.last_success_at = now
    source.last_error = None
    source.consecutive_failures = 0


def mark_source_failure(
    db: Session,
    source: Source,
    error: Exception,
) -> None:
    """
    Record a failed source fetch.
    """

    now = datetime.now(timezone.utc)

    source.last_checked_at = now
    source.last_error = str(error)
    source.consecutive_failures += 1