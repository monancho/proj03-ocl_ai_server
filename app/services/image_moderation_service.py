from pathlib import Path

from app.core.config import Settings, get_settings
from app.core.errors import ApiError
from app.schemas.image import ImageModerationData


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
BLOCKED_IMAGE_MESSAGE = "업로드할 수 없는 이미지입니다. 다른 이미지를 선택해 주세요."


class ImageModerationService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def moderate(self, filename: str | None, content_type: str | None, data: bytes) -> ImageModerationData:
        self._validate_image(filename, content_type, data)
        return ImageModerationData(
            allowed=True,
            risk_level="low",
            categories=[],
            message=None,
        )

    def _validate_image(
        self, filename: str | None, content_type: str | None, data: bytes
    ) -> None:
        if not data:
            raise ApiError(400, "IMAGE_FILE_EMPTY", "빈 이미지 파일입니다.")

        max_size_bytes = self.settings.max_image_size_mb * 1024 * 1024
        if len(data) > max_size_bytes:
            raise ApiError(413, "IMAGE_FILE_TOO_LARGE", "이미지 파일 크기가 너무 큽니다.")

        extension = Path(filename or "").suffix.lower()
        if extension not in ALLOWED_IMAGE_EXTENSIONS or content_type not in ALLOWED_IMAGE_TYPES:
            raise ApiError(415, "IMAGE_TYPE_NOT_ALLOWED", "지원하지 않는 이미지 형식입니다.")
