import pytest

from orbit.ai import AIMessage, EchoProvider, ProviderRouter
from orbit.ai.providers import OllamaProvider


@pytest.mark.asyncio
async def test_echo_provider_is_offline_and_deterministic() -> None:
    response = await EchoProvider().complete(
        [AIMessage(role="user", content="Investigate this")]
    )

    assert response.provider == "echo"
    assert response.metadata["offline"] is True
    assert "Investigate this" in response.content


def test_provider_router_reports_available_providers() -> None:
    router = ProviderRouter([EchoProvider()])

    assert router.get(" ECHO ").name == "echo"

    with pytest.raises(LookupError, match="Available providers: echo"):
        router.get("missing")


def test_provider_router_can_prefer_local_inference() -> None:
    router = ProviderRouter([EchoProvider(), OllamaProvider()])

    assert router.select(local_only=True).name == "ollama"
    assert router.select(preferred="echo").name == "echo"