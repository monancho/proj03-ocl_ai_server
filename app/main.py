from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api import health, image, quiz
from app.core.errors import ApiError, api_error_handler, validation_error_handler


app = FastAPI(title="Doodle & Quiz AI Server", version="0.1.0")
app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.include_router(health.router)
app.include_router(quiz.router)
app.include_router(image.router)
