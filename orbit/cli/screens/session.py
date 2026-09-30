"""Main ORBIT research session screen."""

from collections.abc import Sequence

from textual.app import ComposeResult
from textual.containers import Vertical

from ...commands.registry import Command
from ..state import OrbitState
from ..widgets.activity import Activity
from ..widgets.command_palette import CommandPalette
from ..widgets.prompt import Prompt
from ..widgets.status_bar import StatusBar
from ..widgets.transcript import Transcript


class SessionScreen(Vertical):
    """Main interactive ORBIT session."""

    def __init__(
        self,
        state: OrbitState | None = None,
        commands: Sequence[Command] = (),
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.state = state or OrbitState()
        self.commands = commands

    def compose(self) -> ComposeResult:
        """Compose the ORBIT session interface."""

        yield Transcript(id="transcript")

        yield Activity(id="activity")

        yield CommandPalette(
            self.commands,
            id="command-palette",
        )

        yield Prompt(id="prompt")

        yield StatusBar(id="status-bar")

    def on_mount(self) -> None:
        """Initialize the session screen."""

        status_bar = self.query_one(
            "#status-bar",
            StatusBar,
        )

        status_bar.update_from_state(
            self.state
        )

        prompt = self.query_one(
            "#prompt",
            Prompt,
        )

        prompt.focus_input()

    def add_user_message(
        self,
        content: str,
    ) -> None:
        """Add a user message to the transcript."""

        transcript = self.query_one(
            "#transcript",
            Transcript,
        )

        transcript.add_user_message(
            content
        )

        self.state.add_message(
            "user",
            content,
        )

    def add_orbit_message(
        self,
        content: str,
    ) -> None:
        """Add an ORBIT response."""

        transcript = self.query_one(
            "#transcript",
            Transcript,
        )

        transcript.add_orbit_message(
            content
        )

        self.state.add_message(
            "orbit",
            content,
        )

    def add_activity(
        self,
        text: str,
        level: str = "active",
    ) -> None:
        """Add an activity event."""

        activity = self.query_one(
            "#activity",
            Activity,
        )

        activity.add(
            text,
            level,
        )

        self.state.add_activity(
            text,
            level,
        )

    def clear_active_activity(self) -> None:
        """Remove currently active activities."""

        activity = self.query_one(
            "#activity",
            Activity,
        )

        activity.clear_active()

    def clear_session(self) -> None:
        """Clear the current session."""

        transcript = self.query_one(
            "#transcript",
            Transcript,
        )

        activity = self.query_one(
            "#activity",
            Activity,
        )

        transcript.clear()

        activity.clear()

        self.state.clear_session()