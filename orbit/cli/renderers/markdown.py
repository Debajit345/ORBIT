"""Markdown rendering helpers for the ORBIT terminal UI."""

from rich.markdown import Markdown
from rich.console import Console
from rich.text import Text


def render_markdown(content: str) -> Markdown:
    """Convert Markdown content into a Rich renderable."""

    return Markdown(content)


def render_plain(content: str) -> Text:
    """Convert plain text into a Rich renderable."""

    return Text(content)


def render_to_terminal(content: str) -> None:
    """Render Markdown directly to the terminal."""

    console = Console()
    console.print(Markdown(content))