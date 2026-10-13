import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.profile import Profile
from app.models.skill import UserSkill, Skill


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.profile),
                selectinload(User.skills).joinedload(UserSkill.skill)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.email == email.lower())
            .options(
                selectinload(User.profile),
                selectinload(User.skills).joinedload(UserSkill.skill)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_profile(self, user_id: uuid.UUID) -> Optional[Profile]:
        stmt = select(Profile).where(Profile.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_profile(self, user_id: uuid.UUID, profile_data: dict) -> Profile:
        profile = await self.get_profile(user_id)
        if not profile:
            profile = Profile(user_id=user_id, **profile_data)
            self.db.add(profile)
        else:
            for k, v in profile_data.items():
                if v is not None:
                    setattr(profile, k, v)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def get_user_skills(self, user_id: uuid.UUID) -> List[UserSkill]:
        stmt = (
            select(UserSkill)
            .where(UserSkill.user_id == user_id)
            .options(selectinload(UserSkill.skill))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def add_or_update_user_skill(self, user_id: uuid.UUID, skill_id: uuid.UUID, level: int) -> UserSkill:
        stmt = select(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
        result = await self.db.execute(stmt)
        user_skill = result.scalar_one_or_none()
        if user_skill:
            user_skill.proficiency_level = level
        else:
            user_skill = UserSkill(user_id=user_id, skill_id=skill_id, proficiency_level=level)
            self.db.add(user_skill)
        await self.db.commit()
        await self.db.refresh(user_skill)
        return user_skill

    async def delete_user_skill(self, user_id: uuid.UUID, skill_id: uuid.UUID) -> bool:
        stmt = select(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
        result = await self.db.execute(stmt)
        user_skill = result.scalar_one_or_none()
        if user_skill:
            await self.db.delete(user_skill)
            await self.db.commit()
            return True
        return False
