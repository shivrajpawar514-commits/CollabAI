import uuid
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.project_repo import ProjectRepository
from app.repositories.task_repo import TaskRepository
from app.repositories.advanced_ai_repo import AdvancedAIRepository
from ai.agents.architecture_designer import ArchitectureDesigner, SystemArchitectureBlueprint

logger = logging.getLogger("collabai.services.architecture")


class ArchitectureService:
    def __init__(self):
        self.designer = ArchitectureDesigner()
        self._cache: Dict[str, SystemArchitectureBlueprint] = {}

    async def _build_project_context(self, project_id: uuid.UUID, db: AsyncSession) -> Dict[str, Any]:
        project_repo = ProjectRepository(db)
        project = await project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found",
            )

        task_repo = TaskRepository(db)
        tasks = await task_repo.list_by_project(project_id)

        adv_repo = AdvancedAIRepository(db)
        decisions = await adv_repo.list_decisions(project_id)

        return {
            "title": project.title,
            "description": project.description or "",
            "tags": project.tags or [],
            "skills_needed": project.skills_needed or [],
            "total_tasks_count": len(tasks),
            "decisions": [{"what": d.what, "why": d.why} for d in decisions],
        }

    async def get_project_blueprint(
        self, project_id: uuid.UUID, db: AsyncSession, force_refresh: bool = False
    ) -> SystemArchitectureBlueprint:
        cache_key = str(project_id)
        if not force_refresh and cache_key in self._cache:
            return self._cache[cache_key]

        context = await self._build_project_context(project_id, db)
        blueprint = await self.designer.generate_blueprint(context)
        self._cache[cache_key] = blueprint
        return blueprint
