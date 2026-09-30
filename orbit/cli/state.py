"""Runtime state for the ORBIT terminal interface."""

from dataclasses import dataclass, field


@dataclass
class Message:
    """A single message displayed in the ORBIT transcript."""

    role: str
    content: str


@dataclass
class Activity:
    """A visible activity/status event."""

    text: str
    level: str = "info"


@dataclass
class OrbitState:
    """Mutable runtime state for an ORBIT session."""

    messages: list[Message] = field(default_factory=list)
    activities: list[Activity] = field(default_factory=list)

    ai_provider: str = "AUTO"
    source_count: int = 1
    session_name: str = "NEW"

    ready: bool = True

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the current transcript."""

        self.messages.append(
            Message(
                role=role,
                content=content,
            )
        )

    def add_activity(
        self,
        text: str,
        level: str = "info",
    ) -> None:
        """Add an activity event."""

        self.activities.append(
            Activity(
                text=text,
                level=level,
            )
        )

    def clear_session(self) -> None:
        """Clear the current conversation and activities."""

        self.messages.clear()
        self.activities.clear()

    @property
    def status_text(self) -> str:
        """Return the compact status line used by the TUI."""

        ready = "READY" if self.ready else "BUSY"

        return (
            f"● {ready}"
            f"    │    AI: {self.ai_provider}"
            f"    │    SOURCES: {self.source_count}"
            f"    │    SESSION: {self.session_name}"
        )