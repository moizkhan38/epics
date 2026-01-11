from sqlalchemy import String, Text, Integer, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class UserStory(Base, TimestampMixin):
    """Model for storing user stories"""

    __tablename__ = "user_stories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    epic_id: Mapped[int] = mapped_column(
        ForeignKey("epics.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    acceptance_criteria: Mapped[str] = mapped_column(Text, nullable=True)
    story_points: Mapped[int] = mapped_column(Integer, nullable=True)
    priority: Mapped[str] = mapped_column(String(50), default="medium")
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)

    # Test cases stored as JSON
    test_cases: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Relationships
    epic: Mapped["Epic"] = relationship("Epic", back_populates="user_stories")

    def __repr__(self) -> str:
        return f"<UserStory(id={self.id}, title='{self.title}')>"
