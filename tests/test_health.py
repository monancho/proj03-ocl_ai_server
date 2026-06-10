from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app


client = TestClient(app)


def test_health_without_auth() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "ai-server",
        "version": "0.1.0",
    }
    assert response.headers["X-Request-Id"]


def test_health_preserves_request_id_header() -> None:
    response = client.get("/health", headers={"X-Request-Id": "test-request-id"})

    assert response.status_code == 200
    assert response.headers["X-Request-Id"] == "test-request-id"


def test_ready_returns_ready_when_required_settings_exist(monkeypatch) -> None:
    def fake_settings() -> Settings:
        return Settings(
            AI_SERVER_API_KEY="test-internal-key",
            OPENAI_API_KEY="test-openai-key",
        )

    monkeypatch.setattr("app.api.health.get_settings", fake_settings)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_ready_returns_503_when_required_settings_missing(monkeypatch) -> None:
    def fake_settings() -> Settings:
        return Settings(
            AI_SERVER_API_KEY=None,
            OPENAI_API_KEY=None,
        )

    monkeypatch.setattr("app.api.health.get_settings", fake_settings)

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "SERVICE_NOT_READY"
