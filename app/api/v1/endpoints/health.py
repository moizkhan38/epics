from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@router.get("/health/db", tags=["Health"])
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """Database health check endpoint"""
    try:
        # Test database connection
        await db.execute(text("SELECT 1"))

        # Test pgvector extension
        result = await db.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
        pgvector_installed = result.scalar_one_or_none() is not None

        return {
            "status": "healthy",
            "database": "connected",
            "pgvector": "installed" if pgvector_installed else "not installed"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
