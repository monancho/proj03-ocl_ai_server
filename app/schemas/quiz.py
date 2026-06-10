from typing import Literal

from pydantic import BaseModel, Field, model_validator


Difficulty = Literal["beginner", "intermediate", "advanced"]


class TextQuizGenerateRequest(BaseModel):
    content: str = Field(
        examples=[
            "FastAPI는 Python 기반 API 서버를 빠르게 만들 수 있는 프레임워크입니다. Pydantic을 사용해 요청과 응답을 구조적으로 검증하고 Swagger UI를 자동 제공합니다."
        ],
        description="문제 생성에 사용할 학습 텍스트. 공백 정규화 후 100자 이상, 12,000자 이하를 권장합니다.",
    )
    difficulty: str = Field(
        examples=["beginner"],
        description="난이도. beginner, intermediate, advanced 중 하나를 사용합니다.",
    )


class WebQuizGenerateRequest(BaseModel):
    url: str = Field(
        examples=["https://example.com/article"],
        description="정적 HTML 본문을 추출할 http 또는 https URL입니다.",
    )
    difficulty: str = Field(
        examples=["intermediate"],
        description="난이도. beginner, intermediate, advanced 중 하나를 사용합니다.",
    )


class YouTubeQuizGenerateRequest(BaseModel):
    url: str = Field(
        examples=["https://www.youtube.com/watch?v=VIDEO_ID"],
        description="자막을 추출할 YouTube watch 또는 youtu.be URL입니다.",
    )
    difficulty: str = Field(
        examples=["advanced"],
        description="난이도. beginner, intermediate, advanced 중 하나를 사용합니다.",
    )


class QuizSource(BaseModel):
    type: Literal["text", "web", "youtube"] = Field(description="퀴즈 생성 입력 유형")
    title: str | None = Field(default=None, description="웹페이지 제목")
    url: str | None = Field(default=None, description="입력 URL")
    warning: str | None = Field(
        default=None,
        description="CONTENT_TRUNCATED 등 추출/전처리 warning code. 여러 개면 쉼표로 구분합니다.",
    )


class QuizQuestion(BaseModel):
    question: str = Field(description="한국어 4지선다 질문")
    options: list[str] = Field(
        min_length=4,
        max_length=4,
        description="보기 4개. 첫 번째 보기가 항상 정답입니다.",
    )
    answer_index: int = Field(
        description="정답 보기 index. MVP 규칙상 항상 0입니다.",
        examples=[0],
    )
    explanation: str = Field(description="정답이 맞는 이유를 설명하는 한국어 해설")

    @model_validator(mode="after")
    def validate_answer_index(self) -> "QuizQuestion":
        if self.answer_index != 0:
            raise ValueError("answer_index must be 0")
        return self


class QuizUsage(BaseModel):
    question_count: int = Field(description="생성된 문항 수", examples=[3])
    input_chars: int = Field(description="전처리 후 실제 문제 생성에 사용한 글자 수")


class QuizGenerateData(BaseModel):
    source: QuizSource
    questions: list[QuizQuestion] = Field(min_length=3, max_length=3)
    usage: QuizUsage


class QuizGenerateResponse(BaseModel):
    success: bool = True
    data: QuizGenerateData
