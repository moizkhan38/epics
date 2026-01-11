from sqlalchemy import String, Text, Integer, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from app.models.base import Base, TimestampMixin


class GenerationHistory(Base, TimestampMixin):
    """Model for tracking epic generation history and approval status"""

    __tablename__ = "generation_histories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",  # pending, approved, rejected
        nullable=False,
        index=True
    )

    # AI generation metadata
    prompt_used: Mapped[str] = mapped_column(Text, nullable=True)
    model_version: Mapped[str] = mapped_column(String(100), nullable=True)
    generation_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Similar projects found
    similar_projects: Mapped[dict] = mapped_column(JSON, nullable=True)

    # User feedback
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=True)
    approved_at: Mapped[str] = mapped_column(String(50), nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="generation_histories"
    )
    epics: Mapped[List["Epic"]] = relationship(
        "Epic",
        back_populates="generation_history",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<GenerationHistory(id={self.id}, project_id={self.project_id}, version={self.version}, status='{self.status}')>"
