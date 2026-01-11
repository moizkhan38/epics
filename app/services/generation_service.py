from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.project_repository import ProjectRepository
from app.repositories.epic_repository import EpicRepository
from app.repositories.user_story_repository import UserStoryRepository
from app.repositories.generation_history_repository import GenerationHistoryRepository
from app.services.embedding_service import get_embedding_service
from app.services.ai_service import get_ai_service
from app.schemas.generation import GenerationRequest, RegenerateRequest, SimilarProject
from app.core.logging import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class GenerationService:
    """Service for orchestrating epic and user story generation"""

    def __init__(self, db):
        self.db = db
        from app.repositories import (
            ProjectRepository,
            EpicRepository,
            UserStoryRepository,
            GenerationHistoryRepository
        )

        self.project_repo = ProjectRepository(db)
        self.epic_repo = EpicRepository(db)
        self.story_repo = UserStoryRepository(db)
        self.history_repo = GenerationHistoryRepository(db)

    async def generate_epics_and_stories(
        self,
        request: "GenerationRequest",
        embedding_service,
        ai_service
    ) -> Dict[str, Any]:
        """
        Generate epics and user stories for a new project

        Args:
            request: Generation request with project details
            embedding_service: Service for generating embeddings
            ai_service: Service for AI generation

        Returns:
            Dictionary with generation results
        """
        from datetime import datetime

        # Generate embedding for the project description
        embedding = embedding_service.generate_embedding(request.project_description)

        # Find similar projects
        similar_projects = await project_repo.find_similar_projects(embedding)

        # Generate epics and user stories using AI
        ai_result = await ai_service.generate_epics_and_stories(
            project_description=request.project_description,
            similar_projects=similar_projects,
            additional_context=request.additional_context
        )

        # Create project
        project = await project_repo.create_with_embedding(
            name=request.project_name,
            description=request.project_description,
            embedding=embedding
        )

        # Create generation history
        version = await history_repo.get_latest_version(project.id) + 1
        generation_history = await history_repo.create(
            project_id=project.id,
            version=version,
            status="pending",
            prompt_used="Initial generation",
            model_version=settings.ANTHROPIC_MODEL,
            generation_metadata={
                "additional_context": additional_context,
                "timestamp": datetime.utcnow().isoformat()
            },
            similar_projects=similar_projects
        )

        # Create epics and user stories
        created_epics = []
        for epic_data in ai_result["epics"]:
            # Create epic
            epic = await epic_repo.create(
                project_id=project.id,
                generation_history_id=history.id,
                title=epic_data["title"],
                description=epic_data["description"],
                story_points=epic_data.get("story_points"),
                priority=epic_data.get("priority", "medium"),
                is_approved=False
            )

            # Create user stories for this epic
            for story_data in epic.get("user_stories", []):
                await user_story_repo.create(
                    epic_id=epic.id,
                    title=story_data["title"],
                    description=story_data.get("description", ""),
                    acceptance_criteria=story_data.get("acceptance_criteria"),
                    story_points=story_data.get("story_points"),
                    priority=story_data.get("priority", "medium"),
                    test_cases={"test_cases": story_data.get("test_cases", [])}
                )

            logger.info(
                "generation_completed",
                project_id=project.id,
                history_id=generation_history.id,
                epics_count=len(ai_result["epics"]),
                total_stories=sum(len(epic.get("user_stories", [])) for epic in ai_result.get("epics", []))
            )

            # Commit transaction
            await self.db.commit()

            # Fetch the complete generation history with relationships
            history = await history_repo.get_with_epics(generation_history.id)

            # Build response
            epics_response = []
            for epic in history.epics:
                epic_data = EpicResponse.model_validate(epic)
                epics_response.append(epic_data)

            return GenerationResponse(
                project_id=project.id,
                generation_history_id=history.id,
                version=history.version,
                status=history.status,
                similar_projects=[SimilarProject(**proj) for proj in similar_projects],
                epics=[EpicResponse.model_validate(epic) for epic in epics],
                message="Epics and user stories generated successfully. Please review and approve."
            )

        except Exception as e:
            await self.db.rollback()
            logger.error("generation_failed", error=str(e))
            raise

    async def regenerate_epics(
        self,
        project_id: int,
        previous_history_id: int,
        rejection_reason: str,
        additional_instructions: str | None = None
    ) -> Dict[str, Any]:
        """
        Regenerate epics based on rejection feedback

        Args:
            project_id: Project ID
            previous_history_id: ID of the rejected generation
            rejection_reason: Reason for rejection
            additional_instructions: Additional instructions for regeneration

        Returns:
            Dictionary with generation results
        """
        try:
            # Get project
            project = await self.project_repo.get_by_id(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Get previous generation history
            prev_history = await self.history_repo.get_by_id(generation_history_id)
            if not prev_history:
                raise ValueError(f"Generation history {generation_history_id} not found")

            # Get similar projects from previous generation or compute new ones
            similar_projects = prev_history.similar_projects or []

            # Generate new version
            next_version = await self.history_repo.get_latest_version(project_id) + 1

            # Generate using AI
            ai_result = await self.ai_service.generate_epics_and_stories(
                project_description=project.description,
                similar_projects=similar_projects_data,
                additional_context=additional_instructions,
                rejection_feedback=rejection_reason
            )

            # Create new generation history
            generation_history = await history_repo.create(
                project_id=project_id,
                version=new_version,
                status="pending",
                prompt_used="regeneration_prompt",
                model_version=settings.ANTHROPIC_MODEL,
                generation_metadata={
                    "regeneration": True,
                    "previous_version": version,
                    "rejection_reason": rejection_reason
                },
                similar_projects={}
            )

            # Create epics and user stories
            epics_data = []
            for epic_data in ai_result.get("epics", []):
                # Create epic
                epic = await epic_repo.create(
                    project_id=project_id,
                    generation_history_id=generation_history.id,
                    title=epic_data["title"],
                    description=epic_data["description"],
                    story_points=epic_data.get("story_points"),
                    priority=epic_data.get("priority", "medium"),
                    is_approved=False
                )

                # Create user stories
                user_stories = []
                for story_data in epic_data.get("user_stories", []):
                    test_cases = story_data.get("test_cases")

                    user_story = await user_story_repo.create(
                        epic_id=epic.id,
                        title=story_data["title"],
                        description=story_data["description"],
                        acceptance_criteria=story_data.get("acceptance_criteria"),
                        story_points=story_data.get("story_points"),
                        priority=story_data.get("priority", "medium"),
                        test_cases=test_cases
                    )
                    user_stories.append(user_story)

                epics_response.append({
                    "epic": epic,
                    "user_stories": user_stories
                })

            # Commit the transaction
            await db.commit()

            logger.info(
                "generation_completed",
                project_id=project.id,
                history_id=generation_history.id,
                epics_count=len(epics_response)
            )

            return {
                "project_id": project.id,
                "generation_history_id": generation_history.id,
                "version": version,
                "similar_projects": similar_projects,
                "epics": epics_response
            }

        except Exception as e:
            await db.rollback()
            logger.error("generation_failed", error=str(e))
            raise

    async def regenerate_epics(
        self,
        db: AsyncSession,
        project_id: int,
        generation_history_id: int,
        rejection_reason: str,
        additional_instructions: str | None = None
    ) -> Dict[str, Any]:
        """Regenerate epics based on user feedback"""

        project_repo = ProjectRepository(db)
        history_repo = GenerationHistoryRepository(db)

        # Get project and mark previous generation as rejected
        project = await project_repo.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")

        previous_history = await history_repo.get_by_id(generation_history_id)
        if not previous_history:
            raise ValueError("Generation history not found")

        # Mark as rejected
        await history_repo.reject_generation(generation_history_id, rejection_reason)

        # Get similar projects from previous generation
        similar_projects = previous_history.similar_projects or []

        # Regenerate with feedback
        feedback = f"Previous attempt was rejected. Reason: {rejection_reason}"
        if additional_instructions:
            feedback += f"\n\nAdditional instructions: {additional_instructions}"

        return await self.generate_epics_and_stories(
            db=db,
            project_name=project.name,
            project_description=project.description,
            additional_context=feedback,
            existing_project_id=project_id
        )

    async def approve_generation(
        self,
        db: AsyncSession,
        generation_history_id: int
    ) -> Dict[str, Any]:
        """Approve a generation"""

        history_repo = GenerationHistoryRepository(db)
        epic_repo = EpicRepository(db)

        generation = await history_repo.get_by_id(generation_history_id)
        if not generation:
            raise ValueError("Generation history not found")

        if generation.status == "approved":
            return {"message": "Generation already approved", "generation": generation}

        # Mark generation as approved
        from datetime import datetime
        await history_repo.approve_generation(
            generation_history_id,
            datetime.utcnow().isoformat()
        )

        # Mark all epics as approved
        epics = await epic_repo.get_by_generation_history_id(generation_history_id)
        for epic in epics:
            await epic_repo.approve_epic(epic.id)
            # Approve all user stories
            for story in epic.user_stories:
                story.is_approved = True

        await db.commit()

        logger.info(
            "generation_approved",
            generation_history_id=generation_history_id,
            epics_count=len(epics)
        )

        return {"message": "Generation approved successfully", "epics_count": len(epics)}


def get_generation_service() -> GenerationService:
    """Get generation service instance"""
    return GenerationService()
