from fastapi import APIRouter, Depends

from app.core.auth import verify_internal_api_key
from app.core.rate_limit import verify_ai_usage_limit
from app.schemas.quiz import (
    QuizGenerateResponse,
    TextQuizGenerateRequest,
    WebQuizGenerateRequest,
    YouTubeQuizGenerateRequest,
)
from app.services.quiz_generation_service import QuizGenerationService
from app.services.web_extract_service import WebExtractService
from app.services.youtube_extract_service import YouTubeTranscriptService


router = APIRouter(
    prefix="/ai/quiz",
    dependencies=[Depends(verify_internal_api_key), Depends(verify_ai_usage_limit)],
)


@router.post("/generate/text", response_model=QuizGenerateResponse)
async def generate_text_quiz(request: TextQuizGenerateRequest) -> QuizGenerateResponse:
    data = QuizGenerationService().generate_from_text(
        content=request.content,
        difficulty=request.difficulty,
    )
    return QuizGenerateResponse(data=data)


@router.post("/generate/web", response_model=QuizGenerateResponse)
async def generate_web_quiz(request: WebQuizGenerateRequest) -> QuizGenerateResponse:
    extracted = await WebExtractService().extract(request.url)
    data = QuizGenerationService().generate_from_web(
        content=extracted.text,
        difficulty=request.difficulty,
        title=extracted.title,
        url=request.url,
        warning=extracted.warning,
    )
    return QuizGenerateResponse(data=data)


@router.post("/generate/youtube", response_model=QuizGenerateResponse)
async def generate_youtube_quiz(request: YouTubeQuizGenerateRequest) -> QuizGenerateResponse:
    transcript = await YouTubeTranscriptService().extract(request.url)
    data = QuizGenerationService().generate_from_youtube(
        transcript=transcript.text,
        difficulty=request.difficulty,
        url=request.url,
        warning=transcript.warning,
    )
    return QuizGenerateResponse(data=data)
