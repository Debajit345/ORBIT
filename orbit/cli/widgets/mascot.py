"""Independent ORBIT character state and animation widget."""

from enum import StrEnum

from textual.widgets import Static


class MascotState(StrEnum):
    """Visible ORBIT activity states."""

    IDLE = "idle"
    WORKING = "working"
    TOOL = "tool"
    SUCCESS = "success"
    WARNING = "warning"
    WAITING = "waiting"


class Mascot(Static):
    """Compact character indicator with purposeful state animation."""

    DEFAULT_CSS = """
    Mascot {
        height: 1;
        color: #ff9f43;
        padding: 0 1;
    }
    """

    FRAMES = {
        MascotState.IDLE: ("◌",),
        MascotState.WORKING: ("◒", "◓", "◑", "◐"),
        MascotState.TOOL: ("◇", "◆"),
        MascotState.SUCCESS: ("✦",),
        MascotState.WARNING: ("△",),
        MascotState.WAITING: ("…",),
    }

    def __init__(self, state: MascotState = MascotState.WAITING, **kwargs) -> None:
        super().__init__(**kwargs)
        self.state = state
        self._frame_index = 0

    def on_mount(self) -> None:
        self._render_frame()
        self.set_interval(0.16, self._advance)

    def set_state(self, state: MascotState) -> None:
        """Change the character state and restart its frame sequence."""

        self.state = state
        self._frame_index = 0
        self._render_frame()

    def _advance(self) -> None:
        frames = self.FRAMES[self.state]
        if len(frames) > 1:
            self._frame_index = (self._frame_index + 1) % len(frames)
            self._render_frame()

    def _render_frame(self) -> None:
        self.update(f"{self.FRAMES[self.state][self._frame_index]} ORBIT")