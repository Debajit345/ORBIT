"""ORBIT terminal interface."""

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Input, RichLog, Static


class OrbitApp(App):
    """Main ORBIT terminal application."""

    TITLE = "ORBIT"
    SUB_TITLE = "Open Research & Broadcast Intelligence Terminal"

    CSS = """
    Screen {
        background: #0b0d10;
        color: #d7dde5;
    }

    Header {
        background: #101419;
        color: #8bd5ff;
        height: 3;
    }

    Footer {
        background: #101419;
    }

    #workspace {
        height: 1fr;
        padding: 1 2;
    }

    #conversation {
        height: 1fr;
        background: #0b0d10;
        border: none;
        padding: 1 2;
    }

    #welcome {
        height: auto;
        padding: 1 0 2 0;
    }

    #welcome-title {
        color: #ffffff;
        text-style: bold;
    }

    #welcome-subtitle {
        color: #7d8792;
    }

    #prompt-container {
        height: auto;
        padding: 1 0 0 0;
    }

    #prompt {
        height: 3;
        border: round #39434e;
        background: #12161b;
        color: #f1f5f9;
        padding: 0 1;
    }

    #prompt:focus {
        border: round #6aaed6;
    }

    #hint {
        height: 2;
        color: #59636f;
        padding: 0 1;
    }

    #status {
        height: 2;
        color: #697581;
        padding: 0 1;
    }

    .user-message {
        margin: 1 0;
        color: #e6edf3;
    }

    .orbit-message {
        margin: 1 0 2 0;
        color: #aeb8c4;
    }

    .activity {
        margin: 1 0;
        color: #7d8792;
    }

    .command {
        margin: 1 0;
        color: #8bd5ff;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical(id="workspace"):

            with Vertical(id="conversation"):
                yield Static(
                    "ORBIT",
                    id="welcome-title",
                )

                yield Static(
                    "Open Research & Broadcast Intelligence Terminal\n\n"
                    "Welcome back.\n"
                    "Type /help for available commands.",
                    id="welcome-subtitle",
                )

                yield Static(
                    "● System ready",
                    classes="activity",
                )

            with Vertical(id="prompt-container"):
                yield Input(
                    placeholder="Ask ORBIT anything...",
                    id="prompt",
                )

                yield Static(
                    "Enter send   •   / commands   •   ↑↓ history",
                    id="hint",
                )

            yield Static(
                "● READY    │    AI: AUTO    │    SOURCES: 1    │    SESSION: NEW",
                id="status",
            )

        yield Footer()

    def on_mount(self) -> None:
        """Focus the prompt when ORBIT starts."""

        self.query_one("#prompt", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input."""

        command = event.value.strip()
        event.input.value = ""

        if not command:
            return

        conversation = self.query_one("#conversation", Vertical)

        conversation.mount(
            Static(
                f"You\n  {command}",
                classes="user-message",
            )
        )

        if command == "/help":
            self.show_command_help(conversation)

        elif command == "/status":
            self.show_status(conversation)

        elif command == "/doctor":
            self.show_doctor(conversation)

        elif command == "/clear":
            self.clear_conversation()

        elif command in {"/exit", "/quit"}:
            self.exit()

        elif command.startswith("/"):
            conversation.mount(
                Static(
                    f"Unknown command: {command}\n"
                    "Type /help to see available commands.",
                    classes="command",
                )
            )

        else:
            self.handle_request(conversation, command)

        conversation.scroll_end()

    def handle_request(
        self,
        conversation: Vertical,
        request: str,
    ) -> None:
        """Handle a future natural-language ORBIT request."""

        conversation.mount(
            Static(
                "ORBIT\n"
                "  I received your request.\n\n"
                "  The research agent is not connected yet.",
                classes="orbit-message",
            )
        )

    def show_command_help(self, conversation: Vertical) -> None:
        """Display ORBIT slash commands."""

        conversation.mount(
            Static(
                "ORBIT Commands\n\n"
                "  /help          Show commands\n"
                "  /status        Show system status\n"
                "  /doctor        Run diagnostics\n"
                "  /clear         Clear session\n"
                "  /exit          Exit ORBIT",
                classes="command",
            )
        )

    def show_status(self, conversation: Vertical) -> None:
        """Display current ORBIT status."""

        conversation.mount(
            Static(
                "ORBIT Status\n\n"
                "  Terminal       ONLINE\n"
                "  TUI            ONLINE\n"
                "  Source engine  READY\n"
                "  Knowledge      READY\n"
                "  AI provider    AUTO\n",
                classes="orbit-message",
            )
        )

    def show_doctor(self, conversation: Vertical) -> None:
        """Display basic diagnostics."""

        conversation.mount(
            Static(
                "ORBIT Diagnostics\n\n"
                "  Python         OK\n"
                "  Textual        OK\n"
                "  CLI            OK\n"
                "  Source engine  OK\n"
                "  Database       READY\n"
                "  AI provider    NOT CONFIGURED",
                classes="orbit-message",
            )
        )

    def clear_conversation(self) -> None:
        """Clear the conversation and restore the welcome view."""

        conversation = self.query_one("#conversation", Vertical)

        children = list(conversation.children)

        for child in children:
            child.remove()

        conversation.mount(
            Static(
                "ORBIT",
                id="welcome-title",
            )
        )

        conversation.mount(
            Static(
                "Open Research & Broadcast Intelligence Terminal\n\n"
                "Session cleared.\n"
                "Type /help for available commands.",
                id="welcome-subtitle",
            )
        )


def main() -> int:
    """Launch ORBIT."""

    OrbitApp().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())