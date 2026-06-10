from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ai_endpoint_rejects_missing_api_key(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")

    response = client.post(
        "/ai/quiz/generate/text",
        json={"content": "학습 내용 " * 20, "difficulty": "beginner"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {"code": "INVALID_API_KEY", "message": "허용되지 않은 요청입니다."},
    }


def test_ai_endpoint_rejects_invalid_api_key(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")

    response = client.post(
        "/ai/quiz/generate/text",
        headers={"X-Internal-Api-Key": "wrong-key"},
        json={"content": "학습 내용 " * 20, "difficulty": "beginner"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_API_KEY"
