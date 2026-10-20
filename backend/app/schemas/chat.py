import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse


class MessageCreate(BaseModel):
    content: str = Field(min_length=1)
    is_pinned: bool = False


class MessageResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    mentions: List[str] = Field(default_factory=list)
    is_pinned: bool
    created_at: datetime
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)


class FileAttachmentResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    uploader_id: uuid.UUID
    file_name: str
    file_url: str
    file_size_bytes: int
    content_type: str
    created_at: datetime
    uploader: UserResponse

    model_config = ConfigDict(from_attributes=True)
