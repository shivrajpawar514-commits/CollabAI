import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.architecture import SystemArchitectureBlueprintResponse
from app.services.architecture_service import ArchitectureService

router = APIRouter(prefix="/projects", tags=["System Architecture Blueprint"])
_architecture_service = ArchitectureService()


@router.get(
    "/{project_id}/architecture-blueprint",
    response_model=SystemArchitectureBlueprintResponse,
    summary="Get interactive System Architecture Blueprint with Mermaid diagrams",
)
async def get_architecture_blueprint(
    project_id: uuid.UUID,
    refresh: bool = Query(default=False, description="Force re-generation of blueprint"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generates a full System Architecture Blueprint including Mermaid graph TD, sequence diagrams,
    component SLAs/latency budgets, security isolation guidelines, and scale mitigations.
    """
    return await _architecture_service.get_project_blueprint(project_id, db, force_refresh=refresh)


@router.post(
    "/{project_id}/architecture-blueprint",
    response_model=SystemArchitectureBlueprintResponse,
    summary="Run new automated Architecture Blueprint synthesis",
)
async def run_architecture_blueprint(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Triggers immediate re-synthesis of the project architecture blueprint using latest workspace data.
    """
    return await _architecture_service.get_project_blueprint(project_id, db, force_refresh=True)
