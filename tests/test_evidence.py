from orbit.research.evidence import (
    Analysis,
    EvidenceLedger,
    ExtractedContent,
    SourceEvidence,
    VerifiedFact,
)
from orbit.research.report import render_report


def test_evidence_ledger_preserves_provenance_chain() -> None:
    ledger = EvidenceLedger()
    source = SourceEvidence(
        evidence_id="source-1",
        source_url="https://example.com/report",
        source_name="Example",
        content="The source report states a measurable result.",
    )

    ledger.add_source(source)
    ledger.add_extraction(
        ExtractedContent(
            extraction_id="extract-1",
            evidence_id="source-1",
            text="The report states a measurable result.",
        )
    )
    ledger.add_fact(
        VerifiedFact(
            fact_id="fact-1",
            statement="The report contains a measurable result.",
            evidence_ids=("source-1",),
            status="verified",
        )
    )
    ledger.add_analysis(
        Analysis(
            analysis_id="analysis-1",
            text="The result is relevant to the investigation.",
            evidence_ids=("source-1",),
            fact_ids=("fact-1",),
            provider="test",
        )
    )

    serialized = ledger.to_json()

    assert "https://example.com/report" in serialized
    assert "fact-1" in serialized
    assert "analysis-1" in serialized


def test_evidence_ledger_rejects_unknown_citations() -> None:
    ledger = EvidenceLedger()

    try:
        ledger.add_fact(
            VerifiedFact(
                fact_id="fact-1",
                statement="Unsupported claim",
                evidence_ids=("missing",),
            )
        )
    except KeyError as error:
        assert "missing" in str(error)
    else:
        raise AssertionError("missing evidence citation was accepted")


def test_report_renders_citations_from_ledger() -> None:
    ledger = EvidenceLedger()
    ledger.add_source(
        SourceEvidence(
            evidence_id="source-1",
            source_url="https://example.com/report",
            source_name="Example",
            content="Evidence",
        )
    )
    ledger.add_fact(
        VerifiedFact(
            fact_id="fact-1",
            statement="A verified finding",
            evidence_ids=("source-1",),
            status="verified",
        )
    )

    report = render_report("Research Report", ledger)

    assert "# Research Report" in report
    assert "A verified finding" in report
    assert "[Example](https://example.com/report)" in report