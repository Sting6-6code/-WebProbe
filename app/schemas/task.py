'''
 定义 Task 相关的 Pydantic 模型用于 API 请求/响应
'''
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from uuid import UUID
from app.models.task import TaskStatus
from datetime import datetime

class TaskCreate(BaseModel):
   '''Schema for creating a new task'''
   url: HttpUrl = Field(..., description="URL to scrape")

   class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com"
            }
        }

class TaskResponse(BaseModel):
    '''Schema for task response'''
    id: UUID
    url: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result_id: Optional[UUID] = None

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    '''Schema for paginated task list'''
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int

   