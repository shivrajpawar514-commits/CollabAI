import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.team import TeamResponse, InvitationResponse, InvitationCreate, JoinRequestCreate, InvitationUpdate
from app.services.team_service import TeamService

router = APIRouter(tags=["Teams & Invitations"])


@router.get("/projects/{project_id}/team", response_model=TeamResponse)
async def get_project_team(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get or auto-initialize team roster for a project."""
    service = TeamService(db)
    return await service.get_or_create_project_team(project_id)


@router.post("/projects/{project_id}/team/invite", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    project_id: uuid.UUID,
    inv_in: InvitationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Project owner/lead invites a student to join the team."""
    service = TeamService(db)
    return await service.send_invitation(project_id, current_user.id, inv_in)


@router.post("/projects/{project_id}/team/join-request", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def request_to_join_team(
    project_id: uuid.UUID,
    req_in: JoinRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Student sends a join request to collaborate on a project."""
    service = TeamService(db)
    return await service.create_join_request(project_id, current_user.id, req_in)


@router.get("/projects/{project_id}/team/invitations", response_model=List[InvitationResponse])
async def list_project_invitations(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """List all invitations and join requests for this project."""
    service = TeamService(db)
    items = await service.team_repo.list_project_invitations(project_id)
    return [InvitationResponse.model_validate(i) for i in items]


@router.put("/teams/invitations/{invitation_id}/respond", response_model=InvitationResponse)
async def respond_to_invitation(
    invitation_id: uuid.UUID,
    resp_in: InvitationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept or reject an invitation or join request."""
    service = TeamService(db)
    return await service.respond_to_invitation(invitation_id, current_user.id, resp_in.status)


@router.get("/users/me/invitations", response_model=List[InvitationResponse])
async def list_my_invitations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List pending project invitations received by the current student."""
    service = TeamService(db)
    items = await service.team_repo.list_user_invitations(current_user.id)
    return [InvitationResponse.model_validate(i) for i in items]
