from fastapi.testclient import TestClient

from app.main import app
from app.services.quiz_generation_service import QuizGenerationService
from app.services.youtube_extract_service import YouTubeTranscriptService


client = TestClient(app)


def auth_headers() -> dict[str, str]:
    return {"X-Internal-Api-Key": "test-internal-key"}


def fake_question_payloads(self, source_text: str, difficulty: str) -> list[dict]:
    return [
        {
            "question": f"유튜브 테스트 문제 {index}입니다.",
            "options": ["정답", "오답 1", "오답 2", "오답 3"],
            "answer_index": 0,
            "explanation": "테스트용 해설입니다.",
        }
        for index in range(1, 4)
    ]


def test_youtube_quiz_uses_transcript_stub(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")
    monkeypatch.setattr(
        QuizGenerationService,
        "_generate_question_payloads",
        fake_question_payloads,
    )

    async def fake_transcript(self, video_id: str) -> str:
        return "FastAPI와 Pydantic을 사용하면 API 요청과 응답을 구조적으로 검증할 수 있습니다. " * 5

    monkeypatch.setattr(YouTubeTranscriptService, "_get_transcript_text", fake_transcript)

    response = client.post(
        "/ai/quiz/generate/youtube",
        headers=auth_headers(),
        json={"url": "https://www.youtube.com/watch?v=VIDEO_ID", "difficulty": "advanced"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["data"]["source"]["type"] == "youtube"
    assert body["data"]["source"]["url"] == "https://www.youtube.com/watch?v=VIDEO_ID"
    assert len(body["data"]["questions"]) == 3


def test_youtube_quiz_rejects_invalid_url(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")

    response = client.post(
        "/ai/quiz/generate/youtube",
        headers=auth_headers(),
        json={"url": "https://example.com/watch?v=VIDEO_ID", "difficulty": "beginner"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "YOUTUBE_URL_INVALID"


def test_youtube_quiz_returns_transcript_not_found(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")

    async def empty_transcript(self, video_id: str) -> str:
        return ""

    monkeypatch.setattr(YouTubeTranscriptService, "_get_transcript_text", empty_transcript)

    response = client.post(
        "/ai/quiz/generate/youtube",
        headers=auth_headers(),
        json={"url": "https://youtu.be/VIDEO_ID", "difficulty": "beginner"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "YOUTUBE_TRANSCRIPT_NOT_FOUND"


def test_youtube_quiz_returns_transcript_warning(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")
    monkeypatch.setattr(
        QuizGenerationService,
        "_generate_question_payloads",
        fake_question_payloads,
    )

    async def english_auto_transcript(self, video_id: str):
        return (
            "FastAPI and Pydantic help validate API requests and responses. " * 5,
            ["YOUTUBE_EN_TRANSCRIPT_USED", "YOUTUBE_AUTO_TRANSCRIPT_USED"],
        )

    monkeypatch.setattr(
        YouTubeTranscriptService,
        "_get_transcript_text",
        english_auto_transcript,
    )

    response = client.post(
        "/ai/quiz/generate/youtube",
        headers=auth_headers(),
        json={"url": "https://youtu.be/VIDEO_ID", "difficulty": "beginner"},
    )

    assert response.status_code == 200
    assert (
        response.json()["data"]["source"]["warning"]
        == "YOUTUBE_EN_TRANSCRIPT_USED,YOUTUBE_AUTO_TRANSCRIPT_USED"
    )
