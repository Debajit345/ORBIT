import pytest

from orbit.cli.app import OrbitApp
from orbit.cli.widgets.command_palette import CommandItem, CommandPalette
from orbit.cli.widgets.prompt import Prompt
from orbit.commands.registry import CommandRegistry


def test_command_registry_normalizes_names() -> None:
    registry = CommandRegistry()
    handler = lambda session: session

    registry.register("  STATUS ", "Show status", handler)

    assert registry.get("/status").handler is handler
    assert registry.get("status").name == "/status"


@pytest.mark.asyncio
async def test_typed_commands_opens_palette_and_palette_excludes_launcher() -> None:
    app = OrbitApp()

    async with app.run_test() as pilot:
        palette = app.query_one("#command-palette", CommandPalette)
        prompt = app.query_one("#prompt", Prompt)
        items = list(palette.query(CommandItem))

        assert "/commands" not in [item.command for item in items]

        prompt_input = prompt.query_one("#prompt-input")
        prompt_input.value = "/commands"
        await pilot.press("enter")
        await pilot.pause()

        assert palette.has_class("visible")
        assert app.state.messages[-1].content == "/commands"


@pytest.mark.asyncio
async def test_natural_language_request_runs_offline_agent() -> None:
    app = OrbitApp()

    async with app.run_test() as pilot:
        prompt = app.query_one("#prompt", Prompt)
        prompt_input = prompt.query_one("#prompt-input")
        prompt_input.value = "Research local model options"
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()

        assert "Offline analysis request received" in app.state.messages[-1].content


@pytest.mark.asyncio
async def test_sources_command_reports_configured_provenance_endpoints() -> None:
    app = OrbitApp()

    async with app.run_test() as pilot:
        prompt = app.query_one("#prompt", Prompt)
        prompt_input = prompt.query_one("#prompt-input")
        prompt_input.value = "/sources"
        await pilot.press("enter")
        await pilot.pause()

        assert "NASA (RSS)" in app.state.messages[-1].content
        assert "https://www.nasa.gov/" in app.state.messages[-1].content