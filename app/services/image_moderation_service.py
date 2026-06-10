import base64
from pathlib import Path
from typing import Any

from openai import OpenAI, OpenAIError

from app.core.config import Settings, get_settings
from app.core.errors import ApiError
from app.schemas.image import ImageModerationData


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
EXTENSION_TO_CONTENT_TYPE = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}
BLOCKED_IMAGE_MESSAGE = "업로드할 수 없는 이미지입니다. 다른 이미지를 선택해 주세요."
REVIEW_IMAGE_MESSAGE = "검토가 필요한 이미지입니다."
HIGH_RISK_SCORE_THRESHOLD = 0.8
HIGH_RISK_CATEGORIES = {
    "sexual/minors",
    "sexual_minors",
    "violence/graphic",
    "violence_graphic",
    "self-harm/instructions",
    "self_harm_instructions",
    "hate/threatening",
    "hate_threatening",
}


class ImageModerationService:
    def __init__(
        self,
        settings: Settings | None = None,
        client: Any | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._client = client

    async def moderate(
        self, filename: str | None, content_type: str | None, data: bytes
    ) -> ImageModerationData:
        self._validate_image(filename, content_type, data)
        result = self._moderate_with_openai(content_type or "image/png", data)
        return self._map_moderation_result(result)

    def _moderate_with_openai(self, content_type: str, data: bytes) -> Any:
        client = self._get_openai_client()
        data_url = self._to_data_url(content_type, data)
        try:
            return client.moderations.create(
                model=self.settings.image_moderation_model,
                input=[
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url},
                    }
                ],
                timeout=self.settings.request_timeout_seconds,
            )
        except OpenAIError as exc:
            raise ApiError(
                502,
                "IMAGE_MODERATION_FAILED",
                "이미지 검사 중 오류가 발생했습니다.",
            ) from exc

    def _map_moderation_result(self, response: Any) -> ImageModerationData:
        if not getattr(response, "results", None):
            raise ApiError(
                502,
                "IMAGE_MODERATION_FAILED",
                "이미지 검사 중 오류가 발생했습니다.",
            )

        result = response.results[0]
        categories = self._flagged_categories(getattr(result, "categories", None))
        category_scores = self._category_scores(getattr(result, "category_scores", None))
        flagged = bool(getattr(result, "flagged", False))

        if not flagged:
            return ImageModerationData(
                allowed=True,
                risk_level="low",
                action="allow",
                categories=[],
                message=None,
            )

        risk_level = (
            "high"
            if self._is_high_risk(categories, category_scores)
            else "medium"
        )
        action = "block" if risk_level == "high" else "review"
        return ImageModerationData(
            allowed=False,
            risk_level=risk_level,
            action=action,
            categories=categories,
            message=BLOCKED_IMAGE_MESSAGE if action == "block" else REVIEW_IMAGE_MESSAGE,
        )

    def _flagged_categories(self, categories: Any) -> list[str]:
        if categories is None:
            return []
        raw = categories.model_dump() if hasattr(categories, "model_dump") else vars(categories)
        return [name for name, flagged in raw.items() if flagged]

    def _category_scores(self, category_scores: Any) -> dict[str, float]:
        if category_scores is None:
            return {}
        raw = (
            category_scores.model_dump()
            if hasattr(category_scores, "model_dump")
            else vars(category_scores)
        )
        return {
            name: float(score)
            for name, score in raw.items()
            if isinstance(score, int | float)
        }

    def _is_high_risk(
        self,
        categories: list[str],
        category_scores: dict[str, float],
    ) -> bool:
        if any(category in HIGH_RISK_CATEGORIES for category in categories):
            return True
        return max(category_scores.values() or [0.0]) >= HIGH_RISK_SCORE_THRESHOLD

    def _to_data_url(self, content_type: str, data: bytes) -> str:
        encoded = base64.b64encode(data).decode("ascii")
        return f"data:{content_type};base64,{encoded}"

    def _get_openai_client(self) -> Any:
        if self._client is not None:
            return self._client
        if not self.settings.openai_api_key:
            raise ApiError(
                502,
                "IMAGE_MODERATION_FAILED",
                "이미지 검사 중 오류가 발생했습니다.",
            )
        self._client = OpenAI(api_key=self.settings.openai_api_key)
        return self._client

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
        if EXTENSION_TO_CONTENT_TYPE[extension] != content_type:
            raise ApiError(415, "IMAGE_TYPE_NOT_ALLOWED", "지원하지 않는 이미지 형식입니다.")
        if self._detect_image_type(data) != content_type:
            raise ApiError(415, "IMAGE_TYPE_NOT_ALLOWED", "지원하지 않는 이미지 형식입니다.")

    def _detect_image_type(self, data: bytes) -> str | None:
        if data.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        if data.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            return "image/webp"
        return None
