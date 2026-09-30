"""A small, observable research-agent execution loop."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
import asyncio
from collections.abc import Awaitable, Callable
from collections.abc import AsyncIterator

from ..ai import AIMessage, AIStreamChunk, ProviderRouter


class AgentStage(StrEnum):
    """Stages exposed to the terminal activity stream."""

    REQUEST = "request"
    PLAN = "plan"
    TOOLS = "tools"
    SYNTHESIS = "synthesis"
    RESPONSE = "response"


@dataclass(frozen=True)
class AgentEvent:
    """A timestamped event emitted during one agent run."""

    stage: AgentStage
    message: str
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass(frozen=True)
class AgentResult:
    """Final response and trace for one agent request."""

    response: str
    provider: str
    model: str
    events: tuple[AgentEvent, ...]


class ResearchAgent:
    """Execute a provider-backed research request with observable stages."""

    def __init__(
        self,
        router: ProviderRouter,
        provider_name: str = "echo",
        *,
        max_retries: int = 2,
        backoff_seconds: float = 0.25,
        sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self.router = router
        self.provider_name = provider_name
        self.max_retries = max(0, max_retries)
        self.backoff_seconds = max(0.0, backoff_seconds)
        self.sleeper = sleeper

    async def run(
        self,
        request: str,
        *,
        cancel_event: asyncio.Event | None = None,
    ) -> AgentResult:
        """Run the request through planning, tools, and synthesis stages."""

        if not request.strip():
            raise ValueError("Research request cannot be empty")

        self._check_cancelled(cancel_event)
        events = [
            AgentEvent(AgentStage.REQUEST, "Request received"),
            AgentEvent(AgentStage.PLAN, "Planning research steps"),
            AgentEvent(
                AgentStage.TOOLS,
                "No research tools are configured; using offline context",
            ),
            AgentEvent(AgentStage.SYNTHESIS, "Synthesizing available context"),
        ]

        provider = self.router.get(self.provider_name)
        messages = [AIMessage(role="user", content=request)]
        response = None

        for attempt in range(self.max_retries + 1):
            self._check_cancelled(cancel_event)

            try:
                response = await provider.complete(messages)
                break
            except asyncio.CancelledError:
                raise
            except Exception:
                if attempt >= self.max_retries:
                    raise

                await self.sleeper(
                    self.backoff_seconds * 2**attempt
                )

        if response is None:
            raise RuntimeError("Provider returned no response")

        events.append(AgentEvent(AgentStage.RESPONSE, "Response ready"))

        return AgentResult(
            response=response.content,
            provider=response.provider,
            model=response.model,
            events=tuple(events),
        )

    async def stream(
        self,
        request: str,
        *,
        cancel_event: asyncio.Event | None = None,
    ) -> AsyncIterator[AIStreamChunk]:
        """Stream provider output, falling back to one complete response."""

        if not request.strip():
            raise ValueError("Research request cannot be empty")

        self._check_cancelled(cancel_event)
        provider = self.router.get(self.provider_name)
        messages = [AIMessage(role="user", content=request)]
        stream_method = getattr(provider, "stream", None)

        if stream_method is None:
            response = await provider.complete(messages)
            yield AIStreamChunk(text=response.content, done=True)
            return

        async for chunk in stream_method(messages):
            self._check_cancelled(cancel_event)
            yield chunk

    @staticmethod
    def _check_cancelled(cancel_event: asyncio.Event | None) -> None:
        if cancel_event is not None and cancel_event.is_set():
            raise asyncio.CancelledError