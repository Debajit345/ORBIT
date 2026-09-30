"""Interactive command palette for the ORBIT terminal UI."""

from collections.abc import Sequence

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.events import Click
from textual.message import Message
from textual.widgets import Static

from ...commands.registry import Command


class CommandItem(Static):
    """Clickable command entry."""

    can_focus = True

    DEFAULT_CSS = """
    CommandItem {
        height: 1;
        padding: 0 1;
        color: #d7d7d7;
    }

    CommandItem:hover {
        background: #242424;
        color: #ff9f43;
    }

    CommandItem:focus {
        background: #242424;
        color: #ff9f43;
    }
    """

    class Selected(Message):
        """Message emitted when a command is selected."""

        def __init__(self, command: str) -> None:
            self.command = command
            super().__init__()

    def __init__(
        self,
        command: str,
        description: str,
    ) -> None:
        self.command = command

        super().__init__(
            f"{command:<14} {description}"
        )

    def on_click(self, event: Click) -> None:
        """Notify the application that this command was selected."""

        self.post_message(
            self.Selected(self.command)
        )


class CommandPalette(Vertical):
    """Display clickable ORBIT slash commands."""

    DEFAULT_CSS = """
    CommandPalette {
        height: auto;
        max-height: 12;
        padding: 1 1;
        background: #111111;
        border: round #303030;
        display: none;
    }

    CommandPalette.visible {
        display: block;
    }

    CommandPalette .palette-title {
        height: 1;
        color: #ff9f43;
        text-style: bold;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        commands: Sequence[Command],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.commands = commands

    def compose(self) -> ComposeResult:
        """Build the command palette."""

        yield Static(
            "ORBIT Commands",
            classes="palette-title",
        )

        for command in self.commands:
            yield CommandItem(
                command.name,
                command.description,
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