"""ORBIT terminal application."""

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from ..commands.builtin import register_builtin_commands
from ..commands.registry import CommandRegistry
from .screens.session import SessionScreen
from .state import OrbitState
from .theme import CSS
from .widgets.command_palette import CommandItem, CommandPalette
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
        self.command_registry = CommandRegistry()

        register_builtin_commands(
            self.command_registry,
            help_handler=self.show_command_help,
            commands_handler=self.show_command_palette,
            status_handler=self.show_status,
            doctor_handler=self.show_doctor,
            clear_handler=self.clear_session,
            exit_handler=self.exit_orbit,
        )

    def compose(self) -> ComposeResult:
        """Compose the ORBIT application."""

        yield Header()

        yield SessionScreen(
            state=self.state,
            commands=self.command_registry.all(),
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

        if command.startswith("/"):
            self.handle_command(
                session,
                command,
            )

        else:
            self.handle_request(
                session,
                command,
            )

    def handle_command(
        self,
        session: SessionScreen,
        command_text: str,
    ) -> None:
        """Resolve and execute an ORBIT slash command."""

        command_name = command_text.split(maxsplit=1)[0].lower()

        command = self.command_registry.get(
            command_name,
        )

        if command is None:
            session.add_orbit_message(
                f"Unknown command: {command_name}\n"
                "Type /help to see available commands."
            )
            return

        command.handler(session)

    def on_command_item_selected(
        self,
        message: CommandItem.Selected,
    ) -> None:
        """Execute a command selected from the command palette."""

        session = self.query_one(
            "#session",
            SessionScreen,
        )

        command = message.command

        palette = session.query_one(
            "#command-palette",
            CommandPalette,
        )

        palette.hide()

        session.add_user_message(
            command
        )

        self.handle_command(
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

        self.call_after_refresh(
            session.clear_active_activity
        )

    def show_command_help(
        self,
        session: SessionScreen,
    ) -> None:
        """Display ORBIT slash commands."""

        commands = self.command_registry.all()

        lines = [
            "ORBIT Commands",
            "",
        ]

        for command in commands:
            lines.append(
                f"{command.name:<14} {command.description}"
            )

        session.add_orbit_message(
            "\n".join(lines)
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

    def clear_session(
        self,
        session: SessionScreen,
    ) -> None:
        """Clear the current ORBIT session."""

        session.clear_session()

    def exit_orbit(
        self,
        session: SessionScreen,
    ) -> None:
        """Exit ORBIT."""

        self.exit()


def main() -> int:
    """Launch ORBIT."""

    OrbitApp().run()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())