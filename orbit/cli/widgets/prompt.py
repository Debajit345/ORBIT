"""Prompt widget for the ORBIT terminal UI."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Input, Static


class Prompt(Vertical):
    """User input area for ORBIT."""

    DEFAULT_CSS = """
    Prompt {
        height: auto;
        padding: 1 0 0 0;
    }

    Prompt .prompt-row {
        height: 3;
    }

    Prompt .prompt-symbol {
        width: 3;
        height: 3;
        padding: 1 0 0 1;
        color: #ff9f43;
        text-style: bold;
    }

    Prompt Input {
        width: 1fr;
        height: 3;
        border: none;
        background: #111111;
        color: #e6e6e6;
        padding: 0 1;
    }

    Prompt Input:focus {
        border: none;
    }

    Prompt .prompt-hint {
        height: 2;
        padding: 0 1;
        color: #626262;
    }
    """

    class Submitted(Message):
        """Message emitted when the user submits a prompt."""

        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    def compose(self) -> ComposeResult:
        """Build the prompt UI."""

        with Horizontal(classes="prompt-row"):
            yield Static(
                "❯",
                classes="prompt-symbol",
            )

            yield Input(
                placeholder="Ask ORBIT anything...",
                id="prompt-input",
            )

        yield Static(
            "Enter send   ·   / commands   ·   ↑↓ history",
            classes="prompt-hint",
        )

    def on_input_submitted(
        self,
        event: Input.Submitted,
    ) -> None:
        """Convert input submission into an ORBIT message."""

        value = event.value.strip()

        event.input.value = ""

        if not value:
            return

        self.post_message(
            self.Submitted(value)
        )

    def focus_input(self) -> None:
        """Focus the prompt input."""

        self.query_one(
            "#prompt-input",
            Input,
        ).focus()