from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

from app.schemas.common import TimestampSchema
from app.schemas.user_story import UserStoryResponse


class EpicBase(BaseModel):
    """Base schema for Epic"""

    title: str = Field(..., min_length=1, max_length=500, description="Epic title")
    description: str = Field(..., min_length=10, description="Epic description")
    story_points: Optional[int] = Field(None, ge=1, le=1000, description="Total story points")
    priority: str = Field(default="medium", description="Priority level")


class EpicCreate(EpicBase):
    """Schema for creating an epic"""

    project_id: int = Field(..., description="Associated project ID")
    generation_history_id: int = Field(..., description="Generation history ID")


class EpicResponse(EpicBase, TimestampSchema):
    """Schema for epic response"""

    id: int = Field(..., description="Epic ID")
    project_id: int = Field(..., description="Associated project ID")
    generation_history_id: int = Field(..., description="Generation history ID")
    is_approved: bool = Field(..., description="Approval status")
    user_stories: List[UserStoryResponse] = Field(default_factory=list, description="Associated user stories")

    model_config = ConfigDict(from_attributes=True)


class EpicApproval(BaseModel):
    """Schema for approving/rejecting an epic"""

    epic_id: int = Field(..., description="Epic ID")
    is_approved: bool = Field(..., description="Approval status")
    feedback: Optional[str] = Field(None, description="Optional feedback")
