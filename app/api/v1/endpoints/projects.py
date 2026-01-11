from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import math

from app.db.session import get_db
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectResponse, ProjectListResponse
from app.core.security import verify_api_key
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/projects", response_model=ProjectListResponse, tags=["Projects"])
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """List all projects with pagination"""
    try:
        project_repo = ProjectRepository(db)

        # Calculate offset
        skip = (page - 1) * page_size

        # Get projects and total count
        projects = await project_repo.get_all(skip=skip, limit=page_size)
        total = await project_repo.count()

        # Calculate total pages
        total_pages = math.ceil(total / page_size)

        return ProjectListResponse(
            items=[ProjectResponse.model_validate(p) for p in projects],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error("failed_to_list_projects", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )


@router.get("/projects/{project_id}", response_model=ProjectResponse, tags=["Projects"])
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get a specific project by ID"""
    try:
        project_repo = ProjectRepository(db)
        project = await project_repo.get_by_id(project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )

        return ProjectResponse.model_validate(project)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("failed_to_get_project", project_id=project_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project"
        )


@router.delete("/projects/{project_id}", tags=["Projects"])
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete a project and all associated data"""
    try:
        project_repo = ProjectRepository(db)
        success = await project_repo.delete(project_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )

        await db.commit()

        logger.info("project_deleted", project_id=project_id)

        return {"message": "Project deleted successfully", "project_id": project_id}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("failed_to_delete_project", project_id=project_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )
