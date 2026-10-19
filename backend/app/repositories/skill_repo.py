import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill


class SkillRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, category: Optional[str] = None) -> List[Skill]:
        stmt = select(Skill).order_by(Skill.name.asc())
        if category:
            stmt = stmt.where(Skill.category == category)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, skill_id: uuid.UUID) -> Optional[Skill]:
        stmt = select(Skill).where(Skill.id == skill_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Skill]:
        stmt = select(Skill).where(Skill.name.ilike(name.strip()))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, name: str, category: str = "General") -> Skill:
        existing = await self.get_by_name(name)
        if existing:
            return existing
        skill = Skill(name=name.strip(), category=category.strip())
        self.db.add(skill)
        await self.db.commit()
        await self.db.refresh(skill)
        return skill
