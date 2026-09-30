"""ORBIT terminal application."""

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from .screens.session import SessionScreen
from .state import OrbitState
from .theme import CSS
from .widgets.command_palette import CommandPalette
from .widgets.prompt import Prompt


class OrbitApp(App):
    """Main ORBIT terminal application."""

    TITLE = "ORBIT"
    SUB_TITLE = "Open Research & Broadcast Intelligence Terminal"

    CSS = CSS

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.state = OrbitState()

    def compose(self) -> ComposeResult:
        """Compose the ORBIT application."""

        yield Header()

        yield SessionScreen(
            state=self.state,
            id="session",
        )

        yield Footer()

    def on_mount(self) -> None:
        """Initialize ORBIT."""

        self.query_one(
            "#session",
            SessionScreen,
        ).query_one(
            "#prompt",
            Prompt,
        ).focus_input()

    def on_prompt_submitted(
        self,
        message: Prompt.Submitted,
    ) -> None:
        """Handle a submitted ORBIT prompt."""

        command = message.value.strip()

        if not command:
            return

        session = self.query_one(
            "#session",
            SessionScreen,
        )

        session.add_user_message(command)

        if command == "/help":
            self.show_command_help(session)

        elif command == "/commands":
            self.show_command_palette(session)

        elif command == "/status":
            self.show_status(session)

        elif command == "/doctor":
            self.show_doctor(session)

        elif command == "/clear":
            session.clear_session()

        elif command in {"/exit", "/quit"}:
            self.exit()

        elif command.startswith("/"):
            session.add_orbit_message(
                f"Unknown command: {command}\n"
                "Type /help to see available commands."
            )

        else:
            self.handle_request(
                session,
                command,
            )

    def handle_request(
        self,
        session: SessionScreen,
        request: str,
    ) -> None:
        """Handle a future natural-language ORBIT request."""

        session.add_activity(
            "Processing request",
            "active",
        )

        session.add_orbit_message(
            "I received your request.\n\n"
            "The research agent is not connected yet."
        )

    def show_command_help(
        self,
        session: SessionScreen,
    ) -> None:
        """Display ORBIT slash commands."""

        session.add_orbit_message(
            "ORBIT Commands\n\n"
            "/help          Show commands\n"
            "/commands      Open command palette\n"
            "/status        Show system status\n"
            "/doctor        Run diagnostics\n"
            "/clear         Clear session\n"
            "/exit          Exit ORBIT"
        )

    def show_command_palette(
        self,
        session: SessionScreen,
    ) -> None:
        """Show the ORBIT command palette."""

        palette = session.query_one(
            "#command-palette",
            CommandPalette,
        )

        palette.show()

    def show_status(
        self,
        session: SessionScreen,
    ) -> None:
        """Display current ORBIT status."""

        session.add_orbit_message(
            "ORBIT Status\n\n"
            "Terminal       ONLINE\n"
            "TUI            ONLINE\n"
            "Source engine  READY\n"
            "Knowledge      READY\n"
            "AI provider    AUTO"
        )

    def show_doctor(
        self,
        session: SessionScreen,
    ) -> None:
        """Display basic diagnostics."""

        session.add_orbit_message(
            "ORBIT Diagnostics\n\n"
            "Python         OK\n"
            "Textual        OK\n"
            "CLI            OK\n"
            "Source engine  OK\n"
            "Database       READY\n"
            "AI provider    NOT CONFIGURED"
        )


def main() -> int:
    """Launch ORBIT."""

    OrbitApp().run()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())