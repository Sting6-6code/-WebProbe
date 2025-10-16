'''
 创建任务 API 端点
 POST /tasks - 创建新任务
 GET /tasks/{task_id} - 获取单个任务
 GET /tasks - 获取任务列表

 创建任务端点
 查询任务端点
 查询任务列表端点
 查询任务详情端点
 查询任务列表端点
'''

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import Optional
from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse
from app.repositories.task_repository import TaskRepository
from app.api.v1.dependencies import get_task_repository
from app.models.task import TaskStatus

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
        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )

'''
GET /tasks/{task_id} - 获取单个任务
 GET /tasks - 获取任务列表
'''
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
        total = len(tasks) # Simple count, not efficient for large datasets
    return {
        "tasks": tasks,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }

