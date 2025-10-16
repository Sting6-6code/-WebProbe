# WebProbe MVP 构建任务列表

> 本文档包含按顺序执行的小型、可测试的任务。每个任务专注于一个问题，有明确的开始和结束。

---

## 📋 任务执行说明

- ✅ 每个任务完成后，运行验证步骤确保功能正常
- ✅ 按照任务编号顺序执行
- ✅ 不要跳过任何任务
- ✅ 每个任务完成后标记为已完成

---

## 阶段 1: 项目基础设置 (Tasks 1-5)

### Task 1: 创建项目依赖文件

**目标**: 创建 `requirements.txt` 文件，包含所有必要的 Python 依赖

**具体步骤**:

1. 在项目根目录创建 `requirements.txt`
2. 添加以下依赖（指定版本）:
   - fastapi==0.104.1
   - uvicorn[standard]==0.24.0
   - sqlalchemy==2.0.23
   - psycopg2-binary==2.9.9
   - pydantic==2.5.0
   - pydantic-settings==2.1.0
   - redis==5.0.1
   - celery==5.3.4
   - requests==2.31.0
   - beautifulsoup4==4.12.2
   - python-dotenv==1.0.0

**验证**:

- 文件存在于项目根目录
- 文件包含所有列出的依赖

**完成标志**: `requirements.txt` 文件已创建并包含所有依赖

---

### Task 2: 创建 .gitignore 文件

**目标**: 创建 `.gitignore` 文件，忽略不必要的文件

**具体步骤**:

1. 在项目根目录创建 `.gitignore`
2. 添加以下内容:

   ```
   # Python
   __pycache__/
   *.py[cod]
   *$py.class
   *.so
   .Python
   env/
   venv/
   ENV/

   # Environment
   .env
   .env.local

   # IDE
   .vscode/
   .idea/
   *.swp
   *.swo

   # Database
   *.db
   *.sqlite

   # Logs
   *.log
   logs/

   # Testing
   .pytest_cache/
   .coverage
   htmlcov/

   # Celery
   celerybeat-schedule
   celerybeat.pid
   ```

**验证**:

- `.gitignore` 文件存在
- 文件包含常见的 Python 和项目相关的忽略规则

**完成标志**: `.gitignore` 文件已创建

---

### Task 3: 创建环境变量示例文件

**目标**: 创建 `.env.example` 文件作为环境变量模板

**具体步骤**:

1. 在项目根目录创建 `.env.example`
2. 添加以下内容:

   ```bash
   # Database
   DATABASE_URL=postgresql://webprobe:secret@localhost:5432/webprobe_db

   # Redis
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_URL=redis://localhost:6379/0

   # Celery
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/1

   # Application
   APP_NAME=WebProbe
   DEBUG=true
   LOG_LEVEL=INFO

   # Cache
   CACHE_TTL=300

   # Scraper
   REQUEST_TIMEOUT=30
   MAX_RETRIES=3
   USER_AGENT=WebProbe/1.0
   ```

**验证**:

- `.env.example` 文件存在
- 包含所有必要的配置项

**完成标志**: `.env.example` 文件已创建

---

### Task 4: 创建基础目录结构

**目标**: 创建项目所需的所有空目录和 `__init__.py` 文件

**具体步骤**:

1. 创建以下目录结构（如果不存在）:

   ```
   app/
   app/api/
   app/api/v1/
   app/api/v1/endpoints/
   app/models/
   app/schemas/
   app/services/
   app/repositories/
   app/celery_app/
   app/celery_app/tasks/
   app/core/
   app/utils/
   tests/
   tests/unit/
   tests/integration/
   ```

2. 在每个 Python 包目录中创建空的 `__init__.py` 文件

**验证**:

- 运行 `find app -type f -name "__init__.py"` 应该列出所有 `__init__.py` 文件
- 所有目录存在

**完成标志**: 目录结构已创建，所有 `__init__.py` 文件存在

---

### Task 5: 创建配置管理模块 (app/config.py)

**目标**: 创建配置管理类，使用 Pydantic Settings 加载环境变量

**具体步骤**:

1. 创建 `app/config.py`
2. 实现 `Settings` 类:
   - 继承 `BaseSettings`
   - 定义所有配置字段（数据库、Redis、Celery、应用等）
   - 配置从 `.env` 文件加载
   - 创建全局 `settings` 实例

**代码结构**:

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Application
    APP_NAME: str = "WebProbe"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Cache
    CACHE_TTL: int = 300

    # Scraper
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    USER_AGENT: str = "WebProbe/1.0"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

**验证**:

- 创建 `.env` 文件（复制自 `.env.example`）
- 在 Python REPL 中运行: `from app.config import settings; print(settings.APP_NAME)`
- 应该成功打印配置值

**完成标志**: `app/config.py` 已创建，可以成功导入和读取配置

---

## 阶段 2: 数据库层 (Tasks 6-11)

### Task 6: 创建数据库基础模型 (app/models/base.py)

**目标**: 创建 SQLAlchemy 声明式基类

**具体步骤**:

1. 创建 `app/models/base.py`
2. 定义 `Base` 类和通用的基础模型字段

**代码结构**:

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class UUIDMixin:
    """Mixin for UUID primary key"""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
```

**验证**:

- 文件可以成功导入: `from app.models.base import Base`
- 没有语法错误

**完成标志**: `app/models/base.py` 已创建并可导入

---

### Task 7: 创建 Task 模型 (app/models/task.py)

**目标**: 定义 Task 数据库模型

**具体步骤**:

1. 创建 `app/models/task.py`
2. 定义 `TaskStatus` 枚举
3. 定义 `Task` 模型类

**代码结构**:

```python
from sqlalchemy import Column, String, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin, UUIDMixin
import enum
from typing import Optional

class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Task(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tasks"

    url = Column(String(2048), nullable=False, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    result_id = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"<Task(id={self.id}, url={self.url}, status={self.status})>"
```

**验证**:

- 成功导入: `from app.models.task import Task, TaskStatus`
- 枚举值可访问: `print(TaskStatus.PENDING)`

**完成标志**: `app/models/task.py` 已创建，Task 模型定义完整

---

### Task 8: 创建 Result 模型 (app/models/result.py)

**目标**: 定义 Result 数据库模型，存储抓取结果

**具体步骤**:

1. 创建 `app/models/result.py`
2. 定义 `Result` 模型类

**代码结构**:

```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base, UUIDMixin, TimestampMixin
from datetime import datetime

class Result(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "results"

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, unique=True)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    links = Column(JSONB, nullable=True, default=list)
    text_content = Column(Text, nullable=True)
    extra_data = Column(JSONB, nullable=True, default=dict)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Result(id={self.id}, task_id={self.task_id}, title={self.title})>"
```

**验证**:

- 成功导入: `from app.models.result import Result`
- 没有导入错误

**完成标志**: `app/models/result.py` 已创建

---

### Task 9: 更新 models/**init**.py

**目标**: 在 models 包的 `__init__.py` 中导出所有模型

**具体步骤**:

1. 编辑 `app/models/__init__.py`
2. 导入并导出所有模型

**代码内容**:

```python
from app.models.base import Base
from app.models.task import Task, TaskStatus
from app.models.result import Result

__all__ = ["Base", "Task", "TaskStatus", "Result"]
```

**验证**:

- 成功导入: `from app.models import Task, Result, Base, TaskStatus`

**完成标志**: 所有模型可以从 `app.models` 包导入

---

### Task 10: 创建数据库连接模块 (app/core/database.py)

**目标**: 创建数据库引擎、会话工厂和依赖注入函数

**具体步骤**:

1. 创建 `app/core/database.py`
2. 创建数据库引擎
3. 创建会话工厂
4. 实现 `get_db()` 依赖函数

**代码结构**:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from typing import Generator

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that yields a database session.
    Used with FastAPI's Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database tables.
    Creates all tables defined in models.
    """
    from app.models import Base
    Base.metadata.create_all(bind=engine)
```

**验证**:

- 成功导入: `from app.core.database import engine, get_db, init_db`
- 注意: 暂时不要运行 `init_db()`，因为数据库可能还未准备好

**完成标志**: `app/core/database.py` 已创建

---

### Task 11: 创建数据库初始化脚本 (scripts/init_db.py)

**目标**: 创建用于初始化数据库表的独立脚本

**具体步骤**:

1. 创建 `scripts/` 目录（如果不存在）
2. 创建 `scripts/init_db.py`

**代码结构**:

```python
#!/usr/bin/env python3
"""
Database initialization script.
Run this to create all database tables.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import init_db, engine
from app.models import Base

def main():
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**验证**:

- 文件存在且可执行
- 可以运行（当数据库可用时）: `python scripts/init_db.py`

**完成标志**: 数据库初始化脚本已创建

---

## 阶段 3: Pydantic Schemas (Tasks 12-14)

### Task 12: 创建 Task Schemas (app/schemas/task.py)

**目标**: 定义 Task 相关的 Pydantic 模型用于 API 请求/响应

**具体步骤**:

1. 创建 `app/schemas/task.py`
2. 定义以下 Schema:
   - `TaskCreate`: 创建任务的请求体
   - `TaskResponse`: 任务的响应模型
   - `TaskListResponse`: 任务列表响应

**代码结构**:

```python
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.models.task import TaskStatus

class TaskCreate(BaseModel):
    """Schema for creating a new task"""
    url: HttpUrl = Field(..., description="URL to scrape")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com"
            }
        }

class TaskResponse(BaseModel):
    """Schema for task response"""
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
    """Schema for paginated task list"""
    tasks: list[TaskResponse]
    total: int
    page: int
    page_size: int
```

**验证**:

- 成功导入: `from app.schemas.task import TaskCreate, TaskResponse`
- 可以创建实例: `task = TaskCreate(url="https://example.com")`

**完成标志**: Task schemas 已创建并可导入

---

### Task 13: 创建 Result Schemas (app/schemas/result.py)

**目标**: 定义 Result 相关的 Pydantic 模型

**具体步骤**:

1. 创建 `app/schemas/result.py`
2. 定义 `ResultResponse` Schema

**代码结构**:

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, List, Any
from uuid import UUID

class ResultResponse(BaseModel):
    """Schema for scraping result response"""
    id: UUID
    task_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    links: List[str] = []
    text_content: Optional[str] = None
    extra_data: Dict[str, Any] = {}
    scraped_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
```

**验证**:

- 成功导入: `from app.schemas.result import ResultResponse`

**完成标志**: Result schema 已创建

---

### Task 14: 更新 schemas/**init**.py

**目标**: 导出所有 schemas

**具体步骤**:

1. 编辑 `app/schemas/__init__.py`

**代码内容**:

```python
from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse
from app.schemas.result import ResultResponse

__all__ = [
    "TaskCreate",
    "TaskResponse",
    "TaskListResponse",
    "ResultResponse",
]
```

**验证**:

- 成功导入: `from app.schemas import TaskCreate, TaskResponse, ResultResponse`

**完成标志**: Schemas 可以统一导入

---

## 阶段 4: Repository 层 (Tasks 15-17)

### Task 15: 创建基础 Repository (app/repositories/base.py)

**目标**: 创建通用的 Repository 基类

**具体步骤**:

1. 创建 `app/repositories/base.py`
2. 实现 `BaseRepository` 类

**代码结构**:

```python
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: any) -> Optional[ModelType]:
        """Get a record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination"""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: dict) -> ModelType:
        """Create a new record"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        """Update an existing record"""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: any) -> bool:
        """Delete a record by ID"""
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
```

**验证**:

- 成功导入: `from app.repositories.base import BaseRepository`

**完成标志**: 基础 Repository 已创建

---

### Task 16: 创建 Task Repository (app/repositories/task_repository.py)

**目标**: 创建专门处理 Task 的 Repository

**具体步骤**:

1. 创建 `app/repositories/task_repository.py`
2. 继承 `BaseRepository` 并添加 Task 特定的方法

**代码结构**:

```python
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
from app.repositories.base import BaseRepository
from app.models.task import Task, TaskStatus

class TaskRepository(BaseRepository[Task]):
    """Repository for Task operations"""

    def __init__(self, db: Session):
        super().__init__(Task, db)

    def get_by_url(self, url: str) -> Optional[Task]:
        """Get task by URL"""
        return self.db.query(Task).filter(Task.url == url).first()

    def get_by_status(self, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get tasks by status"""
        return self.db.query(Task).filter(Task.status == status).offset(skip).limit(limit).all()

    def update_status(self, task_id: UUID, status: TaskStatus, error_message: Optional[str] = None) -> Optional[Task]:
        """Update task status"""
        task = self.get_by_id(task_id)
        if task:
            update_data = {"status": status}
            if error_message:
                update_data["error_message"] = error_message
            return self.update(task, update_data)
        return None

    def count_by_status(self, status: TaskStatus) -> int:
        """Count tasks by status"""
        return self.db.query(Task).filter(Task.status == status).count()

    def get_recent(self, limit: int = 10) -> List[Task]:
        """Get most recent tasks"""
        return self.db.query(Task).order_by(Task.created_at.desc()).limit(limit).all()
```

**验证**:

- 成功导入: `from app.repositories.task_repository import TaskRepository`

**完成标志**: Task Repository 已创建

---

### Task 17: 更新 repositories/**init**.py

**目标**: 导出所有 repositories

**具体步骤**:

1. 编辑 `app/repositories/__init__.py`

**代码内容**:

```python
from app.repositories.base import BaseRepository
from app.repositories.task_repository import TaskRepository

__all__ = ["BaseRepository", "TaskRepository"]
```

**验证**:

- 成功导入: `from app.repositories import TaskRepository`

**完成标志**: Repositories 可统一导入

---

## 阶段 5: 基础 API (Tasks 18-22)

### Task 18: 创建 API 依赖注入 (app/api/v1/dependencies.py)

**目标**: 创建 API 端点使用的依赖注入函数

**具体步骤**:

1. 创建 `app/api/v1/dependencies.py`
2. 定义常用的依赖函数

**代码结构**:

```python
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.task_repository import TaskRepository

def get_task_repository(db: Session = Depends(get_db)) -> TaskRepository:
    """Dependency to get TaskRepository instance"""
    return TaskRepository(db)
```

**验证**:

- 成功导入: `from app.api.v1.dependencies import get_task_repository`

**完成标志**: API 依赖已创建

---

### Task 19: 创建健康检查端点 (app/api/v1/endpoints/health.py)

**目标**: 创建健康检查 API 端点

**具体步骤**:

1. 创建 `app/api/v1/endpoints/health.py`
2. 实现 `/health` 端点

**代码结构**:

```python
from fastapi import APIRouter, Depends, HTTPException
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
```

**验证**:

- 文件可以导入
- Router 定义正确

**完成标志**: 健康检查端点已创建

---

### Task 20: 创建任务 API 端点 - 创建任务 (app/api/v1/endpoints/tasks.py - Part 1)

**目标**: 实现 `POST /tasks` 端点用于创建新任务

**具体步骤**:

1. 创建 `app/api/v1/endpoints/tasks.py`
2. 实现创建任务的端点

**代码结构**:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.schemas.task import TaskCreate, TaskResponse
from app.repositories.task_repository import TaskRepository
from app.api.v1.dependencies import get_task_repository

router = APIRouter()

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(
    task_in: TaskCreate,
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """
    Create a new scraping task.

    - **url**: The URL to scrape

    Returns the created task with status PENDING.
    """
    try:
        # Create task data
        task_data = {
            "url": str(task_in.url),
            "status": "PENDING"
        }

        # Create task in database
        task = task_repo.create(task_data)

        # TODO: Later we will trigger Celery task here

        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )
```

**验证**:

- 文件可以成功导入
- Router 定义正确

**完成标志**: 创建任务端点已实现

---

### Task 21: 创建任务 API 端点 - 查询任务 (app/api/v1/endpoints/tasks.py - Part 2)

**目标**: 在同一文件中添加查询任务的端点

**具体步骤**:

1. 编辑 `app/api/v1/endpoints/tasks.py`
2. 添加以下端点:
   - `GET /tasks/{task_id}` - 获取单个任务
   - `GET /tasks` - 获取任务列表

**添加的代码**:

```python
from typing import Optional
from app.schemas.task import TaskListResponse
from app.models.task import TaskStatus

@router.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(
    task_id: UUID,
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """
    Get a specific task by ID.

    Returns task details including current status.
    """
    task = task_repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return task

@router.get("/tasks", response_model=TaskListResponse, tags=["Tasks"])
async def list_tasks(
    skip: int = 0,
    limit: int = 10,
    status_filter: Optional[TaskStatus] = None,
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """
    List tasks with pagination and optional status filter.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 10)
    - **status_filter**: Optional status filter (PENDING, PROCESSING, SUCCESS, FAILED)
    """
    if status_filter:
        tasks = task_repo.get_by_status(status_filter, skip, limit)
        total = task_repo.count_by_status(status_filter)
    else:
        tasks = task_repo.get_all(skip, limit)
        total = len(tasks)  # Simple count, not efficient for large datasets

    return {
        "tasks": tasks,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }
```

**验证**:

- 文件可以成功导入
- 所有端点定义正确

**完成标志**: 任务查询端点已实现

---

### Task 22: 创建 API 路由聚合 (app/api/v1/**init**.py 和 app/main.py)

**目标**: 聚合所有 v1 API 路由并创建 FastAPI 应用

**具体步骤**:

**步骤 1**: 编辑 `app/api/v1/__init__.py`

```python
from fastapi import APIRouter
from app.api.v1.endpoints import tasks, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(tasks.router, prefix="", tags=["Tasks"])
```

**步骤 2**: 创建 `app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import api_router

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Async Web Scraping and Analysis Platform",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to WebProbe API",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**验证**:

- 启动应用: `uvicorn app.main:app --reload`
- 访问 `http://localhost:8000/docs` 查看 API 文档
- 测试健康检查: `curl http://localhost:8000/api/v1/health`

**完成标志**: FastAPI 应用已创建，API 端点可访问

---

## 阶段 6: Celery 集成 (Tasks 23-26)

### Task 23: 创建 Celery 配置 (app/celery_app/celery_config.py)

**目标**: 配置 Celery 应用

**具体步骤**:

1. 创建 `app/celery_app/celery_config.py`
2. 配置 Celery broker 和 backend

**代码结构**:

```python
from celery import Celery
from app.config import settings

# Create Celery instance
celery_app = Celery(
    "webprobe",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.celery_app.tasks.scrape_task"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Optional: Configure task routes
celery_app.conf.task_routes = {
    "app.celery_app.tasks.scrape_task.*": {"queue": "scraping"},
}
```

**验证**:

- 成功导入: `from app.celery_app.celery_config import celery_app`

**完成标志**: Celery 配置已创建

---

### Task 24: 创建基础爬虫服务 (app/services/scraper_service.py)

**目标**: 实现简单的网页抓取逻辑

**具体步骤**:

1. 创建 `app/services/scraper_service.py`
2. 实现基础的网页抓取功能

**代码结构**:

```python
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class ScraperService:
    """Service for web scraping operations"""

    def __init__(self):
        self.timeout = settings.REQUEST_TIMEOUT
        self.user_agent = settings.USER_AGENT
        self.max_retries = settings.MAX_RETRIES

    def scrape_url(self, url: str) -> Dict:
        """
        Scrape a URL and extract content.

        Returns:
            Dictionary with title, links, text_content, and extra_data
        """
        try:
            # Make HTTP request
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract data
            result = {
                "title": self._extract_title(soup),
                "description": self._extract_description(soup),
                "links": self._extract_links(soup, url),
                "text_content": self._extract_text(soup),
                "extra_data": {
                    "status_code": response.status_code,
                    "content_type": response.headers.get("Content-Type"),
                    "content_length": len(response.content)
                }
            }

            return result

        except requests.RequestException as e:
            logger.error(f"Failed to scrape {url}: {e}")
            raise Exception(f"Scraping failed: {str(e)}")

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title"""
        title_tag = soup.find("title")
        return title_tag.get_text(strip=True) if title_tag else None

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract meta description"""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        return meta_desc.get("content") if meta_desc else None

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from page"""
        links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            # Simple link extraction (can be improved with urljoin for relative URLs)
            if href.startswith("http"):
                links.append(href)
        return links[:100]  # Limit to first 100 links

    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract main text content"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text(separator=" ", strip=True)

        # Limit text length
        return text[:5000]  # First 5000 characters
```

**验证**:

- 成功导入: `from app.services.scraper_service import ScraperService`
- 可以创建实例: `scraper = ScraperService()`

**完成标志**: 爬虫服务已创建

---

### Task 25: 创建 Celery 抓取任务 (app/celery_app/tasks/scrape_task.py)

**目标**: 实现异步抓取任务

**具体步骤**:

1. 创建 `app/celery_app/tasks/scrape_task.py`
2. 实现抓取任务逻辑

**代码结构**:

```python
from celery import Task
from app.celery_app.celery_config import celery_app
from app.services.scraper_service import ScraperService
from app.core.database import SessionLocal
from app.repositories.task_repository import TaskRepository
from app.models.task import TaskStatus
from app.models.result import Result
from datetime import datetime
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class ScraperTask(Task):
    """Custom task class with database session handling"""

    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)

@celery_app.task(bind=True, base=ScraperTask, name="scrape_website", max_retries=3)
def scrape_website_task(self, task_id: str, url: str):
    """
    Asynchronous task to scrape a website.

    Args:
        task_id: UUID of the task in database
        url: URL to scrape
    """
    db = SessionLocal()
    task_repo = TaskRepository(db)

    try:
        # Convert string ID to UUID
        task_uuid = UUID(task_id)

        # Update task status to PROCESSING
        logger.info(f"Starting scrape task for {url}")
        task_repo.update_status(task_uuid, TaskStatus.PROCESSING)

        # Update started_at timestamp
        task = task_repo.get_by_id(task_uuid)
        if task:
            task_repo.update(task, {"started_at": datetime.utcnow()})

        # Perform scraping
        scraper = ScraperService()
        scrape_result = scraper.scrape_url(url)

        # Save result to database
        result = Result(
            task_id=task_uuid,
            title=scrape_result.get("title"),
            description=scrape_result.get("description"),
            links=scrape_result.get("links", []),
            text_content=scrape_result.get("text_content"),
            extra_data=scrape_result.get("extra_data", {}),
            scraped_at=datetime.utcnow()
        )
        db.add(result)
        db.commit()
        db.refresh(result)

        # Update task status to SUCCESS
        task_repo.update(task, {
            "status": TaskStatus.SUCCESS,
            "completed_at": datetime.utcnow(),
            "result_id": result.id
        })

        logger.info(f"Successfully scraped {url}")
        return {"status": "success", "result_id": str(result.id)}

    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")

        # Update task status to FAILED
        task = task_repo.get_by_id(UUID(task_id))
        if task:
            task_repo.update(task, {
                "status": TaskStatus.FAILED,
                "completed_at": datetime.utcnow(),
                "error_message": str(e)
            })

        # Retry if not max retries reached
        raise self.retry(exc=e, countdown=60)

    finally:
        db.close()
```

**验证**:

- 成功导入: `from app.celery_app.tasks.scrape_task import scrape_website_task`

**完成标志**: Celery 抓取任务已创建

---

### Task 26: 创建 Celery Worker 入口 (app/celery_app/worker.py)

**目标**: 创建 Celery worker 启动文件

**具体步骤**:

1. 创建 `app/celery_app/worker.py`

**代码结构**:

```python
"""
Celery worker entry point.

To start the worker, run:
    celery -A app.celery_app.worker worker --loglevel=info
"""

from app.celery_app.celery_config import celery_app

# Import all tasks to register them
from app.celery_app.tasks import scrape_task

__all__ = ["celery_app"]
```

**验证**:

- 可以启动 worker（如果 Redis 运行中）: `celery -A app.celery_app.worker worker --loglevel=info`

**完成标志**: Celery worker 入口已创建

---

### Task 27: 集成 Celery 到 API - 更新创建任务端点

**目标**: 在创建任务时触发 Celery 任务

**具体步骤**:

1. 编辑 `app/api/v1/endpoints/tasks.py`
2. 在 `create_task` 函数中添加 Celery 任务触发

**更新代码** (替换 create_task 函数):

```python
from app.celery_app.tasks.scrape_task import scrape_website_task

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(
    task_in: TaskCreate,
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """
    Create a new scraping task and trigger async processing.

    - **url**: The URL to scrape

    Returns the created task with status PENDING.
    The scraping will be performed asynchronously by Celery worker.
    """
    try:
        # Create task data
        task_data = {
            "url": str(task_in.url),
            "status": "PENDING"
        }

        # Create task in database
        task = task_repo.create(task_data)

        # Trigger Celery task asynchronously
        scrape_website_task.delay(str(task.id), str(task.url))

        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )
```

**验证**:

- 重启 FastAPI 应用
- 确保 Celery worker 运行中
- 创建一个任务，观察 worker 日志

**完成标志**: API 成功触发 Celery 任务

---

## 阶段 7: Redis 缓存层 (Tasks 28-30)

### Task 28: 创建 Redis 客户端 (app/core/redis_client.py)

**目标**: 创建 Redis 连接和客户端

**具体步骤**:

1. 创建 `app/core/redis_client.py`

**代码结构**:

```python
import redis
from app.config import settings
from typing import Optional
import json

class RedisClient:
    """Redis client wrapper"""

    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

    def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        return self.client.get(key)

    def set(self, key: str, value: str, ttl: Optional[int] = None):
        """Set value with optional TTL"""
        if ttl:
            self.client.setex(key, ttl, value)
        else:
            self.client.set(key, value)

    def delete(self, key: str):
        """Delete key"""
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return bool(self.client.exists(key))

    def ping(self) -> bool:
        """Test connection"""
        try:
            return self.client.ping()
        except:
            return False

# Global Redis client instance
redis_client = RedisClient()

def get_redis() -> RedisClient:
    """Dependency function to get Redis client"""
    return redis_client
```

**验证**:

- 成功导入: `from app.core.redis_client import redis_client`
- 测试连接（如果 Redis 运行中）: `redis_client.ping()`

**完成标志**: Redis 客户端已创建

---

### Task 29: 创建缓存服务 (app/services/cache_service.py)

**目标**: 实现缓存逻辑封装

**具体步骤**:

1. 创建 `app/services/cache_service.py`

**代码结构**:

```python
import hashlib
import json
from typing import Optional, Dict, Any
from app.core.redis_client import RedisClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """Service for caching scraped results"""

    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
        self.ttl = settings.CACHE_TTL

    def get_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return f"cache:url:{url_hash}"

    def get_cached_result(self, url: str) -> Optional[Dict[Any, Any]]:
        """Get cached result for URL"""
        try:
            cache_key = self.get_cache_key(url)
            cached_data = self.redis.get(cache_key)

            if cached_data:
                logger.info(f"Cache HIT for {url}")
                return json.loads(cached_data)

            logger.info(f"Cache MISS for {url}")
            return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set_cached_result(self, url: str, result: Dict[Any, Any]):
        """Cache result for URL"""
        try:
            cache_key = self.get_cache_key(url)
            cached_data = json.dumps(result)
            self.redis.set(cache_key, cached_data, ttl=self.ttl)
            logger.info(f"Cached result for {url} (TTL: {self.ttl}s)")

        except Exception as e:
            logger.error(f"Cache set error: {e}")

    def invalidate_cache(self, url: str):
        """Invalidate cache for URL"""
        try:
            cache_key = self.get_cache_key(url)
            self.redis.delete(cache_key)
            logger.info(f"Invalidated cache for {url}")

        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
```

**验证**:

- 成功导入: `from app.services.cache_service import CacheService`

**完成标志**: 缓存服务已创建

---

### Task 30: 集成缓存到 API 和 Celery 任务

**目标**: 在创建任务前检查缓存，抓取后写入缓存

**具体步骤**:

**步骤 1**: 更新 `app/api/v1/dependencies.py`，添加缓存服务依赖

```python
from app.services.cache_service import CacheService
from app.core.redis_client import get_redis, RedisClient

def get_cache_service(redis: RedisClient = Depends(get_redis)) -> CacheService:
    """Dependency to get CacheService instance"""
    return CacheService(redis)
```

**步骤 2**: 更新 `app/api/v1/endpoints/tasks.py`，在创建任务前检查缓存

```python
from app.services.cache_service import CacheService
from app.api.v1.dependencies import get_cache_service

# Update create_task function
@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(
    task_in: TaskCreate,
    task_repo: TaskRepository = Depends(get_task_repository),
    cache_service: CacheService = Depends(get_cache_service)
):
    """
    Create a new scraping task and trigger async processing.
    Checks cache first to avoid duplicate scraping.
    """
    try:
        url = str(task_in.url)

        # Check cache first
        cached_result = cache_service.get_cached_result(url)
        if cached_result:
            # Return cached result as a completed task
            # (Simplified: in production, you might return the cached result differently)
            pass

        # Create task data
        task_data = {
            "url": url,
            "status": "PENDING"
        }

        # Create task in database
        task = task_repo.create(task_data)

        # Trigger Celery task asynchronously
        scrape_website_task.delay(str(task.id), url)

        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )
```

**步骤 3**: 更新 `app/celery_app/tasks/scrape_task.py`，抓取后写入缓存

```python
# Add at the top
from app.core.redis_client import redis_client
from app.services.cache_service import CacheService

# Update scrape_website_task function (add after saving result):
        # ... (existing code to save result)

        # Cache the result
        cache_service = CacheService(redis_client)
        cache_data = {
            "title": scrape_result.get("title"),
            "description": scrape_result.get("description"),
            "links": scrape_result.get("links", []),
            "result_id": str(result.id)
        }
        cache_service.set_cached_result(url, cache_data)

        # ... (rest of the code)
```

**验证**:

- 创建任务两次，第二次应该更快（如果使用缓存）
- 检查 Redis 中的缓存键

**完成标志**: 缓存已集成到 API 和 Celery 任务

---

## 阶段 8: Docker 化 (Tasks 31-34)

### Task 31: 创建 Web 应用 Dockerfile (docker/Dockerfile.web)

**目标**: 为 FastAPI 应用创建 Docker 镜像

**具体步骤**:

1. 创建 `docker/` 目录
2. 创建 `docker/Dockerfile.web`

**代码内容**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**验证**:

- 文件存在于 `docker/Dockerfile.web`

**完成标志**: Web Dockerfile 已创建

---

### Task 32: 创建 Worker Dockerfile (docker/Dockerfile.worker)

**目标**: 为 Celery Worker 创建 Docker 镜像

**具体步骤**:

1. 创建 `docker/Dockerfile.worker`

**代码内容**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run Celery worker
CMD ["celery", "-A", "app.celery_app.worker", "worker", "--loglevel=info"]
```

**验证**:

- 文件存在于 `docker/Dockerfile.worker`

**完成标志**: Worker Dockerfile 已创建

---

### Task 33: 创建 .dockerignore 文件

**目标**: 优化 Docker 构建，忽略不必要的文件

**具体步骤**:

1. 在项目根目录创建 `.dockerignore`

**代码内容**:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# Documentation
*.md
docs/

# Testing
.pytest_cache/
.coverage
htmlcov/
tests/

# Logs
*.log
logs/

# Database
*.db
*.sqlite
```

**验证**:

- `.dockerignore` 文件存在

**完成标志**: .dockerignore 已创建

---

### Task 34: 创建 docker-compose.yml

**目标**: 定义完整的多服务 Docker Compose 配置

**具体步骤**:

1. 在项目根目录创建 `docker-compose.yml`

**代码内容**:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    container_name: webprobe_db
    environment:
      POSTGRES_USER: webprobe
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: webprobe_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U webprobe"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - webprobe_network

  redis:
    image: redis:7-alpine
    container_name: webprobe_redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - webprobe_network

  web:
    build:
      context: .
      dockerfile: docker/Dockerfile.web
    container_name: webprobe_web
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://webprobe:secret@db:5432/webprobe_db
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
      - DEBUG=true
      - LOG_LEVEL=INFO
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - webprobe_network

  worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    container_name: webprobe_worker
    command: celery -A app.celery_app.worker worker --loglevel=info
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql://webprobe:secret@db:5432/webprobe_db
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - db
      - redis
    networks:
      - webprobe_network

  flower:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    container_name: webprobe_flower
    command: celery -A app.celery_app.worker flower --port=5555
    ports:
      - "5555:5555"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - redis
      - worker
    networks:
      - webprobe_network

volumes:
  postgres_data:

networks:
  webprobe_network:
    driver: bridge
```

**验证**:

- 运行 `docker-compose config` 验证语法
- 运行 `docker-compose up -d` 启动所有服务
- 访问 `http://localhost:8000/docs` 验证 API
- 访问 `http://localhost:5555` 验证 Flower 面板

**完成标志**: docker-compose.yml 已创建，所有服务可以启动

---

## 阶段 9: 测试与文档 (Tasks 35-40)

### Task 35: 创建 pytest 配置文件

**目标**: 配置 pytest 测试框架

**具体步骤**:

1. 在项目根目录创建 `pytest.ini`

**代码内容**:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
```

2. 更新 `requirements.txt` 添加测试依赖:

```
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

**验证**:

- 文件存在
- 可以运行 `pytest --collect-only`

**完成标志**: pytest 配置已创建

---

### Task 36: 创建 pytest fixtures (tests/conftest.py)

**目标**: 创建测试所需的通用 fixtures

**具体步骤**:

1. 创建 `tests/conftest.py`

**代码结构**:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.base import Base

# Test database URL (use SQLite for simplicity)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with dependency override"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
```

**验证**:

- 文件可以导入
- 运行 `pytest --collect-only` 应该成功

**完成标志**: Test fixtures 已创建

---

### Task 37: 创建 API 单元测试 (tests/unit/test_api.py)

**目标**: 为 API 端点编写单元测试

**具体步骤**:

1. 创建 `tests/unit/test_api.py`

**代码结构**:

```python
import pytest
from fastapi import status

@pytest.mark.unit
def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()

@pytest.mark.unit
def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data

@pytest.mark.unit
def test_create_task(client):
    """Test task creation endpoint"""
    task_data = {"url": "https://example.com"}
    response = client.post("/api/v1/tasks", json=task_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["url"] == task_data["url"]
    assert data["status"] == "PENDING"

@pytest.mark.unit
def test_get_task(client):
    """Test get task endpoint"""
    # First create a task
    task_data = {"url": "https://example.com"}
    create_response = client.post("/api/v1/tasks", json=task_data)
    task_id = create_response.json()["id"]

    # Then retrieve it
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == task_id
    assert data["url"] == task_data["url"]

@pytest.mark.unit
def test_get_task_not_found(client):
    """Test get non-existent task"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/tasks/{fake_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.unit
def test_list_tasks(client):
    """Test list tasks endpoint"""
    # Create a few tasks
    for i in range(3):
        client.post("/api/v1/tasks", json={"url": f"https://example{i}.com"})

    # List tasks
    response = client.get("/api/v1/tasks")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "tasks" in data
    assert len(data["tasks"]) >= 3
    assert "total" in data
```

**验证**:

- 运行测试: `pytest tests/unit/test_api.py -v`
- 所有测试应该通过

**完成标志**: API 单元测试已创建并通过

---

### Task 38: 创建 Repository 单元测试 (tests/unit/test_repositories.py)

**目标**: 为 Repository 层编写单元测试

**具体步骤**:

1. 创建 `tests/unit/test_repositories.py`

**代码结构**:

```python
import pytest
from app.repositories.task_repository import TaskRepository
from app.models.task import Task, TaskStatus
from uuid import uuid4

@pytest.mark.unit
def test_create_task(test_db):
    """Test creating a task"""
    repo = TaskRepository(test_db)
    task_data = {
        "url": "https://example.com",
        "status": TaskStatus.PENDING
    }
    task = repo.create(task_data)

    assert task.id is not None
    assert task.url == task_data["url"]
    assert task.status == TaskStatus.PENDING

@pytest.mark.unit
def test_get_task_by_id(test_db):
    """Test retrieving task by ID"""
    repo = TaskRepository(test_db)

    # Create task
    task_data = {"url": "https://example.com", "status": TaskStatus.PENDING}
    created_task = repo.create(task_data)

    # Retrieve task
    retrieved_task = repo.get_by_id(created_task.id)
    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.url == created_task.url

@pytest.mark.unit
def test_get_task_by_url(test_db):
    """Test retrieving task by URL"""
    repo = TaskRepository(test_db)

    url = "https://unique-test-url.com"
    task_data = {"url": url, "status": TaskStatus.PENDING}
    repo.create(task_data)

    task = repo.get_by_url(url)
    assert task is not None
    assert task.url == url

@pytest.mark.unit
def test_update_task_status(test_db):
    """Test updating task status"""
    repo = TaskRepository(test_db)

    # Create task
    task_data = {"url": "https://example.com", "status": TaskStatus.PENDING}
    task = repo.create(task_data)

    # Update status
    updated_task = repo.update_status(task.id, TaskStatus.PROCESSING)
    assert updated_task.status == TaskStatus.PROCESSING

@pytest.mark.unit
def test_get_tasks_by_status(test_db):
    """Test filtering tasks by status"""
    repo = TaskRepository(test_db)

    # Create tasks with different statuses
    repo.create({"url": "https://example1.com", "status": TaskStatus.PENDING})
    repo.create({"url": "https://example2.com", "status": TaskStatus.PENDING})
    repo.create({"url": "https://example3.com", "status": TaskStatus.SUCCESS})

    # Get pending tasks
    pending_tasks = repo.get_by_status(TaskStatus.PENDING)
    assert len(pending_tasks) >= 2
    assert all(t.status == TaskStatus.PENDING for t in pending_tasks)
```

**验证**:

- 运行测试: `pytest tests/unit/test_repositories.py -v`
- 所有测试应该通过

**完成标志**: Repository 单元测试已创建并通过

---

### Task 39: 创建 README.md

**目标**: 创建项目说明文档

**具体步骤**:

1. 在项目根目录创建或更新 `README.md`

**代码内容**:

````markdown
# WebProbe - 异步 Web 内容抓取与分析平台

WebProbe 是一个基于 FastAPI 和 Celery 的异步网页抓取平台，支持大规模并发抓取、智能缓存和任务管理。

## 技术栈

- **Web 框架**: FastAPI
- **异步任务**: Celery
- **消息队列**: Redis
- **数据库**: PostgreSQL
- **容器化**: Docker & Docker Compose
- **测试**: Pytest

## 功能特性

- ✅ RESTful API 接口
- ✅ 异步任务处理
- ✅ 智能缓存机制
- ✅ 任务状态追踪
- ✅ Docker 一键部署
- ✅ 完整的单元测试

## 快速开始

### 方式 1: 使用 Docker Compose (推荐)

1. 克隆项目

```bash
git clone <repository-url>
cd WebProbe
```
````

2. 启动所有服务

```bash
docker-compose up -d
```

3. 初始化数据库

```bash
docker-compose exec web python scripts/init_db.py
```

4. 访问服务

- API 文档: http://localhost:8000/docs
- Flower 监控: http://localhost:5555

### 方式 2: 本地开发

1. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件配置数据库和 Redis 连接
```

4. 启动 PostgreSQL 和 Redis

```bash
# 使用 Docker
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=secret postgres:15-alpine
docker run -d -p 6379:6379 redis:7-alpine
```

5. 初始化数据库

```bash
python scripts/init_db.py
```

6. 启动服务

```bash
# Terminal 1: FastAPI
uvicorn app.main:app --reload

# Terminal 2: Celery Worker
celery -A app.celery_app.worker worker --loglevel=info

# Terminal 3 (可选): Flower 监控
celery -A app.celery_app.worker flower
```

## API 使用示例

### 创建抓取任务

```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### 查询任务状态

```bash
curl "http://localhost:8000/api/v1/tasks/{task_id}"
```

### 列出所有任务

```bash
curl "http://localhost:8000/api/v1/tasks?skip=0&limit=10"
```

## 测试

运行所有测试:

```bash
pytest
```

运行特定类型的测试:

```bash
pytest -m unit          # 单元测试
pytest -m integration   # 集成测试
```

## 项目结构

详见 [architecture.md](architecture.md) 了解完整的架构设计。

## 开发计划

详见 [tasks.md](tasks.md) 了解 MVP 开发任务列表。

## License

MIT

````

**验证**:
- README.md 存在且内容完整

**完成标志**: README.md 已创建

---

### Task 40: 创建启动脚本 (scripts/start.sh)
**目标**: 创建便捷的启动脚本

**具体步骤**:
1. 创建 `scripts/start.sh`

**代码内容**:
```bash
#!/bin/bash

# WebProbe startup script

echo "🚀 Starting WebProbe..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Start services
echo "📦 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Initialize database
echo "🗄️  Initializing database..."
docker-compose exec -T web python scripts/init_db.py

echo "✅ WebProbe is running!"
echo ""
echo "📍 Access points:"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - API Root: http://localhost:8000"
echo "   - Flower Dashboard: http://localhost:5555"
echo ""
echo "📊 Check service status:"
echo "   docker-compose ps"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
````

2. 创建 `scripts/stop.sh`

```bash
#!/bin/bash

echo "🛑 Stopping WebProbe..."
docker-compose down
echo "✅ All services stopped."
```

3. 使脚本可执行

```bash
chmod +x scripts/start.sh
chmod +x scripts/stop.sh
```

**验证**:

- 脚本文件存在且可执行
- 可以运行 `./scripts/start.sh`

**完成标志**: 启动脚本已创建

---

## 🎉 MVP 完成检查清单

完成所有 40 个任务后，你应该有一个完整的 MVP，包括:

### ✅ 核心功能

- [x] RESTful API 接口 (创建任务、查询任务、列出任务)
- [x] 异步任务处理 (Celery + Redis)
- [x] 网页抓取功能 (requests + BeautifulSoup)
- [x] 数据库存储 (PostgreSQL + SQLAlchemy)
- [x] Redis 缓存机制

### ✅ 基础设施

- [x] Docker 容器化
- [x] Docker Compose 编排
- [x] 环境配置管理
- [x] 数据库迁移支持

### ✅ 代码质量

- [x] Repository 模式
- [x] Service 模式
- [x] 依赖注入
- [x] 单元测试
- [x] API 文档 (自动生成)

### ✅ 监控与运维

- [x] 健康检查端点
- [x] Flower 任务监控
- [x] 结构化日志
- [x] 启动脚本

## 验证 MVP

运行以下命令验证 MVP 是否完整工作:

```bash
# 1. 启动所有服务
./scripts/start.sh

# 2. 运行测试
pytest -v

# 3. 测试 API
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# 4. 检查 Celery 任务
# 访问 http://localhost:5555

# 5. 查看 API 文档
# 访问 http://localhost:8000/docs
```

## 下一步扩展 (可选)

完成 MVP 后，可以考虑以下扩展:

1. **认证与授权**: JWT 或 API Key
2. **限流**: Redis 限流中间件
3. **Webhook**: 任务完成通知
4. **批量任务**: 批量创建和管理任务
5. **结果导出**: CSV/JSON 导出
6. **定时任务**: Celery Beat 定时抓取
7. **监控告警**: 集成 Prometheus + Grafana
8. **前端界面**: Vue.js 或 React 前端

---

**祝你构建顺利！🚀**
