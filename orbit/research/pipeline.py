"""Deterministic research comparison and verification primitives."""

from dataclasses import dataclass
from datetime import datetime
import hashlib
from collections import defaultdict

from ..sources import CollectedItem
from .evidence import EvidenceLedger, SourceEvidence, VerifiedFact


@dataclass(frozen=True)
class Claim:
    """A structured claim extracted from one source."""

    claim_id: str
    subject: str
    predicate: str
    value: str
    evidence_id: str


@dataclass(frozen=True)
class VerificationFinding:
    """Comparison result for claims sharing a subject and predicate."""

    subject: str
    predicate: str
    status: str
    values: tuple[str, ...]
    claim_ids: tuple[str, ...]


class ResearchPipeline:
    """Build an evidence ledger and verify structured claims."""

    def __init__(self) -> None:
        self.ledger = EvidenceLedger()

    def ingest(self, items: list[CollectedItem]) -> tuple[str, ...]:
        """Record collected source items and return evidence identifiers."""

        evidence_ids: list[str] = []

        for item in items:
            evidence_id = _evidence_id(item)
            self.ledger.add_source(
                SourceEvidence(
                    evidence_id=evidence_id,
                    source_url=item.url,
                    source_name=item.source_name,
                    content=item.content,
                    published_at=item.published_at,
                    fingerprint=evidence_id,
                    metadata=item.metadata,
                )
            )
            evidence_ids.append(evidence_id)

        return tuple(evidence_ids)

    def verify(self, claims: list[Claim]) -> list[VerificationFinding]:
        """Compare claims and record verified or contradicted facts."""

        groups: dict[tuple[str, str], list[Claim]] = defaultdict(list)

        for claim in claims:
            if claim.evidence_id not in self.ledger.sources:
                raise KeyError(f"Unknown source evidence: {claim.evidence_id}")
            groups[(claim.subject, claim.predicate)].append(claim)

        findings: list[VerificationFinding] = []

        for (subject, predicate), grouped_claims in groups.items():
            values = tuple(dict.fromkeys(claim.value for claim in grouped_claims))
            status = "verified" if len(values) == 1 else "contradicted"
            findings.append(
                VerificationFinding(
                    subject=subject,
                    predicate=predicate,
                    status=status,
                    values=values,
                    claim_ids=tuple(claim.claim_id for claim in grouped_claims),
                )
            )

            for claim in grouped_claims:
                self.ledger.add_fact(
                    VerifiedFact(
                        fact_id=claim.claim_id,
                        statement=(
                            f"{claim.subject} {claim.predicate} {claim.value}"
                        ),
                        evidence_ids=(claim.evidence_id,),
                        status=status,
                    )
                )

        return findings

    def timeline(self) -> list[SourceEvidence]:
        """Return source evidence ordered by publication/retrieval time."""

        return sorted(
            self.ledger.sources.values(),
            key=lambda source: source.published_at or source.retrieved_at,
        )


def _evidence_id(item: CollectedItem) -> str:
    digest = hashlib.sha256(
        f"{item.source_name}|{item.url}|{item.content}".encode("utf-8")
    ).hexdigest()
    return f"evidence-{digest[:16]}"