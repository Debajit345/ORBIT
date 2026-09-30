"""Built-in ORBIT command definitions."""

from collections.abc import Callable

from .registry import CommandRegistry


def register_builtin_commands(
    registry: CommandRegistry,
    *,
    help_handler: Callable,
    commands_handler: Callable,
    status_handler: Callable,
    doctor_handler: Callable,
    clear_handler: Callable,
    exit_handler: Callable,
) -> None:
    """Register ORBIT's built-in slash commands."""

    registry.register(
        "/help",
        "Show available commands",
        help_handler,
    )

    registry.register(
        "/commands",
        "Open the command palette",
        commands_handler,
    )

    registry.register(
        "/status",
        "Show system status",
        status_handler,
    )

    registry.register(
        "/doctor",
        "Run diagnostics",
        doctor_handler,
    )

    registry.register(
        "/clear",
        "Clear the current session",
        clear_handler,
    )

    registry.register(
        "/exit",
        "Exit ORBIT",
        exit_handler,
    )