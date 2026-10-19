import uuid
from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.project import Project, ProjectSkill, ProjectRole
from app.models.skill import Skill
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, project_id: uuid.UUID) -> Optional[Project]:
        stmt = (
            select(Project)
            .where(Project.id == project_id)
            .options(
                joinedload(Project.owner),
                selectinload(Project.required_skills).joinedload(ProjectSkill.skill),
                selectinload(Project.roles)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_projects(
        self,
        query: Optional[str] = None,
        status: Optional[str] = None,
        skill_id: Optional[uuid.UUID] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Project], int]:
        stmt = (
            select(Project)
            .options(
                joinedload(Project.owner),
                selectinload(Project.required_skills).joinedload(ProjectSkill.skill),
                selectinload(Project.roles)
            )
        )

        count_stmt = select(func.count(Project.id))

        if query:
            search_filter = or_(
                Project.title.ilike(f"%{query}%"),
                Project.description.ilike(f"%{query}%"),
                Project.problem_statement.ilike(f"%{query}%")
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        if status:
            stmt = stmt.where(Project.status == status)
            count_stmt = count_stmt.where(Project.status == status)

        if skill_id:
            skill_filter = Project.required_skills.any(ProjectSkill.skill_id == skill_id)
            stmt = stmt.where(skill_filter)
            count_stmt = count_stmt.where(skill_filter)

        total_res = await self.db.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = stmt.order_by(Project.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items_res = await self.db.execute(stmt)
        items = list(items_res.scalars().all())

        return items, total

    async def create_project(self, owner_id: uuid.UUID, project_in: ProjectCreate) -> Project:
        project = Project(
            title=project_in.title,
            description=project_in.description,
            problem_statement=project_in.problem_statement,
            owner_id=owner_id,
            status=project_in.status,
            max_team_size=project_in.max_team_size,
            repo_url=project_in.repo_url,
            demo_url=project_in.demo_url
        )
        self.db.add(project)
        await self.db.flush()

        # Add skills
        for s in project_in.skills:
            ps = ProjectSkill(
                project_id=project.id,
                skill_id=s.skill_id,
                is_required=s.is_required
            )
            self.db.add(ps)

        # Add roles
        for r in project_in.roles:
            pr = ProjectRole(
                project_id=project.id,
                role_name=r.role_name,
                capacity=r.capacity
            )
            self.db.add(pr)

        await self.db.commit()
        await self.db.refresh(project)
        return await self.get_by_id(project.id) # Re-fetch with all eager relationships
