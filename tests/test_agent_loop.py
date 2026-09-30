import pytest
import asyncio

from orbit.agent import AgentStage, ResearchAgent
from orbit.ai import EchoProvider, ProviderRouter


@pytest.mark.asyncio
async def test_agent_emits_observable_research_stages() -> None:
    agent = ResearchAgent(ProviderRouter([EchoProvider()]))

    result = await agent.run("Find evidence about local models")

    assert result.provider == "echo"
    assert result.response.startswith("Offline analysis request received")
    assert [event.stage for event in result.events] == [
        AgentStage.REQUEST,
        AgentStage.PLAN,
        AgentStage.TOOLS,
        AgentStage.SYNTHESIS,
        AgentStage.RESPONSE,
    ]


@pytest.mark.asyncio
async def test_agent_rejects_empty_requests() -> None:
    agent = ResearchAgent(ProviderRouter([EchoProvider()]))

    with pytest.raises(ValueError, match="cannot be empty"):
        await agent.run("  ")


class FlakyProvider:
    name = "flaky"

    def __init__(self) -> None:
        self.attempts = 0

    async def complete(self, messages, *, model=None):
        self.attempts += 1
        if self.attempts == 1:
            raise RuntimeError("temporary failure")

        return await EchoProvider().complete(messages, model=model)


@pytest.mark.asyncio
async def test_agent_retries_transient_provider_failure() -> None:
    provider = FlakyProvider()
    agent = ResearchAgent(
        ProviderRouter([provider]),
        provider_name="flaky",
        backoff_seconds=0,
    )

    result = await agent.run("retry this")

    assert provider.attempts == 2
    assert "retry this" in result.response


@pytest.mark.asyncio
async def test_agent_honors_cooperative_cancellation() -> None:
    cancel_event = asyncio.Event()
    cancel_event.set()
    agent = ResearchAgent(ProviderRouter([EchoProvider()]))

    with pytest.raises(asyncio.CancelledError):
        await agent.run("cancel this", cancel_event=cancel_event)