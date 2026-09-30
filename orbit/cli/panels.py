from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .themes import THEME

console = Console()


def show_banner() -> None:
    console.print(
        Panel.fit(
            f"[bold {THEME['primary']}]O R B I T[/bold {THEME['primary']}]\n"
            f"[dim]Open Research & Broadcast Intelligence Terminal[/dim]",
            border_style=THEME["primary"],
        )
    )


def show_help() -> None:
    table = Table(
        title="ORBIT Commands",
        show_header=True,
        header_style=f"bold {THEME['primary']}",
    )

    table.add_column("Command", style=THEME["primary"])
    table.add_column("Description")

    table.add_row("/help", "Show available commands")
    table.add_row("/status", "Show ORBIT system status")
    table.add_row("/doctor", "Run system diagnostics")
    table.add_row("/exit", "Exit ORBIT")

    console.print(table)


def show_status() -> None:
    table = Table(
        title="ORBIT Status",
        show_header=True,
        header_style=f"bold {THEME['primary']}",
    )

    table.add_column("Component")
    table.add_column("Status")

    table.add_row("CLI", f"[green]ONLINE[/green]")
    table.add_row("Server", f"[green]READY[/green]")
    table.add_row("Knowledge Vault", "[yellow]NOT CONFIGURED[/yellow]")
    table.add_row("AI", "[yellow]NOT CONFIGURED[/yellow]")
    table.add_row("Sources", "0")

    console.print(table)


def show_doctor() -> None:
    table = Table(
        title="ORBIT Diagnostics",
        show_header=True,
        header_style=f"bold {THEME['primary']}",
    )

    table.add_column("Component")
    table.add_column("Result")

    table.add_row("Python", "[green]OK[/green]")
    table.add_row("Rich", "[green]OK[/green]")
    table.add_row("CLI", "[green]OK[/green]")
    table.add_row("AI", "[yellow]NOT CONFIGURED[/yellow]")
    table.add_row("Obsidian", "[yellow]NOT CONFIGURED[/yellow]")

    console.print(table)
