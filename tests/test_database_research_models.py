from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.models import (
    Base,
    EvidenceRecord,
    ResearchSession,
    SessionEvent,
)


def test_research_session_event_and_evidence_models_round_trip() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        session = ResearchSession(id="session-1", name="Investigation")
        session.events.append(
            SessionEvent(
                event_type="request",
                payload={"text": "research"},
            )
        )
        session.evidence.append(
            EvidenceRecord(
                id="evidence-1",
                source_url="https://example.com",
                source_name="Example",
                content="Evidence",
                metadata_json={"kind": "article"},
            )
        )
        db.add(session)
        db.commit()

        loaded = db.scalar(
            select(ResearchSession).where(ResearchSession.id == "session-1")
        )

        assert loaded is not None
        assert loaded.events[0].payload["text"] == "research"
        assert loaded.evidence[0].source_url == "https://example.com"