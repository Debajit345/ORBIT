"""Traceable evidence contracts for research and synthesis."""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from typing import Any, Literal


EvidenceStatus = Literal["unverified", "verified", "contradicted"]


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class SourceEvidence:
    """Original material collected from a source."""

    evidence_id: str
    source_url: str
    source_name: str
    content: str
    retrieved_at: datetime = field(default_factory=_now)
    published_at: datetime | None = None
    fingerprint: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExtractedContent:
    """Content extracted from source evidence without interpretation."""

    extraction_id: str
    evidence_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VerifiedFact:
    """A factual claim with explicit supporting evidence references."""

    fact_id: str
    statement: str
    evidence_ids: tuple[str, ...]
    status: EvidenceStatus = "unverified"


@dataclass(frozen=True)
class Analysis:
    """Model-generated analysis that remains linked to evidence or facts."""

    analysis_id: str
    text: str
    evidence_ids: tuple[str, ...] = ()
    fact_ids: tuple[str, ...] = ()
    provider: str = "unknown"
    generated_at: datetime = field(default_factory=_now)


class EvidenceLedger:
    """In-memory provenance ledger for one research operation."""

    def __init__(self) -> None:
        self.sources: dict[str, SourceEvidence] = {}
        self.extractions: dict[str, ExtractedContent] = {}
        self.facts: dict[str, VerifiedFact] = {}
        self.analyses: dict[str, Analysis] = {}

    def add_source(self, evidence: SourceEvidence) -> None:
        """Record original source material."""

        self.sources[evidence.evidence_id] = evidence

    def add_extraction(self, extraction: ExtractedContent) -> None:
        """Record extracted content and require its source to exist."""

        self._require_source(extraction.evidence_id)
        self.extractions[extraction.extraction_id] = extraction

    def add_fact(self, fact: VerifiedFact) -> None:
        """Record a fact and require every citation to resolve."""

        self._require_sources(fact.evidence_ids)
        self.facts[fact.fact_id] = fact

    def add_analysis(self, analysis: Analysis) -> None:
        """Record analysis while preserving all provenance references."""

        self._require_sources(analysis.evidence_ids)

        for fact_id in analysis.fact_ids:
            if fact_id not in self.facts:
                raise KeyError(f"Unknown fact reference: {fact_id}")

        self.analyses[analysis.analysis_id] = analysis

    def to_json(self) -> str:
        """Serialize the ledger for checkpoints and audit events."""

        payload = {
            "sources": self.sources,
            "extractions": self.extractions,
            "facts": self.facts,
            "analyses": self.analyses,
        }

        return json.dumps(payload, default=_serialize_value, sort_keys=True)

    def _require_source(self, evidence_id: str) -> None:
        if evidence_id not in self.sources:
            raise KeyError(f"Unknown source evidence: {evidence_id}")

    def _require_sources(self, evidence_ids: tuple[str, ...]) -> None:
        for evidence_id in evidence_ids:
            self._require_source(evidence_id)


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()

    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)

    raise TypeError(f"Cannot serialize {type(value).__name__}")