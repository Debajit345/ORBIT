"""Small dependency-free authentication and audit primitives."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
from pathlib import Path
import secrets
from typing import Any


@dataclass(frozen=True)
class TokenClaims:
    """Verified access-token claims."""

    subject: str
    scopes: tuple[str, ...]
    expires_at: int


class TokenIssuer:
    """Issue and verify compact HMAC-signed access tokens."""

    def __init__(self, secret: str) -> None:
        if len(secret) < 32:
            raise ValueError("Authentication secret must be at least 32 characters")
        self.secret = secret.encode("utf-8")

    def issue(
        self,
        subject: str,
        scopes: tuple[str, ...] = (),
        *,
        ttl: timedelta = timedelta(hours=1),
    ) -> str:
        payload = {
            "sub": subject,
            "scopes": list(scopes),
            "exp": int((datetime.now(timezone.utc) + ttl).timestamp()),
            "nonce": secrets.token_hex(8),
        }
        encoded = _encode(payload)
        signature = hmac.new(self.secret, encoded, hashlib.sha256).digest()
        return f"{encoded.decode()}.{_b64encode(signature)}"

    def verify(self, token: str) -> TokenClaims:
        """Verify signature and expiry, then return claims."""

        try:
            encoded, signature_text = token.split(".", maxsplit=1)
            expected = hmac.new(
                self.secret,
                encoded.encode(),
                hashlib.sha256,
            ).digest()
            signature = _b64decode(signature_text)
            if not hmac.compare_digest(signature, expected):
                raise ValueError("invalid signature")

            payload = json.loads(_b64decode(encoded))
            if int(payload["exp"]) <= int(datetime.now(timezone.utc).timestamp()):
                raise PermissionError("Access token expired")

            return TokenClaims(
                subject=str(payload["sub"]),
                scopes=tuple(str(scope) for scope in payload.get("scopes", [])),
                expires_at=int(payload["exp"]),
            )
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            raise PermissionError("Invalid access token") from error


class AuthorizationPolicy:
    """Check that verified claims contain a required scope."""

    @staticmethod
    def require(claims: TokenClaims, scope: str) -> None:
        if scope not in claims.scopes:
            raise PermissionError(f"Missing required scope: {scope}")


class AuditLogger:
    """Append structured audit records without storing credential values."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        action: str,
        subject: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        safe_metadata = {
            key: value
            for key, value in (metadata or {}).items()
            if not any(secret in key.lower() for secret in ("key", "token", "secret", "password"))
        }
        event = {
            "action": action,
            "subject": subject,
            "metadata": safe_metadata,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, sort_keys=True))
            stream.write("\n")


def _encode(payload: dict[str, Any]) -> bytes:
    return _b64encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()).encode()


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))