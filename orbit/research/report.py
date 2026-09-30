"""Evidence-backed Markdown report generation."""

from .evidence import EvidenceLedger


def render_report(title: str, ledger: EvidenceLedger) -> str:
    """Render facts and analysis with explicit source citations."""

    lines = [f"# {title}", "", "## Findings", ""]

    if ledger.facts:
        for fact in ledger.facts.values():
            citations = ", ".join(
                _source_link(ledger.sources[evidence_id])
                for evidence_id in fact.evidence_ids
            )
            lines.append(f"- {fact.statement} ({citations})")
    else:
        lines.append("No verified facts recorded.")

    lines.extend(("", "## Analysis", ""))

    if ledger.analyses:
        for analysis in ledger.analyses.values():
            citations = [
                _source_link(ledger.sources[evidence_id])
                for evidence_id in analysis.evidence_ids
            ]
            fact_refs = ", ".join(analysis.fact_ids)
            lines.append(analysis.text)
            if citations:
                lines.append(f"\nSources: {', '.join(citations)}")
            if fact_refs:
                lines.append(f"Facts: {fact_refs}")
            lines.append("")
    else:
        lines.append("No analysis recorded.")

    lines.extend(("## Sources", ""))

    for source in ledger.sources.values():
        lines.append(f"- [{source.source_name}]({source.source_url})")

    return "\n".join(lines).rstrip() + "\n"


def _source_link(source) -> str:
    return f"[{source.source_name}]({source.source_url})"