import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SkillBase(BaseModel):
    name: str
    category: str = "General"


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSkillCreate(BaseModel):
    skill_id: uuid.UUID
    proficiency_level: int = Field(default=3, ge=1, le=5, description="Proficiency level from 1 to 5")


class UserSkillUpdate(BaseModel):
    proficiency_level: int = Field(default=3, ge=1, le=5)


class UserSkillResponse(BaseModel):
    id: uuid.UUID
    skill_id: uuid.UUID
    skill: SkillResponse
    proficiency_level: int

    model_config = ConfigDict(from_attributes=True)
