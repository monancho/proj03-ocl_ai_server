from typing import Literal

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high"]
ModerationAction = Literal["allow", "review", "block"]


class ImageModerationData(BaseModel):
    allowed: bool = Field(description="자동 업로드 허용 여부")
    risk_level: RiskLevel = Field(description="이미지 위험도. low, medium, high 중 하나")
    action: ModerationAction = Field(
        description="후속 처리 정책. allow는 허용, review는 검토 필요, block은 차단입니다."
    )
    categories: list[str] = Field(description="OpenAI moderation에서 감지된 위험 카테고리")
    message: str | None = Field(default=None, description="사용자에게 표시할 일반 안내 메시지")


class ImageModerationResponse(BaseModel):
    success: bool = True
    data: ImageModerationData
