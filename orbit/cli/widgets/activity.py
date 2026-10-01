"""Activity display widget for the ORBIT terminal UI."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class Activity(Vertical):
    """Display one transient ORBIT activity at a time."""

    DEFAULT_CSS = """
    Activity {
        height: auto;
        padding: 0 1;
    }

    Activity .activity-item {
        height: 1;
        margin: 0;
        opacity: 1;
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

    TRANSIENT_DURATION = 1.6
    FADE_DURATION = 0.35

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._spinner_index = 0
        self._generation = 0

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
        """Advance the active activity indicator."""

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
        """
        Show one activity message.

        Any previous activity is replaced.
        Success, warning, and error messages automatically
        fade away after a short delay.
        """

        valid_levels = {
            "active",
            "success",
            "warning",
            "error",
        }

        if level not in valid_levels:
            level = "active"

        # Invalidate any previous scheduled dismissal.
        self._generation += 1
        generation = self._generation

        # Never stack activity messages.
        self._remove_all_items()

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

        # Terminal states disappear automatically.
        if level != "active":
            self.set_timer(
                self.TRANSIENT_DURATION,
                lambda: self._fade_current(
                    item,
                    generation,
                ),
            )

    def _fade_current(
        self,
        item: Static,
        generation: int,
    ) -> None:
        """Fade the current transient activity out."""

        if generation != self._generation:
            return

        if item not in self.children:
            return

        item.styles.animate(
            "opacity",
            0.0,
            duration=self.FADE_DURATION,
            on_complete=lambda: self._remove_if_current(
                item,
                generation,
            ),
        )

    def _remove_if_current(
        self,
        item: Static,
        generation: int,
    ) -> None:
        """Remove the item if it is still the current activity."""

        if generation != self._generation:
            return

        if item in self.children:
            item.remove()

    def _remove_all_items(self) -> None:
        """Remove every visible activity item."""

        for child in list(self.children):
            child.remove()

    def clear_active(self) -> None:
        """Remove the current active activity."""

        for child in list(
            self.query(".activity-active")
        ):
            child.remove()

    def clear(self) -> None:
        """Remove all activity items."""

        self._generation += 1
        self._remove_all_items()