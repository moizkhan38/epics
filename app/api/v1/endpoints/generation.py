from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.repositories import (
    ProjectRepository,
    EpicRepository,
    UserStoryRepository,
    GenerationHistoryRepository
)
from app.services.embedding_service import get_embedding_service
from app.services.ai_service import get_ai_service
from app.schemas.generation import (
    GenerationRequest,
    GenerationResponse,
    RegenerateRequest,
    ApprovalRequest,
    GenerationHistoryResponse,
    SimilarProject
)
from app.schemas.epic import EpicResponse
from app.core.security import verify_api_key
from app.core.logging import get_logger
from app.core.config import get_settings
from datetime import datetime

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.post("/generate", response_model=GenerationResponse, tags=["Generation"])
async def generate_epics_and_stories(
    request: GenerationRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Generate epics and user stories for a new project

    This endpoint:
    1. Creates a new project
    2. Finds similar projects using vector similarity
    3. Generates epics and user stories using AI
    4. Returns the generated content for review
    """
    try:
        logger.info(
            "generation_request_received",
            project_name=request.project_name
        )

        # Initialize services and repositories
        embedding_service = get_embedding_service()
        ai_service = get_ai_service()
        project_repo = ProjectRepository(db)
        epic_repo = EpicRepository(db)
        story_repo = UserStoryRepository(db)
        history_repo = GenerationHistoryRepository(db)

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
                "additional_context": request.additional_context,
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
                generation_history_id=generation_history.id,
                title=epic_data["title"],
                description=epic_data["description"],
                story_points=epic_data.get("story_points"),
                priority=epic_data.get("priority", "medium"),
                is_approved=False
            )

            # Create user stories for this epic
            for story_data in epic_data.get("user_stories", []):
                await story_repo.create(
                    epic_id=epic.id,
                    title=story_data["title"],
                    description=story_data.get("description", ""),
                    acceptance_criteria=story_data.get("acceptance_criteria"),
                    story_points=story_data.get("story_points"),
                    priority=story_data.get("priority", "medium"),
                    test_cases={"test_cases": story_data.get("test_cases", [])}
                )

            created_epics.append(epic)

        # Commit transaction
        await db.commit()

        # Fetch the complete generation history with relationships
        history = await history_repo.get_with_epics(generation_history.id)

        logger.info(
            "generation_completed",
            project_id=project.id,
            history_id=generation_history.id,
            epics_count=len(history.epics)
        )

        # Build response
        return GenerationResponse(
            project_id=project.id,
            generation_history_id=history.id,
            version=history.version,
            status=history.status,
            similar_projects=[SimilarProject(**proj) for proj in similar_projects],
            epics=[EpicResponse.model_validate(epic) for epic in history.epics],
            message="Epics and user stories generated successfully. Please review and approve."
        )

    except Exception as e:
        await db.rollback()
        logger.error("generation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate epics: {str(e)}"
        )


@router.post("/regenerate", response_model=GenerationResponse, tags=["Generation"])
async def regenerate_epics(
    request: RegenerateRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Regenerate epics based on rejection feedback

    This endpoint:
    1. Marks the previous generation as rejected
    2. Uses the rejection feedback to improve the next generation
    3. Creates a new version with regenerated content
    """
    try:
        logger.info(
            "regeneration_request_received",
            project_id=request.project_id,
            history_id=request.generation_history_id
        )

        # Initialize services and repositories
        ai_service = get_ai_service()
        project_repo = ProjectRepository(db)
        epic_repo = EpicRepository(db)
        story_repo = UserStoryRepository(db)
        history_repo = GenerationHistoryRepository(db)

        # Get project
        project = await project_repo.get_by_id(request.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {request.project_id} not found"
            )

        # Get previous generation history
        prev_history = await history_repo.get_by_id(request.generation_history_id)
        if not prev_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Generation history {request.generation_history_id} not found"
            )

        # Mark previous as rejected
        await history_repo.reject_generation(
            request.generation_history_id,
            request.rejection_reason
        )

        # Get similar projects from previous generation
        similar_projects = prev_history.similar_projects or []

        # Build feedback prompt
        feedback = f"Previous attempt was rejected. Reason: {request.rejection_reason}"
        if request.additional_instructions:
            feedback += f"\n\nAdditional instructions: {request.additional_instructions}"

        # Regenerate using AI
        ai_result = await ai_service.generate_epics_and_stories(
            project_description=project.description,
            similar_projects=similar_projects,
            additional_context=feedback,
            rejection_feedback=request.rejection_reason
        )

        # Create new generation history
        new_version = await history_repo.get_latest_version(project.id) + 1
        generation_history = await history_repo.create(
            project_id=project.id,
            version=new_version,
            status="pending",
            prompt_used="Regeneration with feedback",
            model_version=settings.ANTHROPIC_MODEL,
            generation_metadata={
                "regeneration": True,
                "previous_version": prev_history.version,
                "rejection_reason": request.rejection_reason,
                "additional_instructions": request.additional_instructions,
                "timestamp": datetime.utcnow().isoformat()
            },
            similar_projects=similar_projects
        )

        # Create epics and user stories
        for epic_data in ai_result["epics"]:
            epic = await epic_repo.create(
                project_id=project.id,
                generation_history_id=generation_history.id,
                title=epic_data["title"],
                description=epic_data["description"],
                story_points=epic_data.get("story_points"),
                priority=epic_data.get("priority", "medium"),
                is_approved=False
            )

            for story_data in epic_data.get("user_stories", []):
                await story_repo.create(
                    epic_id=epic.id,
                    title=story_data["title"],
                    description=story_data.get("description", ""),
                    acceptance_criteria=story_data.get("acceptance_criteria"),
                    story_points=story_data.get("story_points"),
                    priority=story_data.get("priority", "medium"),
                    test_cases={"test_cases": story_data.get("test_cases", [])}
                )

        # Commit transaction
        await db.commit()

        # Fetch complete generation history
        history = await history_repo.get_with_epics(generation_history.id)

        logger.info(
            "regeneration_completed",
            project_id=project.id,
            history_id=generation_history.id,
            version=new_version
        )

        return GenerationResponse(
            project_id=project.id,
            generation_history_id=history.id,
            version=history.version,
            status=history.status,
            similar_projects=[SimilarProject(**proj) for proj in similar_projects],
            epics=[EpicResponse.model_validate(epic) for epic in history.epics],
            message="Epics regenerated successfully. Please review and approve."
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("regeneration_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate epics: {str(e)}"
        )


@router.post("/approve", tags=["Generation"])
async def approve_generation(
    request: ApprovalRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Approve or reject a generation

    If approved, all epics and user stories are marked as approved.
    If rejected, provide rejection_reason for regeneration.
    """
    try:
        history_repo = GenerationHistoryRepository(db)
        epic_repo = EpicRepository(db)

        # Get generation history
        generation = await history_repo.get_by_id(request.generation_history_id)
        if not generation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Generation history {request.generation_history_id} not found"
            )

        if request.is_approved:
            # Approve generation
            await history_repo.approve_generation(
                request.generation_history_id,
                datetime.utcnow().isoformat()
            )

            # Approve all epics and their user stories
            epics = await epic_repo.get_by_generation_history_id(request.generation_history_id)
            for epic in epics:
                await epic_repo.approve_epic(epic.id)
                for story in epic.user_stories:
                    story.is_approved = True

            await db.commit()

            logger.info(
                "generation_approved",
                generation_history_id=request.generation_history_id,
                epics_count=len(epics)
            )

            return {
                "message": "Generation approved successfully",
                "generation_history_id": request.generation_history_id,
                "epics_count": len(epics)
            }
        else:
            # Reject generation
            if not request.rejection_reason:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rejection reason is required when rejecting a generation"
                )

            await history_repo.reject_generation(
                request.generation_history_id,
                request.rejection_reason
            )
            await db.commit()

            logger.info(
                "generation_rejected",
                generation_history_id=request.generation_history_id,
                reason=request.rejection_reason
            )

            return {
                "message": "Generation rejected. Use /regenerate endpoint to create a new version.",
                "generation_history_id": request.generation_history_id
            }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("approval_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process approval: {str(e)}"
        )


@router.get("/history/{project_id}", response_model=List[GenerationHistoryResponse], tags=["Generation"])
async def get_generation_history(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get all generation history for a project"""
    try:
        history_repo = GenerationHistoryRepository(db)
        project_repo = ProjectRepository(db)

        # Check if project exists
        project = await project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )

        # Get generation history
        histories = await history_repo.get_by_project_id(project_id)

        return [GenerationHistoryResponse.model_validate(h) for h in histories]

    except HTTPException:
        raise
    except Exception as e:
        logger.error("failed_to_get_history", project_id=project_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve generation history"
        )
