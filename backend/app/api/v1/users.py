import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.profile import ProfileUpdate, ProfileResponse, StudentProfileDetail
from app.schemas.skill import UserSkillCreate, UserSkillResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users & Profiles"])


@router.get("/me/profile", response_model=StudentProfileDetail)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the current student's complete profile with skills."""
    service = UserService(db)
    return await service.get_student_profile(current_user.id)


@router.put("/me/profile", response_model=ProfileResponse)
async def update_my_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update student profile attributes."""
    service = UserService(db)
    return await service.update_profile(current_user.id, profile_in)


@router.post("/me/skills", response_model=UserSkillResponse)
async def add_or_update_my_skill(
    skill_in: UserSkillCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Add or update proficiency level (1-5) for a technical skill."""
    service = UserService(db)
    return await service.add_or_update_skill(current_user.id, skill_in)


@router.delete("/me/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_my_skill(
    skill_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a skill from the student's profile."""
    service = UserService(db)
    await service.remove_skill(current_user.id, skill_id)
    return None


@router.get("/{user_id}/profile", response_model=StudentProfileDetail)
async def get_user_profile_by_id(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Inspect another student's profile and skills."""
    service = UserService(db)
    return await service.get_student_profile(user_id)
