from types import SimpleNamespace

import anyio

from app.core.config import Settings
from app.services.image_moderation_service import ImageModerationService
from app.services.quiz_generation_service import QuizGenerationService, QuizQuestionSet


class FakeParsedMessage:
    def __init__(self, parsed):
        self.parsed = parsed


class FakeChoice:
    def __init__(self, parsed):
        self.message = FakeParsedMessage(parsed)


class FakeChatCompletions:
    def __init__(self):
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        parsed = QuizQuestionSet(
            questions=[
                {
                    "question": f"OpenAI 테스트 문제 {index}입니다.",
                    "options": ["정답", "오답 1", "오답 2", "오답 3"],
                    "answer_index": 0,
                    "explanation": "정답은 첫 번째 보기입니다.",
                }
                for index in range(1, 4)
            ]
        )
        return SimpleNamespace(choices=[FakeChoice(parsed)])


class FakeOpenAIClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=FakeChatCompletions())


def test_quiz_generation_uses_openai_structured_output_client() -> None:
    client = FakeOpenAIClient()
    service = QuizGenerationService(
        settings=Settings(OPENAI_API_KEY="test-key"),
        client=client,
    )

    data = service.generate_from_text(
        content="FastAPI와 Pydantic을 사용하면 API 요청과 응답을 구조적으로 검증할 수 있습니다. " * 5,
        difficulty="beginner",
    )

    call = client.chat.completions.calls[0]
    assert call["response_format"] is QuizQuestionSet
    assert call["model"] == service.settings.ai_text_model
    assert len(data.questions) == 3
    assert all(question.answer_index == 0 for question in data.questions)


class FakeModerations:
    def __init__(self, flagged: bool):
        self.flagged = flagged
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            results=[
                SimpleNamespace(
                    flagged=self.flagged,
                    categories=SimpleNamespace(violence=self.flagged),
                    category_scores=SimpleNamespace(violence=0.9 if self.flagged else 0.0),
                )
            ]
        )


class FakeModerationClient:
    def __init__(self, flagged: bool):
        self.moderations = FakeModerations(flagged)


def test_image_moderation_uses_openai_multimodal_input() -> None:
    client = FakeModerationClient(flagged=True)
    service = ImageModerationService(
        settings=Settings(OPENAI_API_KEY="test-key"),
        client=client,
    )

    result = anyio.run(
        service.moderate,
        "sample.png",
        "image/png",
        b"\x89PNG\r\n\x1a\nfake-image",
    )

    call = client.moderations.calls[0]
    assert call["model"] == service.settings.image_moderation_model
    assert call["input"][0]["type"] == "image_url"
    assert call["input"][0]["image_url"]["url"].startswith("data:image/png;base64,")
    assert result.allowed is False
    assert result.risk_level == "high"
    assert result.action == "block"
    assert result.message is not None
