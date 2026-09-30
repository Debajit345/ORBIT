from datetime import datetime, timezone

import pytest

from orbit.research import Claim, ResearchPipeline
from orbit.sources import CollectedItem


def item(url: str, content: str, published_at: datetime) -> CollectedItem:
    return CollectedItem(
        title="Research item",
        url=url,
        content=content,
        source_name="Test source",
        published_at=published_at,
    )


def test_pipeline_detects_contradictory_claims_and_preserves_sources() -> None:
    pipeline = ResearchPipeline()
    evidence_ids = pipeline.ingest(
        [
            item(
                "https://example.com/one",
                "Claim one",
                datetime(2026, 1, 2, tzinfo=timezone.utc),
            ),
            item(
                "https://example.com/two",
                "Claim two",
                datetime(2026, 1, 1, tzinfo=timezone.utc),
            ),
        ]
    )

    findings = pipeline.verify(
        [
            Claim("claim-1", "ORBIT", "status", "ready", evidence_ids[0]),
            Claim("claim-2", "ORBIT", "status", "blocked", evidence_ids[1]),
        ]
    )

    assert findings[0].status == "contradicted"
    assert findings[0].values == ("ready", "blocked")
    assert [source.source_url for source in pipeline.timeline()] == [
        "https://example.com/two",
        "https://example.com/one",
    ]
    assert pipeline.ledger.facts["claim-1"].status == "contradicted"


def test_pipeline_rejects_claims_without_provenance() -> None:
    with pytest.raises(KeyError, match="Unknown source evidence"):
        ResearchPipeline().verify(
            [Claim("claim-1", "ORBIT", "status", "ready", "missing")]
        )