from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

from app.schemas.epic import EpicResponse


class SimilarProject(BaseModel):
    """Schema for similar project"""

    project_id: int = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    similarity_score: float = Field(..., ge=0, le=1, description="Cosine similarity score")


class GenerationRequest(BaseModel):
    """Schema for requesting epic generation"""

    project_name: str = Field(..., min_length=1, max_length=255, description="Project name")
    project_description: str = Field(..., min_length=50, description="Detailed project description")
    additional_context: Optional[str] = Field(None, description="Additional context or requirements")


class GenerationResponse(BaseModel):
    """Schema for generation response"""

    project_id: int = Field(..., description="Created project ID")
    generation_history_id: int = Field(..., description="Generation history ID")
    version: int = Field(..., description="Generation version")
    status: str = Field(..., description="Generation status")
    similar_projects: List[SimilarProject] = Field(default_factory=list, description="Similar projects found")
    epics: List[EpicResponse] = Field(..., description="Generated epics with user stories")
    message: str = Field(..., description="Status message")


class RegenerateRequest(BaseModel):
    """Schema for requesting regeneration"""

    project_id: int = Field(..., description="Project ID")
    generation_history_id: int = Field(..., description="Previous generation history ID")
    rejection_reason: str = Field(..., min_length=10, description="Reason for rejection")
    additional_instructions: Optional[str] = Field(None, description="Additional instructions for regeneration")


class ApprovalRequest(BaseModel):
    """Schema for approving/rejecting generation"""

    generation_history_id: int = Field(..., description="Generation history ID")
    is_approved: bool = Field(..., description="Approval status")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection if not approved")


class GenerationHistoryResponse(BaseModel):
    """Schema for generation history response"""

    id: int = Field(..., description="History ID")
    project_id: int = Field(..., description="Project ID")
    version: int = Field(..., description="Version number")
    status: str = Field(..., description="Status")
    similar_projects: Optional[List[SimilarProject]] = Field(None, description="Similar projects")
    rejection_reason: Optional[str] = Field(None, description="Rejection reason")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)
