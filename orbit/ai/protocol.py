"""Stable interfaces for local and hosted AI providers."""

from dataclasses import dataclass, field
from collections.abc import AsyncIterator
from typing import Protocol


@dataclass(frozen=True)
class AIMessage:
    """A provider-neutral conversation message."""

    role: str
    content: str


@dataclass(frozen=True)
class AIResponse:
    """Provider response with routing and usage metadata."""

    content: str
    provider: str
    model: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class AIStreamChunk:
    """One incremental provider response chunk."""

    text: str
    done: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


class AIProvider(Protocol):
    """Async completion contract implemented by every provider adapter."""

    name: str

    async def complete(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
    ) -> AIResponse:
        """Generate a response for a conversation."""

    async def stream(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
    ) -> AsyncIterator[AIStreamChunk]:
        """Yield incremental response chunks."""


class EchoProvider:
    """Offline provider used for local development and deterministic tests."""

    name = "echo"

    async def complete(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
    ) -> AIResponse:
        user_message = next(
            (
                message.content
                for message in reversed(messages)
                if message.role == "user"
            ),
            "",
        )

        return AIResponse(
            content=f"Offline analysis request received: {user_message}",
            provider=self.name,
            model=model or "echo-1",
            metadata={"offline": True},
        )

    async def stream(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
    ) -> AsyncIterator[AIStreamChunk]:
        response = await self.complete(messages, model=model)
        words = response.content.split(" ")

        for index, word in enumerate(words):
            yield AIStreamChunk(
                text=word + (" " if index < len(words) - 1 else ""),
                done=index == len(words) - 1,
                metadata={"offline": True},
            )


class ProviderRouter:
    """Route requests to named providers without coupling callers to SDKs."""

    def __init__(self, providers: list[AIProvider]) -> None:
        self._providers = {provider.name: provider for provider in providers}

    def get(self, name: str) -> AIProvider:
        """Return a configured provider or fail with an actionable error."""

        provider = self._providers.get(name.strip().lower())

        if provider is None:
            available = ", ".join(sorted(self._providers)) or "none"
            raise LookupError(
                f"Unknown AI provider '{name}'. Available providers: {available}"
            )

        return provider

    def select(
        self,
        *,
        preferred: str | None = None,
        local_only: bool = False,
    ) -> AIProvider:
        """Select a provider using explicit preference and privacy policy."""

        if preferred:
            return self.get(preferred)

        if local_only and "ollama" in self._providers:
            return self._providers["ollama"]

        for name in ("ollama", "openai", "openrouter", "gemini", "anthropic", "echo"):
            if name in self._providers:
                return self._providers[name]

        raise LookupError("No AI providers are configured")