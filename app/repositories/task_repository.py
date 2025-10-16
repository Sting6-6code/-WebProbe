'''
创建专门处理 Task 的 Repository
'''
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
from app.repositories.base import BaseRepository
from app.models.task import Task, TaskStatus

class TaskRepository(BaseRepository[Task]):
    '''Repository for Task operations'''
    
    def __init__(self, db: Session):
        super().__init__(Task, db)
    
    def get_by_url(self, url: str) -> Optional[Task]:
        '''Get task by URL'''
        return self.db.query(Task).filter(Task.url == url).first()
    
    def get_by_status(self, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[Task]:
        '''Get tasks by status'''
        return self.db.query(Task).filter(Task.status == status).offset(skip).limit(limit).all()
    
    def update_status(self, task_id: UUID, status: TaskStatus, error_message: Optional[str] = None) -> Optional[Task]:
        '''Update task status'''
        task = self.get_by_id(task_id)
        if task:
            update_data = {"status": status}
            if error_message:
                update_data["error_message"] = error_message
            return self.update(task, update_data)
        return None
    
    def count_by_status(self, status: TaskStatus) -> int:
        '''Count tasks by status'''
        return self.db.query(Task).filter(Task.status == status).count()
    
    def get_recent(self, limit: int = 10) -> List[Task]:
        '''Get most recent tasks'''
        return self.db.query(Task).order_by(Task.created_at.desc()).limit(limit).all()

