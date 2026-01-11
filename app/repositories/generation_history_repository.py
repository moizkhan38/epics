from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.generation_history import GenerationHistory
from app.repositories.base_repository import BaseRepository


class GenerationHistoryRepository(BaseRepository[GenerationHistory]):
    """Repository for GenerationHistory model"""

    def __init__(self, db: AsyncSession):
        super().__init__(GenerationHistory, db)

    async def get_by_project_id(
        self,
        project_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[GenerationHistory]:
        """Get all generation histories for a project"""
        result = await self.db.execute(
            select(GenerationHistory)
            .where(GenerationHistory.project_id == project_id)
            .order_by(GenerationHistory.version.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_latest_version(self, project_id: int) -> int:
        """Get the latest version number for a project"""
        result = await self.db.execute(
            select(func.max(GenerationHistory.version))
            .where(GenerationHistory.project_id == project_id)
        )
        max_version = result.scalar_one_or_none()
        return max_version if max_version is not None else 0

    async def get_with_epics(self, history_id: int) -> GenerationHistory | None:
        """Get generation history with its epics and user stories"""
        result = await self.db.execute(
            select(GenerationHistory)
            .where(GenerationHistory.id == history_id)
            .options(
                selectinload(GenerationHistory.epics)
                .selectinload("user_stories")
            )
        )
        return result.scalar_one_or_none()

    async def approve_generation(
        self,
        history_id: int,
        approved_at: str
    ) -> GenerationHistory | None:
        """Mark a generation as approved"""
        return await self.update(
            history_id,
            status="approved",
            approved_at=approved_at
        )

    async def reject_generation(
        self,
        history_id: int,
        rejection_reason: str
    ) -> GenerationHistory | None:
        """Mark a generation as rejected"""
        return await self.update(
            history_id,
            status="rejected",
            rejection_reason=rejection_reason
        )
