"""Status bar widget for the ORBIT terminal UI."""

from textual.widgets import Static

from ..state import OrbitState


class StatusBar(Static):
    """Display the current ORBIT session status."""

    DEFAULT_CSS = """
    StatusBar {
        height: 2;
        padding: 0 1;
        color: #626262;
    }

    StatusBar.status-ready {
        color: #626262;
    }

    StatusBar.status-working {
        color: #d97732;
    }

    StatusBar.status-error {
        color: #f85149;
    }
    """

    def update_from_state(
        self,
        state: OrbitState,
    ) -> None:
        """Update the status bar from ORBIT runtime state."""

        self.update(
            state.status_text
        )

        self.remove_class(
            "status-ready",
            "status-working",
            "status-error",
        )

        if state.ready:
            self.add_class(
                "status-ready"
            )
        else:
            self.add_class(
                "status-working"
            )