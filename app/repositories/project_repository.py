from typing import List, Dict, Any
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.base_repository import BaseRepository
from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project model"""

    def __init__(self, db: AsyncSession):
        super().__init__(Project, db)

    async def create_with_embedding(
        self,
        name: str,
        description: str,
        embedding: List[float]
    ) -> Project:
        """Create a project with embedding vector"""
        project = await self.create(
            name=name,
            description=description,
            description_embedding=embedding
        )
        return project

    async def find_similar_projects(
        self,
        embedding: List[float],
        limit: int = None,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar projects using vector similarity search

        Args:
            embedding: Query embedding vector
            limit: Maximum number of results
            threshold: Minimum similarity threshold

        Returns:
            List of similar projects with similarity scores
        """
        if limit is None:
            limit = settings.MAX_SIMILAR_PROJECTS
        if threshold is None:
            threshold = settings.SIMILARITY_THRESHOLD

        # Convert embedding to PostgreSQL array format
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        # Use pgvector's cosine similarity operator
        query = text("""
            SELECT
                id,
                name,
                description,
                1 - (description_embedding <=> :embedding::vector) as similarity_score
            FROM projects
            WHERE description_embedding IS NOT NULL
                AND 1 - (description_embedding <=> :embedding::vector) >= :threshold
            ORDER BY description_embedding <=> :embedding::vector
            LIMIT :limit
        """)

        result = await self.db.execute(
            query,
            {
                "embedding": embedding_str,
                "threshold": threshold,
                "limit": limit
            }
        )

        similar_projects = []
        for row in result:
            similar_projects.append({
                "project_id": row.id,
                "name": row.name,
                "description": row.description,
                "similarity_score": float(row.similarity_score)
            })

        logger.info(
            "similar_projects_found",
            count=len(similar_projects),
            threshold=threshold
        )

        return similar_projects

    async def get_with_epics(self, project_id: int) -> Project | None:
        """Get project with its epics"""
        from app.models.epic import Epic
        from app.models.user_story import UserStory

        result = await self.db.execute(
            select(Project)
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
