from fastapi import APIRouter, Depends, File, UploadFile

from app.core.auth import verify_internal_api_key
from app.core.errors import ApiError
from app.schemas.image import ImageModerationResponse
from app.services.image_moderation_service import ImageModerationService


router = APIRouter(prefix="/ai/image", dependencies=[Depends(verify_internal_api_key)])


@router.post("/moderate", response_model=ImageModerationResponse)
async def moderate_image(image: UploadFile | None = File(default=None)) -> ImageModerationResponse:
    if image is None:
        raise ApiError(400, "IMAGE_FILE_MISSING", "이미지 파일이 필요합니다.")

    data = await image.read()
    result = await ImageModerationService().moderate(
        filename=image.filename,
        content_type=image.content_type,
        data=data,
    )
    return ImageModerationResponse(data=result)
