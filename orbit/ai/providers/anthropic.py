"""Anthropic messages API provider adapter."""

import os

import httpx

from ..protocol import AIMessage, AIResponse


class AnthropicProvider:
    """Call the Anthropic Messages API."""

    name = "anthropic"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        default_model: str = "claude-3-5-haiku-latest",
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.default_model = default_model
        self.timeout = timeout
        self.transport = transport

    async def complete(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
    ) -> AIResponse:
        if not self.api_key:
            raise RuntimeError("Anthropic API key is not configured")

        selected_model = model or self.default_model
        system_messages = [
            message.content
            for message in messages
            if message.role == "system"
        ]
        conversation = [
            {"role": message.role, "content": message.content}
            for message in messages
            if message.role != "system"
        ]
        payload = {
            "model": selected_model,
            "max_tokens": 2048,
            "messages": conversation,
        }
        if system_messages:
            payload["system"] = "\n\n".join(system_messages)

        async with httpx.AsyncClient(
            base_url="https://api.anthropic.com/v1",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            timeout=self.timeout,
            transport=self.transport,
        ) as client:
            response = await client.post("/messages", json=payload)
            response.raise_for_status()
            data = response.json()

        try:
            content = data["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError("Invalid Anthropic response") from error

        return AIResponse(
            content=content,
            provider=self.name,
            model=selected_model,
            metadata={"usage": data.get("usage", {})},
        )