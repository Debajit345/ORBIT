"""Structured JSON event logging for local diagnostics and audit."""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


class JsonEventLogger:
    """Append structured operational events to a JSONL file."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: str, **fields: Any) -> None:
        payload = {
            "event": event,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **fields,
        }
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(payload, default=str, sort_keys=True))
            stream.write("\n")