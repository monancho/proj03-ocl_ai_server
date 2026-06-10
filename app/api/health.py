from fastapi import APIRouter

from app.core.config import get_settings
from app.core.errors import ApiError


router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.service_name,
        "version": settings.version,
    }


@router.get("/ready")
async def ready() -> dict[str, str]:
    settings = get_settings()
    missing = []
    if not settings.ai_server_api_key:
        missing.append("AI_SERVER_API_KEY")
    if not settings.openai_api_key:
        missing.append("OPENAI_API_KEY")
    if not settings.ai_text_model:
        missing.append("AI_TEXT_MODEL")
    if not settings.image_moderation_model:
        missing.append("IMAGE_MODERATION_MODEL")

    if missing:
        raise ApiError(
            503,
            "SERVICE_NOT_READY",
            "필수 환경변수 설정이 완료되지 않았습니다.",
        )

    return {
        "status": "ready",
        "service": settings.service_name,
        "version": settings.version,
    }
