"""Central visual theme for the ORBIT terminal UI."""


THEME = {
    "background": "#0b0d10",
    "surface": "#101419",
    "surface_alt": "#12161b",
    "border": "#39434e",
    "border_focus": "#6aaed6",
    "text": "#d7dde5",
    "text_muted": "#697581",
    "text_subtle": "#59636f",
    "primary": "#8bd5ff",
    "accent": "#c792ea",
    "success": "#7ee787",
    "warning": "#e3b341",
    "danger": "#f85149",
}


def get_color(name: str) -> str:
    """Return a theme color, falling back to the primary color."""

    return THEME.get(
        name,
        THEME["primary"],
    )


CSS = f"""
Screen {{
    background: {THEME["background"]};
    color: {THEME["text"]};
}}

Header {{
    background: {THEME["surface"]};
    color: {THEME["primary"]};
    height: 3;
}}

Footer {{
    background: {THEME["surface"]};
    color: {THEME["text_muted"]};
}}

#session {{
    height: 1fr;
    padding: 0 2;
}}

#transcript {{
    height: 1fr;
    background: {THEME["background"]};
}}

#activity {{
    height: auto;
}}

#command-palette {{
    height: auto;
}}

#status-bar {{
    height: 2;
    color: {THEME["text_muted"]};
}}
"""