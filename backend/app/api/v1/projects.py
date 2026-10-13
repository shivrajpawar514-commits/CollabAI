import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectListResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    q: Optional[str] = Query(None, description="Search keyword in title, description, or problem statement"),
    status: Optional[str] = Query(None, description="Filter by status (e.g. 'recruiting')"),
    skill_id: Optional[uuid.UUID] = Query(None, description="Filter by required skill ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Discover projects with keyword search and skill/status filters."""
    service = ProjectService(db)
    return await service.list_projects(
        query=q,
        status_filter=status,
        skill_id=skill_id,
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new student project with required skills and open roles."""
    service = ProjectService(db)
    return await service.create_project(current_user.id, project_in)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve full project details by ID."""
    service = ProjectService(db)
    return await service.get_project(project_id)
