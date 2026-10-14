import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse


class MilestoneBase(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    order_index: int = 0
    status: str = Field(default="pending", description="'pending', 'in_progress', 'completed'")


class MilestoneCreate(MilestoneBase):
    pass


class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    order_index: Optional[int] = None
    status: Optional[str] = None


class MilestoneResponse(MilestoneBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskCommentBase(BaseModel):
    content: str = Field(min_length=1)


class TaskCommentCreate(TaskCommentBase):
    pass


class TaskCommentResponse(TaskCommentBase):
    id: uuid.UUID
    task_id: uuid.UUID
    user_id: uuid.UUID
    user: UserResponse
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskDependencyResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    depends_on_task_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: Optional[str] = None
    status: str = Field(default="todo", description="'backlog', 'todo', 'in_progress', 'review', 'completed'")
    priority: str = Field(default="medium", description="'low', 'medium', 'high', 'urgent'")
    deadline: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    order_index: int = 0
    milestone_id: Optional[uuid.UUID] = None
    assignee_id: Optional[uuid.UUID] = None


class TaskCreate(TaskBase):
    dependency_ids: List[uuid.UUID] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    deadline: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    order_index: Optional[int] = None
    milestone_id: Optional[uuid.UUID] = None
    assignee_id: Optional[uuid.UUID] = None


class TaskMove(BaseModel):
    status: str = Field(description="'backlog', 'todo', 'in_progress', 'review', 'completed'")
    order_index: int = 0


class TaskResponse(TaskBase):
    id: uuid.UUID
    project_id: uuid.UUID
    creator_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    assignee: Optional[UserResponse] = None
    creator: UserResponse
    comments_count: int = 0
    dependencies: List[TaskDependencyResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class TaskDetailResponse(TaskResponse):
    comments: List[TaskCommentResponse] = Field(default_factory=list)
    milestone: Optional[MilestoneResponse] = None

    model_config = ConfigDict(from_attributes=True)
