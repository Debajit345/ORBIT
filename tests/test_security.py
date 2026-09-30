from datetime import timedelta

import pytest

from orbit.security import AuditLogger, AuthorizationPolicy, TokenIssuer


def test_tokens_and_scopes_are_verified(tmp_path) -> None:
    issuer = TokenIssuer("x" * 32)
    token = issuer.issue("researcher", ("research:read",))
    claims = issuer.verify(token)

    assert claims.subject == "researcher"
    AuthorizationPolicy.require(claims, "research:read")

    with pytest.raises(PermissionError, match="Missing required scope"):
        AuthorizationPolicy.require(claims, "admin")

    with pytest.raises(PermissionError, match="expired"):
        issuer.verify(issuer.issue("researcher", ttl=timedelta(seconds=-1)))


def test_audit_logger_redacts_secret_like_metadata(tmp_path) -> None:
    path = tmp_path / "audit.jsonl"
    AuditLogger(path).record(
        "login",
        "researcher",
        {"provider": "ollama", "api_key": "should-not-persist"},
    )

    text = path.read_text(encoding="utf-8")
    assert "ollama" in text
    assert "should-not-persist" not in text