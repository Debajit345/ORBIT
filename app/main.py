"""ORBIT server entrypoint, health, and authenticated routes."""

import os

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from orbit.diagnostics import run_diagnostics
from orbit.security import AuthorizationPolicy, TokenIssuer


app = FastAPI(
    title="ORBIT",
    description="Local-first research and intelligence server",
    version="0.1.0",
)

_auth_secret = os.getenv("ORBIT_AUTH_SECRET")
auth_issuer = TokenIssuer(_auth_secret) if _auth_secret else None
bearer = HTTPBearer(auto_error=False)


class TokenRequest(BaseModel):
    """Local token issuance request."""

    subject: str
    scopes: tuple[str, ...] = ()


def require_claims(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
):
	"""Verify a bearer token or reject the request."""

	if auth_issuer is None:
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail="ORBIT_AUTH_SECRET is not configured",
		)

	if credentials is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Bearer token required",
		)

	try:
		return auth_issuer.verify(credentials.credentials)
	except PermissionError as error:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail=str(error),
		) from error


@app.get("/health")
def health() -> dict[str, str]:
    """Return a process-level liveness response."""

    return {"status": "ok", "service": "orbit"}


@app.post("/auth/token")
def issue_token(request: TokenRequest) -> dict[str, str]:
    """Issue a local token only when an operator configured a secret."""

    if auth_issuer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ORBIT_AUTH_SECRET is not configured",
        )

    return {"access_token": auth_issuer.issue(request.subject, request.scopes)}


@app.get("/admin/diagnostics")
def protected_diagnostics(claims=Depends(require_claims)) -> dict[str, object]:
    """Return diagnostics to callers with the admin:read scope."""

    try:
        AuthorizationPolicy.require(claims, "admin:read")
    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error

    return {
        "checks": {
            check.component: check.status
            for check in run_diagnostics()
        }
    }


@app.get("/ready")
def ready() -> dict[str, object]:
	"""Return readiness details from local, non-network diagnostics."""

	checks = run_diagnostics()
	blocking = {"Python", "Textual", "Database"}
	ready_checks = all(
		check.status not in {"ERROR", "MISSING"}
		for check in checks
		if check.component in blocking
	)

	return {
		"status": "ready" if ready_checks else "not_ready",
		"checks": {
			check.component: check.status for check in checks
		},
	}
