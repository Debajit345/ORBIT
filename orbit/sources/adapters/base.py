"""Shared source adapter contracts."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol


@dataclass(frozen=True)
class CollectedItem:
    """Normalized content collected from a configured source."""

    title: str
    url: str
    content: str
    source_name: str
    published_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class SourceAdapter(Protocol):
    """Async contract shared by source adapters."""

    async def collect(self) -> list[CollectedItem]:
        """Collect normalized items from the source."""
