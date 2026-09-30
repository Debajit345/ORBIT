"""Command handling for the ORBIT CLI."""

from rich.console import Console

from .panels import show_doctor, show_help, show_status

console = Console()


def handle_command(command: str) -> bool:
    command = command.strip().lower()

    if command == "/help":
        show_help()
    elif command == "/status":
        show_status()
    elif command == "/doctor":
        show_doctor()
    elif command in {"/exit", "/quit"}:
        return False
    elif command == "":
        pass
    else:
        console.print(f"[red]Unknown command:[/red] {command}")
        console.print("Type [cyan]/help[/cyan] to see available commands.")

    return True
