import secrets

from fastapi import Header

from app.core.config import get_settings
from app.core.errors import ApiError


async def verify_internal_api_key(
    x_internal_api_key: str | None = Header(default=None, alias="X-Internal-Api-Key"),
) -> None:
    expected_key = get_settings().ai_server_api_key
    if not expected_key or not x_internal_api_key:
        raise ApiError(401, "INVALID_API_KEY", "허용되지 않은 요청입니다.")
    if not secrets.compare_digest(x_internal_api_key, expected_key):
        raise ApiError(401, "INVALID_API_KEY", "허용되지 않은 요청입니다.")
