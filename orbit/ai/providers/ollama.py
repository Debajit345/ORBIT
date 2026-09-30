"""Local Ollama provider adapter."""

import httpx
import json
from collections.abc import AsyncIterator

from ..protocol import AIMessage, AIResponse, AIStreamChunk


class OllamaProvider:
    """Call a local Ollama `/api/chat` endpoint."""

    name = "ollama"

    def __init__(
        self,
        *,
        base_url: str = "http://localhost:11434",
        default_model: str = "llama3.2",
        timeout: float = 60.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = timeout
        self.transport = transport

    async def complete(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
    ) -> AIResponse:
        selected_model = model or self.default_model
        payload = {
            "model": selected_model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
            "stream": False,
        }

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            transport=self.transport,
        ) as client:
            response = await client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()

        try:
            content = data["message"]["content"]
        except (KeyError, TypeError) as error:
            raise RuntimeError("Invalid Ollama response") from error

        return AIResponse(
            content=content,
            provider=self.name,
            model=selected_model,
            metadata={"done": data.get("done", True)},
        )

    async def stream(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
    ) -> AsyncIterator[AIStreamChunk]:
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
            timeout=self.timeout,
            transport=self.transport,
        ) as client:
            async with client.stream("POST", "/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue

                    data = json.loads(line)
                    yield AIStreamChunk(
                        text=data.get("message", {}).get("content", ""),
                        done=bool(data.get("done", False)),
                        metadata={"total_duration": data.get("total_duration")},
                    )