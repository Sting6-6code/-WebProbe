'''
 导出所有 endpoints
'''
from fastapi import APIRouter
from app.api.v1.endpoints.tasks import router as tasks_router
from app.api.v1.endpoints.health import router as health_router

api_router = APIRouter()
api_router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(health_router, prefix="/health", tags=["Health"])

__all__ = ["api_router"]