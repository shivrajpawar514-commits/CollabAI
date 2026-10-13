from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.repositories.skill_repo import SkillRepository
from app.schemas.skill import SkillResponse, SkillCreate

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("/", response_model=List[SkillResponse])
async def list_skills(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List available technical and domain skills."""
    repo = SkillRepository(db)
    skills = await repo.get_all(category=category)
    return [SkillResponse.model_validate(s) for s in skills]


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_in: SkillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a new skill to the taxonomy."""
    repo = SkillRepository(db)
    skill = await repo.create(name=skill_in.name, category=skill_in.category)
    return SkillResponse.model_validate(skill)
