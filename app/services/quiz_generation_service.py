from app.core.config import Settings, get_settings
from app.core.errors import ApiError
from app.schemas.quiz import QuizGenerateData, QuizQuestion, QuizSource, QuizUsage


ALLOWED_DIFFICULTIES = {"beginner", "intermediate", "advanced"}
MIN_SOURCE_CHARS = 100


class QuizGenerationService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def generate_from_text(self, content: str, difficulty: str) -> QuizGenerateData:
        source_text = content.strip()
        self._validate_text_input(source_text, difficulty)

        questions = [
            QuizQuestion(
                question=f"입력한 학습 내용에서 확인해야 할 핵심 개념 {index}은 무엇인가요?",
                options=[
                    f"학습 내용의 핵심 개념 {index}",
                    f"관련 없는 보기 {index}-1",
                    f"관련 없는 보기 {index}-2",
                    f"관련 없는 보기 {index}-3",
                ],
                answer_index=0,
                explanation="입력된 본문을 바탕으로 핵심 내용을 확인하도록 구성한 문제입니다.",
            )
            for index in range(1, 4)
        ]

        return QuizGenerateData(
            source=QuizSource(type="text"),
            questions=questions,
            usage=QuizUsage(question_count=3, input_chars=len(source_text)),
        )

    def _validate_text_input(self, content: str, difficulty: str) -> None:
        if difficulty not in ALLOWED_DIFFICULTIES:
            raise ApiError(400, "DIFFICULTY_INVALID", "지원하지 않는 난이도입니다.")
        if len(content) < MIN_SOURCE_CHARS:
            raise ApiError(400, "SOURCE_TEXT_TOO_SHORT", "문제 생성을 위한 내용이 부족합니다.")
        if len(content) > self.settings.max_source_chars:
            raise ApiError(400, "SOURCE_TEXT_TOO_LONG", "문제 생성을 위한 내용이 너무 깁니다.")
