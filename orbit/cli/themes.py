"""Theme definitions for the ORBIT CLI."""

THEME = {
    "primary": "cyan",
    "secondary": "magenta",
    "success": "green",
    "warning": "yellow",
    "danger": "red",
    "muted": "dim",
    "title": "bold cyan",
    "accent": "bold magenta",
}


def get_color(name: str) -> str:
    return THEME.get(name, "white")
