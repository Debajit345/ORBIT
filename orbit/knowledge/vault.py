"""Obsidian-compatible Markdown note storage."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MarkdownNote:
    """A Markdown note with simple YAML frontmatter."""

    title: str
    content: str
    metadata: dict[str, Any]


class MarkdownVault:
    """Write and read notes without requiring Obsidian."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, note: MarkdownNote, filename: str | None = None) -> Path:
        """Save a note and return its path."""

        name = filename or self._slug(note.title)
        if not name.endswith(".md"):
            name = f"{name}.md"

        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._render(note), encoding="utf-8")
        return path

    def read(self, filename: str) -> MarkdownNote:
        """Read a note from the vault."""

        path = self.root / filename
        text = path.read_text(encoding="utf-8")

        if not text.startswith("---\n"):
            return MarkdownNote(path.stem, text, {})

        _, frontmatter, content = text.split("---\n", 2)
        metadata: dict[str, Any] = {}

        for line in frontmatter.splitlines():
            if ":" in line:
                key, value = line.split(":", maxsplit=1)
                metadata[key.strip()] = value.strip()

        return MarkdownNote(
            title=str(metadata.pop("title", path.stem)),
            content=content.strip("\n"),
            metadata=metadata,
        )

    @staticmethod
    def _slug(title: str) -> str:
        return "-".join(title.lower().split())

    @staticmethod
    def _render(note: MarkdownNote) -> str:
        metadata = {"title": note.title, **note.metadata}
        frontmatter = "\n".join(
            f"{key}: {value}" for key, value in metadata.items()
        )
        return f"---\n{frontmatter}\n---\n\n{note.content.rstrip()}\n"