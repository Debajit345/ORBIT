"""Central command registry for ORBIT."""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Command:
    """Definition of an ORBIT slash command."""

    name: str
    description: str
    handler: Callable


class CommandRegistry:
    """Register and resolve ORBIT slash commands."""

    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}

    def register(
        self,
        name: str,
        description: str,
        handler: Callable,
    ) -> None:
        """Register a command."""

        normalized_name = self._normalize_name(name)

        self._commands[normalized_name] = Command(
            name=normalized_name,
            description=description,
            handler=handler,
        )

    def get(self, name: str) -> Command | None:
        """Return a command by name."""

        normalized_name = self._normalize_name(name)

        return self._commands.get(normalized_name)

    def all(self) -> list[Command]:
        """Return all registered commands."""

        return list(self._commands.values())

    def clear(self) -> None:
        """Remove all registered commands."""

        self._commands.clear()

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize a command name for registration and lookup."""

        normalized_name = name.strip().lower()

        if not normalized_name.startswith("/"):
            normalized_name = f"/{normalized_name}"

        return normalized_name