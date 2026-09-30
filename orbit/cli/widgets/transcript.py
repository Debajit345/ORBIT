"""Conversation transcript widget for ORBIT."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class Transcript(Vertical):
    """Scrollable conversation transcript."""

    DEFAULT_CSS = """
    Transcript {
        height: 1fr;
        overflow-y: auto;
        padding: 0 1;
    }

    Transcript .transcript-user {
        margin: 1 0;
        color: #d7dde5;
    }

    Transcript .transcript-orbit {
        margin: 1 0 2 0;
        color: #aeb8c4;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the initial transcript."""

        yield Static(
            "ORBIT",
            classes="transcript-orbit",
        )

        yield Static(
            "Open Research & Broadcast Intelligence Terminal\n\n"
            "Welcome back.\n"
            "Type /help for available commands.",
            classes="transcript-orbit",
        )

    def add_user_message(self, content: str) -> None:
        """Add a user message to the transcript."""

        self.mount(
            Static(
                f"You\n  {content}",
                classes="transcript-user",
            )
        )

        self.scroll_end()

    def add_orbit_message(self, content: str) -> None:
        """Add an ORBIT response to the transcript."""

        self.mount(
            Static(
                f"ORBIT\n  {content}",
                classes="transcript-orbit",
            )
        )

        self.scroll_end()

    def add_system_message(self, content: str) -> None:
        """Add a system message to the transcript."""

        self.mount(
            Static(
                content,
                classes="transcript-orbit",
            )
        )

        self.scroll_end()

    def clear(self) -> None:
        """Remove all transcript messages."""

        for child in list(self.children):
            child.remove()

        self.mount(
            Static(
                "ORBIT",
                classes="transcript-orbit",
            )
        )

        self.mount(
            Static(
                "Open Research & Broadcast Intelligence Terminal\n\n"
                "Session cleared.\n"
                "Type /help for available commands.",
                classes="transcript-orbit",
            )
        )