import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.task import (
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    TaskCreate, TaskUpdate, TaskMove, TaskResponse, TaskDetailResponse,
    TaskCommentCreate, TaskCommentResponse
)
from app.services.task_service import TaskService

router = APIRouter(tags=["Tasks, Milestones & Kanban"])


# Milestones
@router.get("/projects/{project_id}/milestones", response_model=List[MilestoneResponse])
async def list_milestones(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """List project roadmap milestones."""
    service = TaskService(db)
    return await service.get_milestones(project_id)


@router.post("/projects/{project_id}/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    project_id: uuid.UUID,
    m_in: MilestoneCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a new milestone to the project roadmap."""
    service = TaskService(db)
    return await service.create_milestone(project_id, current_user.id, m_in)


@router.put("/projects/{project_id}/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    project_id: uuid.UUID,
    milestone_id: uuid.UUID,
    m_in: MilestoneUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a milestone's title, status, or deadline."""
    service = TaskService(db)
    return await service.update_milestone(project_id, milestone_id, current_user.id, m_in)


# Tasks
@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def list_tasks(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """List all Kanban tasks for a project."""
    service = TaskService(db)
    return await service.get_tasks(project_id)


@router.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: uuid.UUID,
    t_in: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task with priority, estimated hours, and assignee."""
    service = TaskService(db)
    return await service.create_task(project_id, current_user.id, t_in)


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task_detail(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get task details with threaded comments and milestone information."""
    service = TaskService(db)
    return await service.get_task_detail(task_id)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    t_in: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update task fields."""
    service = TaskService(db)
    task = await service.task_repo.get_task_by_id(task_id)
    if not task:
        raise status.HTTP_404_NOT_FOUND
    return await service.update_task(task.project_id, task_id, current_user.id, t_in)


@router.patch("/tasks/{task_id}/move", response_model=TaskResponse)
async def move_task(
    task_id: uuid.UUID,
    move_in: TaskMove,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Kanban drag & drop endpoint: move task to a different status column and position."""
    service = TaskService(db)
    task = await service.task_repo.get_task_by_id(task_id)
    if not task:
        raise status.HTTP_404_NOT_FOUND
    return await service.move_task(task.project_id, task_id, current_user.id, move_in)


@router.post("/tasks/{task_id}/comments", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED)
async def add_task_comment(
    task_id: uuid.UUID,
    c_in: TaskCommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Post a comment on a task."""
    service = TaskService(db)
    task = await service.task_repo.get_task_by_id(task_id)
    if not task:
        raise status.HTTP_404_NOT_FOUND
    return await service.add_comment(task.project_id, task_id, current_user.id, c_in)
