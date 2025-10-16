#定义 Task 数据库模型
'''
表示一个网页的抓取任务
'''
from sqlalchemy import Column, String, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin, UUIDMixin
import enum
from typing import Optional

#task status 枚举
class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

#Task 模型
class Task(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tasks" #表名

    url = Column(String(2048), nullable=False, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    result_id = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"<Task(id={self.id}, url={self.url}, status={self.status})>"