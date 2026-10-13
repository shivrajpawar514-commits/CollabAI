import uuid
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.repositories.skill_repo import SkillRepository
from app.schemas.profile import ProfileUpdate, ProfileResponse, StudentProfileDetail
from app.schemas.user import UserResponse
from app.schemas.skill import UserSkillResponse, UserSkillCreate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.skill_repo = SkillRepository(db)

    async def get_student_profile(self, user_id: uuid.UUID) -> StudentProfileDetail:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student user not found.")

        profile = await self.user_repo.get_profile(user_id)
        skills = await self.user_repo.get_user_skills(user_id)

        return StudentProfileDetail(
            user=UserResponse.model_validate(user),
            profile=ProfileResponse.model_validate(profile) if profile else None,
            skills=[UserSkillResponse.model_validate(s) for s in skills]
        )

    async def update_profile(self, user_id: uuid.UUID, update_in: ProfileUpdate) -> ProfileResponse:
        data = update_in.model_dump(exclude_unset=True)
        updated_profile = await self.user_repo.upsert_profile(user_id, data)
        return ProfileResponse.model_validate(updated_profile)

    async def add_or_update_skill(self, user_id: uuid.UUID, skill_in: UserSkillCreate) -> UserSkillResponse:
        skill = await self.skill_repo.get_by_id(skill_in.skill_id)
        if not skill:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill does not exist.")

        user_skill = await self.user_repo.add_or_update_user_skill(
            user_id=user_id,
            skill_id=skill_in.skill_id,
            level=skill_in.proficiency_level
        )
        return UserSkillResponse.model_validate(user_skill)

    async def remove_skill(self, user_id: uuid.UUID, skill_id: uuid.UUID) -> bool:
        removed = await self.user_repo.delete_user_skill(user_id, skill_id)
        if not removed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found on student profile.")
        return True
