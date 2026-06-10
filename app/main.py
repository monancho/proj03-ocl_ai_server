from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api import health, image, quiz
from app.core.errors import ApiError, api_error_handler, validation_error_handler
from app.core.request_context import request_context_middleware


app = FastAPI(title="Doodle & Quiz AI Server", version="0.1.0")
app.middleware("http")(request_context_middleware)
app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.include_router(health.router)
app.include_router(quiz.router)
app.include_router(image.router)
