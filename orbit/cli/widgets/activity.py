"""Activity display widget for ORBIT."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class Activity(Vertical):
    """Display the current and recent ORBIT activities."""

    DEFAULT_CSS = """
    Activity {
        height: auto;
        padding: 0 1;
    }

    Activity .activity-item {
        height: auto;
        margin: 0 0 1 0;
        color: #697581;
    }

    Activity .activity-active {
        color: #8bd5ff;
    }

    Activity .activity-success {
        color: #7ee787;
    }

    Activity .activity-warning {
        color: #e3b341;
    }

    Activity .activity-error {
        color: #f85149;
    }
    """

    def compose(self) -> ComposeResult:
        """Start with an empty activity area."""

        yield from ()

    def add(
        self,
        text: str,
        level: str = "active",
    ) -> None:
        """Add an activity item."""

        valid_levels = {
            "active",
            "success",
            "warning",
            "error",
        }

        if level not in valid_levels:
            level = "active"

        prefix = {
            "active": "◉",
            "success": "✓",
            "warning": "!",
            "error": "×",
        }[level]

        self.mount(
            Static(
                f"{prefix} {text}",
                classes=f"activity-item activity-{level}",
            )
        )

        self.scroll_end()

    def clear(self) -> None:
        """Remove all activity items."""

        for child in list(self.children):
            child.remove()