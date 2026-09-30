"""OpenAI-compatible provider adapter for OpenAI and OpenRouter."""

import os
import json
from collections.abc import AsyncIterator

import httpx

from ..protocol import AIMessage, AIResponse, AIStreamChunk


class OpenAICompatibleProvider:
    """Call providers implementing the OpenAI chat-completions contract."""

    def __init__(
        self,
        *,
        name: str = "openai",
        base_url: str = "https://api.openai.com/v1",
        api_key: str | None = None,
        default_model: str = "gpt-4o-mini",
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
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
            raise RuntimeError(f"{self.name} API key is not configured")

        payload = {
            "model": model or self.default_model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
        }

        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout,
            transport=self.transport,
        ) as client:
            response = await client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError(f"Invalid {self.name} response") from error

        return AIResponse(
            content=content,
            provider=self.name,
            model=payload["model"],
            metadata={"usage": data.get("usage", {})},
        )

    async def stream(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
    ) -> AsyncIterator[AIStreamChunk]:
        if not self.api_key:
            raise RuntimeError(f"{self.name} API key is not configured")

        payload = {
            "model": model or self.default_model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
            "stream": True,
        }

        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout,
            transport=self.transport,
        ) as client:
            async with client.stream(
                "POST",
                "/chat/completions",
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue

                    data = line[5:].strip()
                    if data == "[DONE]":
                        yield AIStreamChunk(text="", done=True)
                        return

                    chunk = json.loads(data)
                    text = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if text:
                        yield AIStreamChunk(text=text)