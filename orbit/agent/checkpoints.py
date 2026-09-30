"""Checkpoint and rewind support for agent runs."""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Checkpoint:
    """Snapshot of an agent state at a named stage."""

    checkpoint_id: str
    stage: str
    state: dict[str, Any]
    created_at: str


class CheckpointStore:
    """Append and restore checkpoints for resumable work."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, checkpoint_id: str, stage: str, state: dict[str, Any]) -> Checkpoint:
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            stage=stage,
            state=state,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        checkpoints = self.list()
        checkpoints.append(checkpoint)
        self.path.write_text(
            json.dumps([asdict(item) for item in checkpoints], sort_keys=True),
            encoding="utf-8",
        )
        return checkpoint

    def list(self) -> list[Checkpoint]:
        if not self.path.exists():
            return []
        return [
            Checkpoint(**record)
            for record in json.loads(self.path.read_text(encoding="utf-8"))
        ]

    def rewind(self, checkpoint_id: str) -> Checkpoint:
        for checkpoint in reversed(self.list()):
            if checkpoint.checkpoint_id == checkpoint_id:
                return checkpoint
        raise KeyError(f"Unknown checkpoint: {checkpoint_id}")