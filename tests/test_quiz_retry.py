from app.schemas.quiz import QuizSource
from app.services.quiz_generation_service import QuizGenerationService


def test_quiz_generation_retries_once_after_invalid_schema() -> None:
    service = QuizGenerationService()
    calls = {"count": 0}

    def flaky_generator(source_text: str, difficulty: str) -> list[dict]:
        calls["count"] += 1
        if calls["count"] == 1:
            return [
                {
                    "question": "첫 번째 시도는 정답 위치가 잘못된 문제입니다.",
                    "options": ["오답", "정답", "오답", "오답"],
                    "answer_index": 1,
                    "explanation": "잘못된 응답입니다.",
                }
            ]
        return [
            {
                "question": f"재시도 후 생성된 문제 {index}입니다.",
                "options": ["정답", "오답 1", "오답 2", "오답 3"],
                "answer_index": 0,
                "explanation": "정답은 항상 첫 번째 보기입니다.",
            }
            for index in range(1, 4)
        ]

    data = service._generate_with_retry(
        source_text="FastAPI와 Pydantic을 사용하면 API 요청과 응답을 구조적으로 검증할 수 있습니다. " * 5,
        difficulty="beginner",
        source=QuizSource(type="text"),
        generator=flaky_generator,
    )

    assert calls["count"] == 2
    assert len(data.questions) == 3
    assert all(question.answer_index == 0 for question in data.questions)
