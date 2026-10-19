import uuid
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.project_repo import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectListResponse


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)

    async def create_project(self, owner_id: uuid.UUID, project_in: ProjectCreate) -> ProjectResponse:
        project = await self.project_repo.create_project(owner_id, project_in)
        return ProjectResponse.model_validate(project)

    async def get_project(self, project_id: uuid.UUID) -> ProjectResponse:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
        return ProjectResponse.model_validate(project)

    async def list_projects(
        self,
        query: Optional[str] = None,
        status_filter: Optional[str] = None,
        skill_id: Optional[uuid.UUID] = None,
        page: int = 1,
        page_size: int = 20
    ) -> ProjectListResponse:
        items, total = await self.project_repo.list_projects(
            query=query,
            status=status_filter,
            skill_id=skill_id,
            page=page,
            page_size=page_size
        )
        return ProjectListResponse(
            items=[ProjectResponse.model_validate(p) for p in items],
            total=total,
            page=page,
            page_size=page_size
        )
