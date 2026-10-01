"""Conversation transcript widget for the ORBIT terminal UI."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.events import Click
from textual.widgets import Static

from ..renderers.markdown import render_markdown


class Transcript(Vertical):
    """Scrollable conversation transcript."""

    DEFAULT_CSS = """
    Transcript {
        height: 1fr;
        overflow-y: auto;
        padding: 1 1;
    }

    Transcript .welcome {
        height: auto;
        margin: 1 0 3 0;
    }

    Transcript .welcome-title {
        color: #ff9f43;
        text-style: bold;
        margin-bottom: 1;
    }

    Transcript .welcome-body {
        color: #c8c8c8;
    }

    Transcript .message {
        height: auto;
        margin: 1 0 3 0;
        padding: 0 0 1 0;
    }

    Transcript .message-user {
        border-left: tall #303030;
    }

    Transcript .message-orbit {
        border-left: tall #d97732;
    }

    Transcript .message-label {
        height: auto;
        padding: 0 0 0 2;
        text-style: bold;
    }

    Transcript .message-user .message-label {
        color: #858585;
    }

    Transcript .message-orbit .message-label {
        color: #ff9f43;
    }

    Transcript .message-body {
        height: auto;
        padding: 0 2;
        color: #d7d7d7;
    }

    Transcript .message-user .message-body {
        color: #e0e0e0;
    }

    Transcript .message-orbit .message-body {
        color: #c8c8c8;
    }

    Transcript .system-message {
        height: auto;
        margin: 1 0 2 0;
        padding: 0 0 0 2;
        color: #626262;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the initial transcript."""

        with Vertical(classes="welcome"):
            yield Static(
                "ORBIT",
                classes="welcome-title",
            )

            yield Static(
                "Open Research & Broadcast Intelligence Terminal\n\n"
                "Welcome back.\n"
                "Type /help for available commands.",
                classes="welcome-body",
            )

    def on_click(self, event: Click) -> None:
        """Close the command palette when the workspace is clicked."""

        session = self.screen.query_one("#session")
        palette = session.query_one("#command-palette")

        if palette.has_class("visible"):
            palette.hide()
            session.query_one("#prompt").focus_input()

    def add_user_message(
        self,
        content: str,
    ) -> None:
        """Add a user message."""

        self.mount(
            Vertical(
                Static(
                    "You",
                    classes="message-label",
                ),
                Static(
                    content,
                    classes="message-body",
                ),
                classes="message message-user",
            )
        )

        self.scroll_end()

    def add_orbit_message(
        self,
        content: str,
    ) -> None:
        """Add an ORBIT response."""

        self.mount(
            Vertical(
                Static(
                    "ORBIT",
                    classes="message-label",
                ),
                Static(
                    render_markdown(content),
                    classes="message-body",
                ),
                classes="message message-orbit",
            )
        )

        self.scroll_end()

    def add_orbit_stream(
        self,
        content: str,
    ) -> Static:
        """Mount an ORBIT response body that can update incrementally."""

        body = Static(
            render_markdown(content),
            classes="message-body",
        )

        message = Vertical(
            Static(
                "ORBIT",
                classes="message-label",
            ),
            body,
            classes="message message-orbit",
        )

        self.mount(message)
        self.scroll_end()

        return body

    def add_system_message(
        self,
        content: str,
    ) -> None:
        """Add a system message."""

        self.mount(
            Static(
                content,
                classes="system-message",
            )
        )

        self.scroll_end()

    def clear(self) -> None:
        """Clear the transcript."""

        for child in list(self.children):
            child.remove()

        self.mount(
            Vertical(
                Static(
                    "ORBIT",
                    classes="welcome-title",
                ),
                Static(
                    "Session cleared.\n"
                    "Type /help for available commands.",
                    classes="welcome-body",
                ),
                classes="welcome",
            )
        )