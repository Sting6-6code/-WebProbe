'''
 定义 ResultResponse Schema
'''
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class ResultResponse(BaseModel):
    '''Schema for result response'''
    id: UUID
    task_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    links: List[str] = []
    text_content: Optional[str] = None
    extra_data: Dict[str, Any] = {}  # 改名与模型保持一致
    scraped_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True