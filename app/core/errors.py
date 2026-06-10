from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiError(HTTPException):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message},
        )


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": {"code": code, "message": message}},
    )


async def api_error_handler(_request: Request, exc: ApiError) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    return error_response(
        exc.status_code,
        str(detail.get("code", "INTERNAL_ERROR")),
        str(detail.get("message", "요청 처리 중 오류가 발생했습니다.")),
    )


async def validation_error_handler(
    _request: Request, _exc: RequestValidationError
) -> JSONResponse:
    return error_response(422, "REQUEST_VALIDATION_ERROR", "요청 형식이 올바르지 않습니다.")
