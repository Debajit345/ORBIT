"""Prompt widget for the ORBIT terminal UI."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Input, Static


class Prompt(Vertical):
    """User input area for ORBIT."""

    DEFAULT_CSS = """
    Prompt {
        height: auto;
        padding: 1 0 0 0;
    }

    Prompt Input {
        height: 3;
        border: round #39434e;
        background: #12161b;
        color: #d7dde5;
        padding: 0 1;
    }

    Prompt Input:focus {
        border: round #6aaed6;
    }

    Prompt .prompt-hint {
        height: 2;
        color: #59636f;
        padding: 0 1;
    }
    """

    class Submitted(Message):
        """Message emitted when the user submits a prompt."""

        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    def compose(self) -> ComposeResult:
        """Build the prompt UI."""

        yield Input(
            placeholder="Ask ORBIT anything...",
            id="prompt-input",
        )

        yield Static(
            "Enter send   •   / commands   •   ↑↓ history",
            classes="prompt-hint",
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Convert Textual input submission into an ORBIT message."""

        value = event.value.strip()

        event.input.value = ""

        if not value:
            return

        self.post_message(
            self.Submitted(value)
        )

    def focus_input(self) -> None:
        """Focus the prompt input."""

        self.query_one("#prompt-input", Input).focus()