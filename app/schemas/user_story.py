from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

from app.schemas.common import TimestampSchema


class TestCase(BaseModel):
    """Schema for a test case"""

    id: str = Field(..., description="Test case ID")
    title: str = Field(..., description="Test case title")
    description: str = Field(..., description="Test case description")
    steps: List[str] = Field(..., description="Test steps")
    expected_result: str = Field(..., description="Expected result")
    priority: str = Field(default="medium", description="Test priority")


class UserStoryBase(BaseModel):
    """Base schema for User Story"""

    title: str = Field(..., min_length=1, max_length=500, description="User story title")
    description: str = Field(..., min_length=10, description="User story description")
    acceptance_criteria: Optional[str] = Field(None, description="Acceptance criteria")
    story_points: Optional[int] = Field(None, ge=1, le=100, description="Story points estimate")
    priority: str = Field(default="medium", description="Priority level")


class UserStoryCreate(UserStoryBase):
    """Schema for creating a user story"""

    epic_id: int = Field(..., description="Associated epic ID")
    test_cases: Optional[List[TestCase]] = Field(None, description="Associated test cases")


class UserStoryResponse(UserStoryBase, TimestampSchema):
    """Schema for user story response"""

    id: int = Field(..., description="User story ID")
    epic_id: int = Field(..., description="Associated epic ID")
    is_approved: bool = Field(..., description="Approval status")
    test_cases: Optional[List[TestCase]] = Field(None, description="Associated test cases")

    model_config = ConfigDict(from_attributes=True)
