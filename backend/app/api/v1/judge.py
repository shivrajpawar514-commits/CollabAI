import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.judge_evaluation import HackathonJudgeEvaluationResponse
from app.services.judge_evaluation_service import JudgeEvaluationService

router = APIRouter(prefix="/projects", tags=["Hackathon Judge Evaluation"])
_judge_service = JudgeEvaluationService()


@router.get(
    "/{project_id}/judge-eval",
    response_model=HackathonJudgeEvaluationResponse,
    summary="Get simulated Hackathon Judge Evaluation & 5-criteria rubric scorecard",
)
async def get_judge_evaluation(
    project_id: uuid.UUID,
    refresh: bool = Query(default=False, description="Force re-generation of evaluation"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Rigorously evaluates project milestones, architecture decisions, and task delivery against
    the official 5-pillar hackathon rubric (Innovation, Technical Architecture, Practical Impact,
    UI/UX Polish, Completeness & Execution).
    """
    return await _judge_service.evaluate_project(project_id, db, force_refresh=refresh)


@router.post(
    "/{project_id}/judge-eval",
    response_model=HackathonJudgeEvaluationResponse,
    summary="Run new automated Hackathon Judge Evaluation simulation",
)
async def run_judge_evaluation(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Triggers an immediate evaluation run using the latest project workspace context.
    """
    return await _judge_service.evaluate_project(project_id, db, force_refresh=True)
