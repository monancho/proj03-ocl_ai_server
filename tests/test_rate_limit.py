from fastapi.testclient import TestClient
from types import SimpleNamespace

from app.core.rate_limit import usage_guard
from app.main import app
from app.services.image_moderation_service import ImageModerationService
from app.services.quiz_generation_service import QuizGenerationService


client = TestClient(app)
PNG_BYTES = b"\x89PNG\r\n\x1a\nnot-a-real-image-but-has-png-signature"


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


def fake_openai_moderation(self, content_type: str, data: bytes):
    return SimpleNamespace(
        results=[
            SimpleNamespace(
                flagged=False,
                categories=SimpleNamespace(),
                category_scores=SimpleNamespace(),
            )
        ]
    )


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


def test_image_moderation_is_excluded_from_daily_usage_limit(monkeypatch) -> None:
    usage_guard.reset()
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")
    monkeypatch.setenv("AI_DAILY_REQUEST_LIMIT", "1")
    monkeypatch.setenv("AI_RATE_LIMIT_PER_MINUTE", "100")
    monkeypatch.setattr(
        QuizGenerationService,
        "_generate_question_payloads",
        fake_question_payloads,
    )
    monkeypatch.setattr(
        ImageModerationService,
        "_moderate_with_openai",
        fake_openai_moderation,
    )

    payload = {
        "content": "FastAPI? Pydantic???ъ슜?섎㈃ API ?붿껌怨??묐떟??援ъ“?곸쑝濡?寃利앺븷 ???덉뒿?덈떎. " * 5,
        "difficulty": "beginner",
    }

    quiz = client.post(
        "/ai/quiz/generate/text",
        headers=auth_headers(),
        json=payload,
    )
    image = client.post(
        "/ai/image/moderate",
        headers=auth_headers(),
        files={"image": ("sample.png", PNG_BYTES, "image/png")},
    )

    usage_guard.reset()
    assert quiz.status_code == 200
    assert image.status_code == 200
    assert image.json()["data"]["action"] == "allow"
