from fastapi import APIRouter, Depends

from app.core.auth import verify_internal_api_key
from app.schemas.quiz import QuizGenerateResponse, TextQuizGenerateRequest
from app.services.quiz_generation_service import QuizGenerationService


router = APIRouter(prefix="/ai/quiz", dependencies=[Depends(verify_internal_api_key)])


@router.post("/generate/text", response_model=QuizGenerateResponse)
async def generate_text_quiz(request: TextQuizGenerateRequest) -> QuizGenerateResponse:
    data = QuizGenerationService().generate_from_text(
        content=request.content,
        difficulty=request.difficulty,
    )
    return QuizGenerateResponse(data=data)
