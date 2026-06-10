from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def auth_headers() -> dict[str, str]:
    return {"X-Internal-Api-Key": "test-internal-key"}


def test_generate_text_quiz_returns_three_korean_multiple_choice_questions(
    monkeypatch,
) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")
    content = "파이썬 FastAPI는 API 서버를 빠르게 만들 수 있는 프레임워크입니다. " * 5

    response = client.post(
        "/ai/quiz/generate/text",
        headers=auth_headers(),
        json={"content": content, "difficulty": "beginner"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["source"]["type"] == "text"
    assert body["data"]["usage"]["question_count"] == 3
    assert len(body["data"]["questions"]) == 3
    for question in body["data"]["questions"]:
        assert len(question["options"]) == 4
        assert question["answer_index"] == 0
        assert question["question"]
        assert question["explanation"]


def test_generate_text_quiz_rejects_invalid_difficulty(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")
    content = "파이썬 FastAPI는 API 서버를 빠르게 만들 수 있는 프레임워크입니다. " * 5

    response = client.post(
        "/ai/quiz/generate/text",
        headers=auth_headers(),
        json={"content": content, "difficulty": "expert"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "DIFFICULTY_INVALID"


def test_generate_text_quiz_rejects_too_long_content(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")

    response = client.post(
        "/ai/quiz/generate/text",
        headers=auth_headers(),
        json={"content": "가" * 12001, "difficulty": "beginner"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "SOURCE_TEXT_TOO_LONG"
