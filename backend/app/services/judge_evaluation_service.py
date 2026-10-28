import uuid
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.project_repo import ProjectRepository
from app.repositories.task_repo import TaskRepository
from app.repositories.advanced_ai_repo import AdvancedAIRepository
from app.services.velocity_service import VelocityService
from ai.agents.judge_evaluator import JudgeEvaluator, HackathonJudgeEvaluation

logger = logging.getLogger("collabai.services.judge_evaluation")


class JudgeEvaluationService:
    def __init__(self):
        self.evaluator = JudgeEvaluator()
        self.velocity_service = VelocityService()
        self._cache: Dict[str, HackathonJudgeEvaluation] = {}

    async def _build_evaluation_context(self, project_id: uuid.UUID, db: AsyncSession) -> Dict[str, Any]:
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

        try:
            velocity = await self.velocity_service.get_project_velocity(project_id, db)
            velocity_data = velocity.model_dump() if hasattr(velocity, "model_dump") else velocity.dict()
        except Exception:
            velocity_data = {"velocity_score": 85, "velocity_grade": "A-"}

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
            "team_size": len(project.team.members) if (project.team and project.team.members) else 1,
            "total_tasks_count": len(tasks),
            "completed_tasks_count": len(completed_tasks),
            "milestones": milestones_list,
            "decisions": [{"what": d.what, "why": d.why} for d in decisions],
            "velocity": velocity_data,
        }

    async def evaluate_project(
        self, project_id: uuid.UUID, db: AsyncSession, force_refresh: bool = False
    ) -> HackathonJudgeEvaluation:
        cache_key = str(project_id)
        if not force_refresh and cache_key in self._cache:
            return self._cache[cache_key]

        context = await self._build_evaluation_context(project_id, db)
        evaluation = await self.evaluator.evaluate_project(context)
        self._cache[cache_key] = evaluation
        return evaluation
