from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.task_repository import TaskRepository

def get_task_repository(db: Session = Depends(get_db)) -> TaskRepository:
    """Dependency to get TaskRepository instance"""
    return TaskRepository(db)