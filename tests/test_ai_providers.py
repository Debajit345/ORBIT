import httpx
import pytest

from orbit.ai import AIMessage
from orbit.ai.providers import (
    AnthropicProvider,
    GeminiProvider,
    OllamaProvider,
    OpenAICompatibleProvider,
)


def transport_for(payload: dict) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    return httpx.MockTransport(handler)


def stream_transport(body: str) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=body.encode(),
            headers={"content-type": "text/event-stream"},
        )

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_openai_compatible_provider_parses_response() -> None:
    provider = OpenAICompatibleProvider(
        api_key="test-key",
        transport=transport_for(
            {"choices": [{"message": {"content": "answer"}}]}
        ),
    )

    response = await provider.complete(
        [AIMessage(role="user", content="question")]
    )

    assert response.content == "answer"
    assert response.provider == "openai"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("provider", "payload", "expected"),
    [
        (OllamaProvider, {"message": {"content": "local"}}, "local"),
        (
            GeminiProvider,
            {"candidates": [{"content": {"parts": [{"text": "gemini"}]}}]},
            "gemini",
        ),
        (AnthropicProvider, {"content": [{"text": "claude"}]}, "claude"),
    ],
)
async def test_provider_adapters_parse_responses(provider, payload, expected) -> None:
    kwargs = {"transport": transport_for(payload)}
    if provider is GeminiProvider:
        kwargs["api_key"] = "test-key"
    if provider is AnthropicProvider:
        kwargs["api_key"] = "test-key"

    response = await provider(**kwargs).complete(
        [AIMessage(role="user", content="question")]
    )

    assert response.content == expected


@pytest.mark.asyncio
async def test_openai_compatible_provider_streams_sse_chunks() -> None:
    provider = OpenAICompatibleProvider(
        api_key="test-key",
        transport=stream_transport(
            'data: {"choices":[{"delta":{"content":"hello "}}]}\n'
            'data: {"choices":[{"delta":{"content":"world"}}]}\n'
            "data: [DONE]\n"
        ),
    )

    chunks = [
        chunk async for chunk in provider.stream(
            [AIMessage(role="user", content="question")]
        )
    ]

    assert "".join(chunk.text for chunk in chunks) == "hello world"
    assert chunks[-1].done is True


@pytest.mark.asyncio
async def test_ollama_provider_streams_json_lines() -> None:
    provider = OllamaProvider(
        transport=stream_transport(
            '{"message":{"content":"hello "},"done":false}\n'
            '{"message":{"content":"world"},"done":true}\n'
        ),
    )

    chunks = [
        chunk async for chunk in provider.stream(
            [AIMessage(role="user", content="question")]
        )
    ]

    assert "".join(chunk.text for chunk in chunks) == "hello world"
    assert chunks[-1].done is True