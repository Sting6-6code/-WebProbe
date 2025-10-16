'''
 定义 Result 数据库模型，存储抓取结果
 存储抓取结果的模型

 为什么用 JSONB？
✅ 灵活存储结构化数据（列表、字典）
✅ 不需要创建新表
✅ 支持 JSON 查询（WHERE metadata->>'key' = 'value'）

 '''
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base, UUIDMixin, TimestampMixin
from datetime import datetime

class Result(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "results" #表名

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, unique=True)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    links = Column(JSONB, nullable=True, default=list)
    text_content = Column(Text, nullable=True)
    extra_data = Column(JSONB, nullable=True, default=dict)  # 改名避免与 SQLAlchemy 保留字冲突
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Result(id={self.id}, task_id={self.task_id}, title={self.title})>"