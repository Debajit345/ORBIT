import pytest

from orbit.tools import (
    PermissionPolicy,
    ToolDefinition,
    ToolPermission,
    ToolRegistry,
)


def test_tool_registry_enforces_approval_boundaries() -> None:
    registry = ToolRegistry(
        PermissionPolicy(
            allowed={ToolPermission.READ, ToolPermission.NETWORK},
            require_approval={ToolPermission.NETWORK},
        )
    )
    registry.register(
        ToolDefinition(
            name="fetch",
            description="Fetch a source",
            permission=ToolPermission.NETWORK,
            handler=lambda url: f"fetched {url}",
        )
    )

    with pytest.raises(PermissionError, match="requires approval"):
        registry.execute("FETCH", "https://example.com")

    assert registry.execute(
        "fetch",
        "https://example.com",
        approved=True,
    ) == "fetched https://example.com"


def test_tool_registry_denies_write_by_default() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="write_note",
            description="Write a note",
            permission=ToolPermission.WRITE,
            handler=lambda: None,
        )
    )

    with pytest.raises(PermissionError, match="not allowed"):
        registry.execute("write_note")