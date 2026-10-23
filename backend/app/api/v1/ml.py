import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.ml_service import MLService
from app.schemas.ml import (
    RecommendationFeedbackCreate,
    RecommendationFeedbackResponse,
    TeammateMatchV2Response,
    DeadlineRiskReport,
    SkillGapAnalysis,
)

router = APIRouter(prefix="", tags=["ML Intelligence & Optimization"])
ml_service = MLService()


@router.get(
    "/projects/{project_id}/intelligence/teammates",
    response_model=TeammateMatchV2Response,
    status_code=status.HTTP_200_OK,
)
async def get_teammate_recommendations_v2(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Candidate Recommendation Engine v2 & v3:
    Uses dense vector candidate pre-filtering, weighted skill gap complementarity scoring,
    and XGBoost gradient-boosted ranking with feature attribution.
    """
    return await ml_service.get_recommendations_v2(
        project_id=project_id,
        db=db,
    )


@router.get(
    "/projects/{project_id}/intelligence/deadline-risk",
    response_model=DeadlineRiskReport,
    status_code=status.HTTP_200_OK,
)
async def predict_deadline_risk(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sprint Deadline Risk & Velocity Forecast:
    Gradient-boosted sprint classification analyzing remaining tasks, days left,
    blocked task dependencies, team size, and historical velocity to predict slip and bottlenecks.
    """
    return await ml_service.predict_deadline_risk(
        project_id=project_id,
        db=db,
    )


@router.get(
    "/projects/{project_id}/intelligence/skill-gap",
    response_model=SkillGapAnalysis,
    status_code=status.HTTP_200_OK,
)
async def analyze_team_skill_gap(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    NetworkX Skill Graph & Skill Gap Learning Path:
    Traverses the skill prerequisite DAG to generate an ordered, step-by-step curriculum
    with curated free open-access learning resources (official docs, freeCodeCamp, MIT OCW).
    """
    return await ml_service.analyze_skill_gap(
        project_id=project_id,
        db=db,
    )


@router.post(
    "/projects/{project_id}/intelligence/feedback",
    response_model=RecommendationFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def log_recommendation_feedback(
    project_id: uuid.UUID,
    feedback: RecommendationFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Log user interaction telemetry on teammate recommendations (accepted, invited, dismissed)
    to drive continuous model retraining and calibration in the XGBoost ranking loop.
    """
    return await ml_service.log_feedback(
        project_id=project_id,
        reviewer_id=current_user.id,
        data=feedback,
        db=db,
    )
