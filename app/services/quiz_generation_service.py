from collections.abc import Callable
from typing import Any

from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field, ValidationError

from app.core.config import Settings, get_settings
from app.core.errors import ApiError
from app.schemas.quiz import QuizGenerateData, QuizQuestion, QuizSource, QuizUsage
from app.services.text_processing_service import truncate_learning_text


ALLOWED_DIFFICULTIES = {"beginner", "intermediate", "advanced"}
MIN_SOURCE_CHARS = 100
MAX_GENERATION_ATTEMPTS = 2


class QuizQuestionSet(BaseModel):
    questions: list[QuizQuestion] = Field(min_length=3, max_length=3)


class QuizGenerationService:
    def __init__(
        self,
        settings: Settings | None = None,
        client: Any | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._client = client

    def generate_from_text(self, content: str, difficulty: str) -> QuizGenerateData:
        source_text, was_truncated = truncate_learning_text(
            content,
            self.settings.max_source_chars,
        )
        if was_truncated:
            raise ApiError(400, "SOURCE_TEXT_TOO_LONG", "문제 생성을 위한 내용이 너무 깁니다.")
        self._validate_text_input(source_text, difficulty)
        return self._generate_with_retry(
            source_text=source_text,
            difficulty=difficulty,
            source=QuizSource(type="text"),
        )

    def generate_from_web(
        self,
        content: str,
        difficulty: str,
        title: str | None,
        url: str,
        warning: str | None,
    ) -> QuizGenerateData:
        source_text = content.strip()
        self._validate_extracted_source_text(source_text, difficulty)
        return self._generate_with_retry(
            source_text=source_text,
            difficulty=difficulty,
            source=QuizSource(type="web", title=title, url=url, warning=warning),
        )

    def generate_from_youtube(
        self,
        transcript: str,
        difficulty: str,
        url: str,
        warning: str | None,
    ) -> QuizGenerateData:
        source_text = transcript.strip()
        self._validate_extracted_source_text(source_text, difficulty)
        return self._generate_with_retry(
            source_text=source_text,
            difficulty=difficulty,
            source=QuizSource(type="youtube", url=url, warning=warning),
        )

    def _generate_with_retry(
        self,
        source_text: str,
        difficulty: str,
        source: QuizSource,
        generator: Callable[[str, str], list[dict]] | None = None,
    ) -> QuizGenerateData:
        question_generator = generator or self._generate_question_payloads
        last_error: Exception | None = None

        for _attempt in range(MAX_GENERATION_ATTEMPTS):
            try:
                payloads = question_generator(source_text, difficulty)
                questions = [QuizQuestion.model_validate(item) for item in payloads]
                self._validate_questions(questions)
                return QuizGenerateData(
                    source=source,
                    questions=questions,
                    usage=QuizUsage(
                        question_count=len(questions),
                        input_chars=len(source_text),
                    ),
                )
            except (ValidationError, ValueError, OpenAIError) as exc:
                last_error = exc

        raise ApiError(
            502,
            "QUIZ_GENERATION_FAILED",
            "문제 생성 중 오류가 발생했습니다.",
        ) from last_error

    def _generate_question_payloads(self, source_text: str, difficulty: str) -> list[dict]:
        client = self._get_openai_client()
        completion = client.chat.completions.parse(
            model=self.settings.ai_text_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "너는 한국어 교육용 퀴즈 생성기다. "
                        "반드시 제공된 학습 자료에서 근거를 찾을 수 있는 4지선다 객관식 3문항만 생성한다. "
                        "각 문항의 정답은 항상 첫 번째 보기이며 answer_index는 항상 0이다. "
                        "문제, 보기, 해설은 모두 한국어로 작성한다. "
                        "단순 암기 확인보다 학습자의 이해를 확인하는 문제를 우선한다. "
                        "3문항은 서로 다른 사고 유형으로 구성한다: 핵심 개념 이해, 관계나 이유 파악, 실제 적용 또는 오개념 구분. "
                        "보기는 너무 노골적인 오답을 피하고, 학습자가 헷갈릴 만하지만 명확히 구분되는 선택지로 만든다. "
                        "해설은 학습자에게 개념을 설명하듯 자연스럽게 작성하고 "
                        "'원문', '지문', '제공된 텍스트', '자료에 따르면' 같은 출처 지칭 표현은 쓰지 않는다."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"난이도: {difficulty}\n"
                        "아래 학습 자료를 바탕으로 한국어 4지선다 문제 3개를 만들어라.\n"
                        "각 문제는 question, options, answer_index, explanation을 포함해야 한다.\n"
                        "문항은 단순히 문장을 찾아 맞히는 방식이 아니라, "
                        "개념을 이해했는지 확인하는 방식으로 작성하라.\n"
                        "세 문제의 질문 방식과 초점은 서로 달라야 하며, "
                        "가능하면 정의 확인, 이유/관계 파악, 적용/판단 문제를 섞어라.\n"
                        "explanation은 정답이 왜 맞는지 한 문장으로 설명하되, "
                        "'원문', '지문', '제공된 텍스트', '자료에 따르면' 같은 표현은 쓰지 마라.\n\n"
                        f"학습 자료:\n{source_text}"
                    ),
                },
            ],
            response_format=QuizQuestionSet,
            max_completion_tokens=1800,
            timeout=self.settings.request_timeout_seconds,
        )
        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise ValueError("OpenAI response did not include parsed quiz data")
        return [question.model_dump() for question in parsed.questions]

    def _get_openai_client(self) -> Any:
        if self._client is not None:
            return self._client
        if not self.settings.openai_api_key:
            raise ApiError(
                502,
                "QUIZ_GENERATION_FAILED",
                "문제 생성 중 오류가 발생했습니다.",
            )
        self._client = OpenAI(api_key=self.settings.openai_api_key)
        return self._client

    def _validate_questions(self, questions: list[QuizQuestion]) -> None:
        if len(questions) != 3:
            raise ValueError("quiz generation must return exactly 3 questions")
        for question in questions:
            if len(question.options) != 4:
                raise ValueError("each question must return exactly 4 options")
            if question.answer_index != 0:
                raise ValueError("answer_index must be 0")

    def _validate_text_input(self, content: str, difficulty: str) -> None:
        self._validate_extracted_source_text(content, difficulty)

    def _validate_extracted_source_text(self, content: str, difficulty: str) -> None:
        if difficulty not in ALLOWED_DIFFICULTIES:
            raise ApiError(400, "DIFFICULTY_INVALID", "지원하지 않는 난이도입니다.")
        if len(content) < MIN_SOURCE_CHARS:
            raise ApiError(400, "SOURCE_TEXT_TOO_SHORT", "문제 생성을 위한 내용이 부족합니다.")
