"""Explicit tool registration and approval policy."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable


class ToolPermission(StrEnum):
    """Permission levels required by a tool."""

    READ = "read"
    WRITE = "write"
    NETWORK = "network"


@dataclass(frozen=True)
class ToolDefinition:
    """A callable tool with an explicit permission requirement."""

    name: str
    description: str
    permission: ToolPermission
    handler: Callable[..., Any]


class PermissionPolicy:
    """Deny-by-default policy for agent tool execution."""

    def __init__(
        self,
        *,
        allowed: set[ToolPermission] | None = None,
        require_approval: set[ToolPermission] | None = None,
    ) -> None:
        self.allowed = allowed or set()
        self.require_approval = require_approval or set()

    def check(
        self,
        permission: ToolPermission,
        *,
        approved: bool = False,
    ) -> None:
        """Raise unless a tool permission is allowed and approved."""

        if permission not in self.allowed:
            raise PermissionError(
                f"Tool permission '{permission}' is not allowed"
            )

        if permission in self.require_approval and not approved:
            raise PermissionError(
                f"Tool permission '{permission}' requires approval"
            )


class ToolRegistry:
    """Resolve and execute explicitly registered tools."""

    def __init__(self, policy: PermissionPolicy | None = None) -> None:
        self.policy = policy or PermissionPolicy()
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Register or replace a named tool."""

        self._tools[tool.name.strip().lower()] = tool

    def get(self, name: str) -> ToolDefinition | None:
        """Return a tool by normalized name."""

        return self._tools.get(name.strip().lower())

    def execute(
        self,
        name: str,
        *args: Any,
        approved: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Check permission and execute a registered tool."""

        tool = self.get(name)

        if tool is None:
            raise LookupError(f"Unknown tool: {name}")

        self.policy.check(tool.permission, approved=approved)
        return tool.handler(*args, **kwargs)