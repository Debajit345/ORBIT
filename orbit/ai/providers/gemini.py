"""Google Gemini generate-content provider adapter."""

import os

import httpx

from ..protocol import AIMessage, AIResponse


class GeminiProvider:
    """Call the Gemini REST generateContent endpoint."""

    name = "gemini"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        default_model: str = "gemini-2.0-flash",
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
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
            raise RuntimeError("Gemini API key is not configured")

        selected_model = model or self.default_model
        contents = [
            {
                "role": "model" if message.role == "assistant" else "user",
                "parts": [{"text": message.content}],
            }
            for message in messages
            if message.role != "system"
        ]

        async with httpx.AsyncClient(
            base_url="https://generativelanguage.googleapis.com/v1beta",
            params={"key": self.api_key},
            timeout=self.timeout,
            transport=self.transport,
        ) as client:
            response = await client.post(
                f"/models/{selected_model}:generateContent",
                json={"contents": contents},
            )
            response.raise_for_status()
            data = response.json()

        try:
            content = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError("Invalid Gemini response") from error

        return AIResponse(
            content=content,
            provider=self.name,
            model=selected_model,
            metadata={"usage": data.get("usageMetadata", {})},
        )