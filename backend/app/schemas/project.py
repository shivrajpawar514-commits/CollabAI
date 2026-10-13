import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.user import UserResponse
from app.schemas.skill import SkillResponse


class ProjectRoleBase(BaseModel):
    role_name: str
    capacity: int = Field(default=1, ge=1)


class ProjectRoleCreate(ProjectRoleBase):
    pass


class ProjectRoleResponse(ProjectRoleBase):
    id: uuid.UUID
    project_id: uuid.UUID
    filled_count: int

    model_config = ConfigDict(from_attributes=True)


class ProjectSkillCreate(BaseModel):
    skill_id: uuid.UUID
    is_required: bool = True


class ProjectSkillResponse(BaseModel):
    id: uuid.UUID
    skill_id: uuid.UUID
    skill: SkillResponse
    is_required: bool

    model_config = ConfigDict(from_attributes=True)


class ProjectBase(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    problem_statement: Optional[str] = None
    max_team_size: int = Field(default=4, ge=1, le=20)
    repo_url: Optional[str] = None
    demo_url: Optional[str] = None


class ProjectCreate(ProjectBase):
    status: str = Field(default="recruiting")
    skills: List[ProjectSkillCreate] = Field(default_factory=list)
    roles: List[ProjectRoleCreate] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    problem_statement: Optional[str] = None
    status: Optional[str] = None
    max_team_size: Optional[int] = None
    repo_url: Optional[str] = None
    demo_url: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    owner: UserResponse
    status: str
    created_at: datetime
    updated_at: datetime
    required_skills: List[ProjectSkillResponse] = Field(default_factory=list)
    roles: List[ProjectRoleResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
