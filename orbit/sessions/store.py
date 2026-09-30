"""Local, append-only session event storage."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class SessionEvent:
    """One durable event in a research session."""

    event_type: str
    payload: dict[str, Any]
    created_at: str

    @classmethod
    def create(cls, event_type: str, payload: dict[str, Any]) -> "SessionEvent":
        return cls(
            event_type=event_type,
            payload=payload,
            created_at=datetime.now(timezone.utc).isoformat(),
        )


class SessionStore:
    """Persist session events as human-inspectable JSON lines."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def create_session(self) -> str:
        """Create and return a stable session identifier."""

        session_id = uuid4().hex
        self._path(session_id).touch()
        return session_id

    def append(self, session_id: str, event: SessionEvent) -> None:
        """Append one event atomically enough for local single-user use."""

        path = self._path(session_id)

        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(asdict(event), sort_keys=True))
            stream.write("\n")

    def read(self, session_id: str) -> list[SessionEvent]:
        """Read all events for a session in insertion order."""

        path = self._path(session_id)

        if not path.exists():
            return []

        events: list[SessionEvent] = []

        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(SessionEvent(**json.loads(line)))

        return events

    def _path(self, session_id: str) -> Path:
        if not session_id or any(character in session_id for character in "\\/"):
            raise ValueError("Invalid session identifier")

        return self.root / f"{session_id}.jsonl"