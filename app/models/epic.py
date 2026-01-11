from sqlalchemy import String, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from app.models.base import Base, TimestampMixin


class Epic(Base, TimestampMixin):
    """Model for storing epics"""

    __tablename__ = "epics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    generation_history_id: Mapped[int] = mapped_column(
        ForeignKey("generation_histories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    story_points: Mapped[int] = mapped_column(Integer, nullable=True)
    priority: Mapped[str] = mapped_column(String(50), default="medium")
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="epics")
    generation_history: Mapped["GenerationHistory"] = relationship(
        "GenerationHistory",
        back_populates="epics"
    )
    user_stories: Mapped[List["UserStory"]] = relationship(
        "UserStory",
        back_populates="epic",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Epic(id={self.id}, title='{self.title}')>"
