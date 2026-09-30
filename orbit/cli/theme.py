"""Central visual theme for the ORBIT terminal UI."""


THEME = {
    "background": "#0b0b0b",
    "surface": "#111111",
    "surface_alt": "#171717",
    "border": "#2a2a2a",
    "border_focus": "#d97732",
    "text": "#e6e6e6",
    "text_muted": "#858585",
    "text_subtle": "#626262",
    "primary": "#d97732",
    "primary_bright": "#ff9f43",
    "accent": "#c792ea",
    "success": "#7ee787",
    "warning": "#e3b341",
    "danger": "#f85149",
}


def get_color(name: str) -> str:
    """Return a theme color."""

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
    color: {THEME["primary_bright"]};
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
    padding: 0 1;
}}

#mascot {{
    height: 1;
}}

#command-palette {{
    height: auto;
}}

#status-bar {{
    height: 2;
    color: {THEME["text_muted"]};
}}
"""