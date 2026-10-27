import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.velocity import SprintVelocityMetricsResponse
from app.services.velocity_service import VelocityService

router = APIRouter(prefix="/projects", tags=["Sprint Velocity & Burndown"])
_velocity_service = VelocityService()


@router.get(
    "/{project_id}/velocity",
    response_model=SprintVelocityMetricsResponse,
    summary="Compute sprint velocity, burndown curve, and health score",
)
async def get_project_velocity(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns live sprint velocity metrics: completion rates, remaining hours,
    7-day burndown chart, milestone progress items, and AI recommendations.
    """
    return await _velocity_service.compute_project_velocity(project_id, db)
