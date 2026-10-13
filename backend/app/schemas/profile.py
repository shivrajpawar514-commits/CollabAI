import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.skill import UserSkillResponse
from app.schemas.user import UserResponse


class ProfileBase(BaseModel):
    college: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    languages: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    preferred_roles: List[str] = Field(default_factory=list)
    availability_hours_per_week: int = Field(default=10, ge=1, le=100)
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    college: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    languages: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    preferred_roles: Optional[List[str]] = None
    availability_hours_per_week: Optional[int] = Field(default=None, ge=1, le=100)
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentProfileDetail(BaseModel):
    user: UserResponse
    profile: Optional[ProfileResponse] = None
    skills: List[UserSkillResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
