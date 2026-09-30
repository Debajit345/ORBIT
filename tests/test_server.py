from fastapi.testclient import TestClient

from app.main import app
from app import main as main_module
from orbit.security import TokenIssuer


def test_health_endpoint() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "orbit"}


def test_ready_endpoint_reports_checks() -> None:
    response = TestClient(app).get("/ready")

    assert response.status_code == 200
    assert "Python" in response.json()["checks"]
    assert response.json()["status"] in {"ready", "not_ready"}


def test_authenticated_diagnostics_requires_scope(monkeypatch) -> None:
    main_module.auth_issuer = TokenIssuer("x" * 32)
    client = TestClient(app)
    token = main_module.auth_issuer.issue("operator", ("admin:read",))

    response = client.get(
        "/admin/diagnostics",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "Python" in response.json()["checks"]