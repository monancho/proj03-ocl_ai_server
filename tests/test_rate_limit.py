from fastapi.testclient import TestClient

from app.core.rate_limit import usage_guard
from app.main import app
from app.services.quiz_generation_service import QuizGenerationService


client = TestClient(app)


def auth_headers() -> dict[str, str]:
    return {"X-Internal-Api-Key": "test-internal-key"}


def fake_question_payloads(self, source_text: str, difficulty: str) -> list[dict]:
    return [
        {
            "question": f"보호 제한 테스트 문제 {index}입니다.",
            "options": ["정답", "오답 1", "오답 2", "오답 3"],
            "answer_index": 0,
            "explanation": "테스트용 해설입니다.",
        }
        for index in range(1, 4)
    ]


def test_ai_daily_usage_limit_returns_429(monkeypatch) -> None:
    usage_guard.reset()
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")
    monkeypatch.setenv("AI_DAILY_REQUEST_LIMIT", "1")
    monkeypatch.setenv("AI_RATE_LIMIT_PER_MINUTE", "100")
    monkeypatch.setattr(
        QuizGenerationService,
        "_generate_question_payloads",
        fake_question_payloads,
    )

    payload = {
        "content": "FastAPI와 Pydantic을 사용하면 API 요청과 응답을 구조적으로 검증할 수 있습니다. " * 5,
        "difficulty": "beginner",
    }

    first = client.post(
        "/ai/quiz/generate/text",
        headers=auth_headers(),
        json=payload,
    )
    second = client.post(
        "/ai/quiz/generate/text",
        headers=auth_headers(),
        json=payload,
    )

    usage_guard.reset()
    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["error"]["code"] == "AI_DAILY_USAGE_LIMIT_EXCEEDED"
