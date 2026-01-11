from sqlalchemy import String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from typing import List

from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    """Model for storing project descriptions and their embeddings"""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Vector embedding for similarity search
    description_embedding: Mapped[Vector] = mapped_column(
        Vector(384),  # Dimension for all-MiniLM-L6-v2
        nullable=True
    )

    # Relationships
    epics: Mapped[List["Epic"]] = relationship(
        "Epic",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    generation_histories: Mapped[List["GenerationHistory"]] = relationship(
        "GenerationHistory",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "ix_projects_description_embedding",
            "description_embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"description_embedding": "vector_cosine_ops"}
        ),
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}')>"
