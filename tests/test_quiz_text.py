from fastapi.testclient import TestClient

from app.main import app
from app.services.quiz_generation_service import QuizGenerationService


client = TestClient(app)


def auth_headers() -> dict[str, str]:
    return {"X-Internal-Api-Key": "test-internal-key"}


def fake_question_payloads(self, source_text: str, difficulty: str) -> list[dict]:
    return [
        {
            "question": f"테스트 문제 {index}입니다.",
            "options": ["정답", "오답 1", "오답 2", "오답 3"],
            "answer_index": 0,
            "explanation": "테스트용 해설입니다.",
        }
        for index in range(1, 4)
    ]


def test_generate_text_quiz_returns_three_korean_multiple_choice_questions(
    monkeypatch,
) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")
    monkeypatch.setattr(
        QuizGenerationService,
        "_generate_question_payloads",
        fake_question_payloads,
    )
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


def test_generate_text_quiz_uses_normalized_content(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")
    captured = {}

    def capture_question_payloads(self, source_text: str, difficulty: str) -> list[dict]:
        captured["source_text"] = source_text
        return fake_question_payloads(self, source_text, difficulty)

    monkeypatch.setattr(
        QuizGenerationService,
        "_generate_question_payloads",
        capture_question_payloads,
    )

    content = (
        "  FastAPI는   API 서버를 빠르게 만들 수 있는 프레임워크입니다.\n\n"
        "FastAPI는   API 서버를 빠르게 만들 수 있는 프레임워크입니다.\n"
        "Pydantic을 사용하면 요청과 응답을 구조적으로 검증할 수 있습니다. " * 4
    )

    response = client.post(
        "/ai/quiz/generate/text",
        headers=auth_headers(),
        json={"content": content, "difficulty": "beginner"},
    )

    assert response.status_code == 200
    assert "  " not in captured["source_text"]
