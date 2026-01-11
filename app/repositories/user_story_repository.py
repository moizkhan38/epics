from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_story import UserStory
from app.repositories.base_repository import BaseRepository


class UserStoryRepository(BaseRepository[UserStory]):
    """Repository for UserStory model"""

    def __init__(self, db: AsyncSession):
        super().__init__(UserStory, db)

    async def get_by_epic_id(self, epic_id: int) -> List[UserStory]:
        """Get all user stories for an epic"""
        result = await self.db.execute(
            select(UserStory).where(UserStory.epic_id == epic_id)
        )
        return list(result.scalars().all())

    async def approve_story(self, story_id: int) -> UserStory | None:
        """Approve a user story"""
        return await self.update(story_id, is_approved=True)

    async def reject_story(self, story_id: int) -> UserStory | None:
        """Reject a user story"""
        return await self.update(story_id, is_approved=False)
