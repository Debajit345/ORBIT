"""ORBIT terminal application."""

import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from ..agent import ResearchAgent
from ..ai import EchoProvider, ProviderRouter
from app.ingestion.sources import SOURCES
from ..commands.builtin import register_builtin_commands
from ..commands.registry import CommandRegistry
from ..diagnostics import run_diagnostics
from .screens.session import SessionScreen
from .renderers.markdown import render_markdown
from .state import OrbitState
from .theme import CSS
from .widgets.command_palette import CommandItem, CommandPalette
from .widgets.mascot import Mascot, MascotState
from .widgets.prompt import Prompt
from .widgets.transcript import Transcript


class OrbitApp(App):
    """Main ORBIT terminal application."""

    TITLE = "ORBIT"
    SUB_TITLE = "Open Research & Broadcast Intelligence Terminal"
    ENABLE_COMMAND_PALETTE = False
    CSS = CSS

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.state = OrbitState()
        self.command_registry = CommandRegistry()
        self.agent = ResearchAgent(
            ProviderRouter([EchoProvider()])
        )

        register_builtin_commands(
            self.command_registry,
            help_handler=self.show_command_help,
            commands_handler=self.show_command_palette,
            sources_handler=self.show_sources,
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
            command_registry=self.command_registry,
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
        """Schedule a natural-language request for the research agent."""

        self.run_worker(
            self._run_request(session, request),
            exclusive=True,
            group="research",
        )

    async def _run_request(
        self,
        session: SessionScreen,
        request: str,
    ) -> None:
        """Execute a request and stream its major stages into the session."""

        session.add_activity(
            "Processing request",
            "active",
        )
        mascot = session.query_one("#mascot", Mascot)
        mascot.set_state(MascotState.WORKING)

        try:
            transcript = session.query_one("#transcript", Transcript)
            response_widget = transcript.add_orbit_stream("")
            response_text = ""

            async for chunk in self.agent.stream(request):
                response_text += chunk.text
                response_widget.update(render_markdown(response_text))
                await asyncio.sleep(0)

            session.add_activity("Response streamed", "success")
            self.state.add_message("orbit", response_text)
            mascot.set_state(MascotState.SUCCESS)
            self.call_after_refresh(mascot.set_state, MascotState.WAITING)
        except Exception as error:
            session.add_activity(
                "Research request failed",
                "error",
            )
            session.add_orbit_message(
                f"Research request failed: {error}"
            )
            mascot.set_state(MascotState.WARNING)
            self.call_after_refresh(mascot.set_state, MascotState.WAITING)
        finally:
            session.clear_active_activity()


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

    def show_sources(
        self,
        session: SessionScreen,
    ) -> None:
        """Display configured source definitions and provenance endpoints."""

        lines = ["Configured Sources", ""]

        for source in SOURCES:
            lines.extend(
                (
                    f"{source.name} ({source.source_type})",
                    f"  Category: {source.category}",
                    f"  Feed: {source.feed_url}",
                    f"  Website: {source.website_url}",
                    "",
                )
            )

        if not SOURCES:
            lines.append("No sources configured.")

        session.add_orbit_message("\n".join(lines).rstrip())

    def show_doctor(
        self,
        session: SessionScreen,
    ) -> None:
        """Display local runtime and hardware diagnostics."""

        lines = ["ORBIT Diagnostics", ""]

        for result in run_diagnostics():
            lines.append(
                f"{result.component:<12} {result.status:<12} {result.detail}"
            )

        session.add_orbit_message("\n".join(lines))

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