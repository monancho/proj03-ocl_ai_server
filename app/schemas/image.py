from typing import Literal

from pydantic import BaseModel


RiskLevel = Literal["low", "medium", "high"]


class ImageModerationData(BaseModel):
    allowed: bool
    risk_level: RiskLevel
    categories: list[str]
    message: str | None = None


class ImageModerationResponse(BaseModel):
    success: bool = True
    data: ImageModerationData
