import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse


class TeamMemberBase(BaseModel):
    role: str = Field(default="member", description="'owner', 'lead', 'member'")
    role_title: Optional[str] = None


class TeamMemberAdd(TeamMemberBase):
    user_id: uuid.UUID


class TeamMemberResponse(TeamMemberBase):
    id: uuid.UUID
    team_id: uuid.UUID
    user_id: uuid.UUID
    user: UserResponse
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeamBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: Optional[str] = None


class TeamResponse(TeamBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    members: List[TeamMemberResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class InvitationCreate(BaseModel):
    recipient_id: uuid.UUID
    role_name: Optional[str] = None
    message: Optional[str] = None


class JoinRequestCreate(BaseModel):
    role_name: Optional[str] = None
    message: Optional[str] = None


class InvitationUpdate(BaseModel):
    status: str = Field(description="'accepted' or 'rejected'")


class InvitationResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    team_id: uuid.UUID
    sender_id: uuid.UUID
    recipient_id: Optional[uuid.UUID] = None
    type: str
    role_name: Optional[str] = None
    message: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    sender: UserResponse
    recipient: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
