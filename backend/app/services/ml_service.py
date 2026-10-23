import os
import sys
import uuid
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ai.ml.matching_v2 import MatchingEngineV2, CandidateMatchV2
from ai.ml.deadline_risk import DeadlineRiskPredictor, DeadlineRiskReport
from ai.ml.skill_graph import SkillGraphEngine, SkillGapAnalysis

from app.models.project import Project
from app.models.team import Team
from app.repositories.ml_repo import MLRepository
from app.repositories.project_repo import ProjectRepository
from app.schemas.ml import (
    RecommendationFeedbackCreate,
    RecommendationFeedbackResponse,
    TeammateMatchV2Response,
)

logger = logging.getLogger("collabai.ml")


class MLService:
    def __init__(self):
        self.skill_graph = SkillGraphEngine()

    async def get_recommendations_v2(
        self,
        project_id: uuid.UUID,
        db: AsyncSession,
    ) -> TeammateMatchV2Response:
        project_repo = ProjectRepository(db)
        project = await project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        ml_repo = MLRepository(db)
        required_skills, team_skills = await ml_repo.get_project_skills_and_team_skills(project_id)

        # Team member IDs to exclude
        exclude_ids = [project.owner_id]
        if project.team and project.team.members:
            exclude_ids.extend([m.user_id for m in project.team.members])

        candidates_raw = await ml_repo.get_candidate_students(exclude_user_ids=exclude_ids, limit=60)

        project_dict = {
            "id": str(project.id),
            "title": project.title,
            "description": project.description,
            "problem_statement": project.problem_statement or "",
            "required_skills": required_skills,
            "roles": [r.role_name for r in (project.roles or [])],
            "college": project.owner.profile.college if (project.owner and project.owner.profile) else None,
        }

        matches: List[CandidateMatchV2] = []
        for cand in candidates_raw:
            match_v2 = MatchingEngineV2.compute_match_v2(
                project_dict=project_dict,
                candidate=cand,
                existing_team_skills=team_skills,
            )
            matches.append(match_v2)

        # Sort primarily by ML rank score (XGBoost), secondarily by weighted score
        matches.sort(key=lambda m: (m.ml_rank_score, m.match_score), reverse=True)

        return TeammateMatchV2Response(
            project_id=project.id,
            project_title=project.title,
            recommendations=matches[:20],
            total_analyzed=len(candidates_raw),
        )

    async def predict_deadline_risk(
        self,
        project_id: uuid.UUID,
        db: AsyncSession,
    ) -> DeadlineRiskReport:
        project_repo = ProjectRepository(db)
        project = await project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        ml_repo = MLRepository(db)
        metrics = await ml_repo.get_project_sprint_metrics(project_id)

        return DeadlineRiskPredictor.predict_risk(
            project_id=str(project.id),
            total_tasks=metrics["total_tasks"],
            completed_tasks=metrics["completed_tasks"],
            blocked_tasks=metrics["blocked_tasks"],
            days_left=metrics["days_left"],
            team_size=metrics["team_size"],
            recent_weekly_velocity=metrics["recent_weekly_velocity"],
        )

    async def analyze_skill_gap(
        self,
        project_id: uuid.UUID,
        db: AsyncSession,
    ) -> SkillGapAnalysis:
        project_repo = ProjectRepository(db)
        project = await project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        ml_repo = MLRepository(db)
        required_skills, team_skills = await ml_repo.get_project_skills_and_team_skills(project_id)

        # If project has no skills listed, fallback to common foundational stack based on title
        if not required_skills:
            title_lower = project.title.lower()
            if "ai" in title_lower or "ml" in title_lower or "rag" in title_lower:
                required_skills = ["python", "fastapi", "pgvector", "machine learning", "rag"]
            else:
                required_skills = ["react", "next.js", "typescript", "fastapi", "postgresql"]

        return self.skill_graph.analyze_skill_gap(
            project_id=str(project.id),
            required_skills=required_skills,
            team_owned_skills=list(team_skills),
        )

    async def log_feedback(
        self,
        project_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        data: RecommendationFeedbackCreate,
        db: AsyncSession,
    ) -> RecommendationFeedbackResponse:
        ml_repo = MLRepository(db)
        fb = await ml_repo.log_feedback(
            project_id=project_id,
            reviewer_id=reviewer_id,
            candidate_id=data.candidate_id,
            action=data.action,
            match_score=data.match_score,
            ml_rank_score=data.ml_rank_score,
            feature_vector_json=data.feature_vector_json,
        )
        return RecommendationFeedbackResponse.model_validate(fb)
