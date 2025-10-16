'''
 创建健康检查端点
'''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.config import settings

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    Verifies database connectivity and service status.
    """
    try:
        # Test database connection
        db.execute("SELECT 1")

        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")