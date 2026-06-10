from fastapi.testclient import TestClient

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
