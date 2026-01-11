from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

from app.schemas.common import TimestampSchema


class ProjectBase(BaseModel):
    """Base schema for Project"""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str = Field(..., min_length=10, description="Project description")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    pass


class ProjectResponse(ProjectBase, TimestampSchema):
    """Schema for project response"""

    id: int = Field(..., description="Project ID")

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """Schema for paginated project list response"""

    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
