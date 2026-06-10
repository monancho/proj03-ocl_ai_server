from typing import Literal

from pydantic import BaseModel, Field, model_validator


Difficulty = Literal["beginner", "intermediate", "advanced"]


class TextQuizGenerateRequest(BaseModel):
    content: str
    difficulty: str


class QuizSource(BaseModel):
    type: Literal["text", "web", "youtube"]
    title: str | None = None
    url: str | None = None
    warning: str | None = None


class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(min_length=4, max_length=4)
    answer_index: int
    explanation: str

    @model_validator(mode="after")
    def validate_answer_index(self) -> "QuizQuestion":
        if self.answer_index != 0:
            raise ValueError("answer_index must be 0")
        return self


class QuizUsage(BaseModel):
    question_count: int
    input_chars: int


class QuizGenerateData(BaseModel):
    source: QuizSource
    questions: list[QuizQuestion] = Field(min_length=3, max_length=3)
    usage: QuizUsage


class QuizGenerateResponse(BaseModel):
    success: bool = True
    data: QuizGenerateData
