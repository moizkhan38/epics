from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.epic import Epic
from app.repositories.base_repository import BaseRepository


class EpicRepository(BaseRepository[Epic]):
    """Repository for Epic model"""

    def __init__(self, db: AsyncSession):
        super().__init__(Epic, db)

    async def get_by_project_id(self, project_id: int) -> List[Epic]:
        """Get all epics for a project"""
        result = await self.db.execute(
            select(Epic)
            .where(Epic.project_id == project_id)
            .options(selectinload(Epic.user_stories))
        )
        return list(result.scalars().all())

    async def get_by_generation_history_id(self, history_id: int) -> List[Epic]:
        """Get all epics for a generation history"""
        result = await self.db.execute(
            select(Epic)
            .where(Epic.generation_history_id == history_id)
            .options(selectinload(Epic.user_stories))
        )
        return list(result.scalars().all())

    async def get_with_stories(self, epic_id: int) -> Epic | None:
        """Get epic with its user stories"""
        result = await self.db.execute(
            select(Epic)
            .where(Epic.id == epic_id)
            .options(selectinload(Epic.user_stories))
        )
        return result.scalar_one_or_none()

    async def approve_epic(self, epic_id: int) -> Epic | None:
        """Approve an epic"""
        return await self.update(epic_id, is_approved=True)

    async def reject_epic(self, epic_id: int) -> Epic | None:
        """Reject an epic"""
        return await self.update(epic_id, is_approved=False)
