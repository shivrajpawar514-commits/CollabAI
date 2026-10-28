import uuid
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.project_repo import ProjectRepository
from app.repositories.task_repo import TaskRepository
from app.repositories.advanced_ai_repo import AdvancedAIRepository
from ai.agents.pitch_deck_generator import PitchDeckGenerator, HackathonPitchDeck, ProjectPortfolioExport


class PitchDeckService:
    def __init__(self):
        self.generator = PitchDeckGenerator()

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
        completed_tasks = [t for t in tasks if t.status in ["done", "completed"]]

        adv_repo = AdvancedAIRepository(db)
        decisions = await adv_repo.list_decisions(project_id)

        # Team member count
        team_size = len(project.team.members) if (project.team and project.team.members) else 1

        milestones_list = []
        if project.milestones:
            for m in project.milestones:
                milestones_list.append({
                    "title": m.title,
                    "status": getattr(m, "status", "in_progress"),
                })

        return {
            "title": project.title,
            "description": project.description or "",
            "tags": project.tags or [],
            "skills_needed": project.skills_needed or [],
            "team_size": team_size,
            "total_tasks_count": len(tasks),
            "completed_tasks_count": len(completed_tasks),
            "milestones": milestones_list,
            "decisions": [{"what": d.what, "why": d.why} for d in decisions],
        }

    async def get_pitch_deck(self, project_id: uuid.UUID, db: AsyncSession) -> HackathonPitchDeck:
        ctx = await self._build_project_context(project_id, db)
        return await self.generator.generate_pitch_deck(ctx)

    async def get_portfolio_export(self, project_id: uuid.UUID, db: AsyncSession) -> ProjectPortfolioExport:
        ctx = await self._build_project_context(project_id, db)
        pitch_deck = await self.generator.generate_pitch_deck(ctx)
        return self.generator.generate_portfolio_export(ctx, pitch_deck=pitch_deck)
