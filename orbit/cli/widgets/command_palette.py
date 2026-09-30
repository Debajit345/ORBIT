"""Interactive command palette for the ORBIT terminal UI."""

from collections.abc import Sequence

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.events import Key
from textual.message import Message
from textual.widgets import Static

from ...commands.registry import Command


class CommandItem(Static):
    """Focusable and clickable command entry."""

    DEFAULT_CSS = """
    CommandItem {
        height: 1;
        padding: 0 1;
        color: #d7d7d7;
    }

    CommandItem:focus {
        background: #242424;
        color: #ff9f43;
        text-style: bold;
    }

    CommandItem:hover {
        background: #242424;
        color: #ff9f43;
    }
    """

    can_focus = True

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

    def on_click(self) -> None:
        """Execute this command."""

        self.post_message(
            self.Selected(self.command)
        )

    def on_key(self, event: Key) -> None:
        """Handle keyboard navigation."""

        palette = self.parent

        if not isinstance(palette, CommandPalette):
            return

        if event.key == "down":
            event.stop()
            palette.focus_next_item()

        elif event.key == "up":
            event.stop()
            palette.focus_previous_item()

        elif event.key == "enter":
            event.stop()
            self.post_message(
                self.Selected(self.command)
            )

        elif event.key == "escape":
            event.stop()
            palette.hide()
            palette.return_focus_to_prompt()


class CommandPalette(Vertical):
    """Display and navigate ORBIT slash commands."""

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

        self.commands = [
            command
            for command in commands
            if command.name != "/commands"
        ]

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

        self.call_after_refresh(
            self.focus_first_item
        )

    def hide(self) -> None:
        """Hide the command palette."""

        self.remove_class("visible")
        self.return_focus_to_prompt()

    def toggle(self) -> None:
        """Toggle command palette visibility."""

        if self.has_class("visible"):
            self.hide()
        else:
            self.show()

    def get_items(self) -> list[CommandItem]:
        """Return all command entries."""

        return list(
            self.query(CommandItem)
        )

    def get_focused_index(self) -> int:
        """Return the currently focused command index."""

        items = self.get_items()

        for index, item in enumerate(items):
            if item.has_focus:
                return index

        return 0

    def focus_first_item(self) -> None:
        """Focus the first command."""

        items = self.get_items()

        if items:
            items[0].focus()

    def focus_next_item(self) -> None:
        """Move focus to the next command."""

        items = self.get_items()

        if not items:
            return

        index = self.get_focused_index()

        next_index = min(
            index + 1,
            len(items) - 1,
        )

        items[next_index].focus()

    def focus_previous_item(self) -> None:
        """Move focus to the previous command."""

        items = self.get_items()

        if not items:
            return

        index = self.get_focused_index()

        previous_index = max(
            index - 1,
            0,
        )

        items[previous_index].focus()

    def return_focus_to_prompt(self) -> None:
        """Return focus to the ORBIT prompt."""

        session = self.screen.query_one(
            "#session"
        )

        prompt = session.query_one(
            "#prompt"
        )

        prompt.focus_input()