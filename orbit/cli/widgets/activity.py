"""Activity display widget for ORBIT."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class Activity(Vertical):
    """Display current and recent ORBIT activities."""

    DEFAULT_CSS = """
    Activity {
        height: auto;
        padding: 0 1;
    }

    Activity .activity-item {
        height: auto;
        margin: 0 0 1 0;
        color: #858585;
    }

    Activity .activity-active {
        color: #d97732;
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

    SPINNER_FRAMES = (
        "·",
        "✢",
        "✳",
        "✶",
        "✻",
        "✽",
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._spinner_index = 0

    def compose(self) -> ComposeResult:
        """Start with an empty activity area."""

        yield from ()

    def on_mount(self) -> None:
        """Start the activity spinner."""

        self.set_interval(
            0.12,
            self._advance_spinner,
        )

    def _advance_spinner(self) -> None:
        """Advance active activity indicators."""

        self._spinner_index = (
            self._spinner_index + 1
        ) % len(self.SPINNER_FRAMES)

        frame = self.SPINNER_FRAMES[
            self._spinner_index
        ]

        for item in self.query(
            ".activity-active"
        ):
            if not isinstance(item, Static):
                continue

            text = getattr(
                item,
                "_orbit_activity_text",
                None,
            )

            if text is None:
                continue

            item.update(
                f"{frame} {text}"
            )

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

        if level == "active":
            prefix = self.SPINNER_FRAMES[
                self._spinner_index
            ]
        else:
            prefix = {
                "success": "✓",
                "warning": "!",
                "error": "×",
            }[level]

        item = Static(
            f"{prefix} {text}",
            classes=f"activity-item activity-{level}",
        )

        item._orbit_activity_text = text

        self.mount(item)

        self.scroll_end()

    def clear_active(self) -> None:
        """Remove all currently active activities."""

        for child in list(
            self.query(".activity-active")
        ):
            child.remove()

    def clear(self) -> None:
        """Remove all activity items."""

        for child in list(self.children):
            child.remove()