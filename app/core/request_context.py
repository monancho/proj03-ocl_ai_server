import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request, Response


REQUEST_ID_HEADER = "X-Request-Id"
logger = logging.getLogger("ai_server.request")


async def request_context_middleware(request: Request, call_next) -> Response:
    request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
    start = perf_counter()

    response = await call_next(request)
    response.headers[REQUEST_ID_HEADER] = request_id

    elapsed_ms = round((perf_counter() - start) * 1000, 2)
    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "elapsed_ms": elapsed_ms,
        },
    )
    return response
