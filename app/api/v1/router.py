from fastapi import APIRouter

from app.api.v1.endpoints import health, projects, generation

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router)
api_router.include_router(projects.router)
api_router.include_router(generation.router)
