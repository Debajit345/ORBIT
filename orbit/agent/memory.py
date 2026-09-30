"""Durable, local agent memory."""

from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass(frozen=True)
class Memory:
    """One remembered fact associated with a scope."""

    scope: str
    key: str
    value: str


class MemoryStore:
    """Persist simple scoped memory as JSON."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def remember(self, scope: str, key: str, value: str) -> None:
        memories = self._read()
        memories[(scope, key)] = Memory(scope, key, value)
        self.path.write_text(
            json.dumps([asdict(memory) for memory in memories.values()], sort_keys=True),
            encoding="utf-8",
        )

    def recall(self, scope: str, key: str) -> Memory | None:
        return self._read().get((scope, key))

    def list_scope(self, scope: str) -> list[Memory]:
        return [memory for memory in self._read().values() if memory.scope == scope]

    def _read(self) -> dict[tuple[str, str], Memory]:
        if not self.path.exists():
            return {}
        records = json.loads(self.path.read_text(encoding="utf-8"))
        return {
            (record["scope"], record["key"]): Memory(**record)
            for record in records
        }