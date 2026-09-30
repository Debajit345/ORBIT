"""Command palette for the ORBIT terminal UI."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class CommandPalette(Vertical):
    """Display available ORBIT slash commands."""

    DEFAULT_CSS = """
    CommandPalette {
        height: auto;
        padding: 1 1;
        background: #101419;
        border: round #39434e;
        display: none;
    }

    CommandPalette.visible {
        display: block;
    }

    CommandPalette .palette-title {
        color: #8bd5ff;
        text-style: bold;
        margin-bottom: 1;
    }

    CommandPalette .command-item {
        height: auto;
        padding: 0 1;
        color: #d7dde5;
    }

    CommandPalette .command-item:hover {
        background: #12161b;
        color: #8bd5ff;
    }
    """

    COMMANDS = (
        ("/help", "Show available commands"),
        ("/status", "Show system status"),
        ("/doctor", "Run diagnostics"),
        ("/clear", "Clear the current session"),
        ("/exit", "Exit ORBIT"),
    )

    def compose(self) -> ComposeResult:
        """Build the command palette."""

        yield Static(
            "ORBIT Commands",
            classes="palette-title",
        )

        for command, description in self.COMMANDS:
            yield Static(
                f"{command:<12} {description}",
                classes="command-item",
            )

    def show(self) -> None:
        """Show the command palette."""

        self.add_class("visible")

    def hide(self) -> None:
        """Hide the command palette."""

        self.remove_class("visible")

    def toggle(self) -> None:
        """Toggle command palette visibility."""

        if self.has_class("visible"):
            self.hide()
        else:
            self.show()