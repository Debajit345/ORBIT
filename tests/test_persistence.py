from pathlib import Path

from orbit.knowledge import MarkdownNote, MarkdownVault
from orbit.sessions import SessionEvent, SessionStore


def test_session_store_round_trips_events(tmp_path: Path) -> None:
    store = SessionStore(tmp_path / "sessions")
    session_id = store.create_session()
    event = SessionEvent.create("message", {"role": "user", "content": "hello"})

    store.append(session_id, event)

    assert store.read(session_id) == [event]


def test_markdown_vault_round_trips_frontmatter(tmp_path: Path) -> None:
    vault = MarkdownVault(tmp_path / "vault")
    note = MarkdownNote(
        title="Research Brief",
        content="# Findings\n\nEvidence-backed result.",
        metadata={"tags": "research,orbit"},
    )

    path = vault.save(note)
    loaded = vault.read(path.name)

    assert loaded == note