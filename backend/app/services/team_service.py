import uuid
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team, TeamMember, Invitation
from app.repositories.team_repo import TeamRepository
from app.repositories.project_repo import ProjectRepository
from app.repositories.notification_repo import NotificationRepository
from app.repositories.user_repo import UserRepository
from app.schemas.team import TeamResponse, InvitationResponse, InvitationCreate, JoinRequestCreate
from app.core.ws import ws_manager


class TeamService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.team_repo = TeamRepository(db)
        self.project_repo = ProjectRepository(db)
        self.notif_repo = NotificationRepository(db)
        self.user_repo = UserRepository(db)

    async def get_or_create_project_team(self, project_id: uuid.UUID) -> TeamResponse:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

        team = await self.team_repo.get_or_create_team(
            project_id=project_id,
            name=f"{project.title} Team",
            owner_id=project.owner_id
        )
        return TeamResponse.model_validate(team)

    async def send_invitation(self, project_id: uuid.UUID, sender_id: uuid.UUID, inv_in: InvitationCreate) -> InvitationResponse:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

        team = await self.team_repo.get_or_create_team(project_id, f"{project.title} Team", project.owner_id)

        # Verify sender is authorized (project owner or team lead)
        if project.owner_id != sender_id:
            # Check if sender is team lead
            is_mem = await self.team_repo.is_member(team.id, sender_id)
            if not is_mem:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only team members can invite teammates.")

        # Create invitation
        inv = await self.team_repo.create_invitation(
            project_id=project_id,
            team_id=team.id,
            sender_id=sender_id,
            recipient_id=inv_in.recipient_id,
            type_="invite",
            role_name=inv_in.role_name,
            message=inv_in.message
        )

        # Notify recipient
        sender = await self.user_repo.get_by_id(sender_id)
        sender_name = sender.full_name if sender else "A team lead"
        notif = await self.notif_repo.create_notification(
            user_id=inv_in.recipient_id,
            actor_id=sender_id,
            title=f"Invitation to join {project.title}",
            message=f"{sender_name} invited you to join '{project.title}' as {inv_in.role_name or 'a team member'}.",
            type_="invite",
            link=f"/projects/{project_id}/workspace"
        )
        await ws_manager.send_to_user(str(inv_in.recipient_id), "notification", {
            "id": str(notif.id),
            "title": notif.title,
            "message": notif.message,
            "type": notif.type
        })

        return InvitationResponse.model_validate(await self.team_repo.get_invitation_by_id(inv.id))

    async def create_join_request(self, project_id: uuid.UUID, student_id: uuid.UUID, req_in: JoinRequestCreate) -> InvitationResponse:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

        team = await self.team_repo.get_or_create_team(project_id, f"{project.title} Team", project.owner_id)

        # Check if already a member
        if await self.team_repo.is_member(team.id, student_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are already a member of this team.")

        inv = await self.team_repo.create_invitation(
            project_id=project_id,
            team_id=team.id,
            sender_id=student_id,
            recipient_id=project.owner_id,
            type_="join_request",
            role_name=req_in.role_name,
            message=req_in.message
        )

        # Notify project owner
        applicant = await self.user_repo.get_by_id(student_id)
        app_name = applicant.full_name if applicant else "A student"
        notif = await self.notif_repo.create_notification(
            user_id=project.owner_id,
            actor_id=student_id,
            title=f"New Join Request for {project.title}",
            message=f"{app_name} applied to join as {req_in.role_name or 'collaborator'}.",
            type_="join_request",
            link=f"/projects/{project_id}/workspace?tab=team"
        )
        await ws_manager.send_to_user(str(project.owner_id), "notification", {
            "id": str(notif.id),
            "title": notif.title,
            "message": notif.message,
            "type": notif.type
        })

        return InvitationResponse.model_validate(await self.team_repo.get_invitation_by_id(inv.id))

    async def respond_to_invitation(self, invitation_id: uuid.UUID, user_id: uuid.UUID, new_status: str) -> InvitationResponse:
        inv = await self.team_repo.get_invitation_by_id(invitation_id)
        if not inv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found.")

        # Check permissions
        if inv.type == "invite":
            # Recipient must be the user responding
            if inv.recipient_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the invitee can respond.")
        elif inv.type == "join_request":
            # Project owner / team lead must be the user responding
            project = await self.project_repo.get_by_id(inv.project_id)
            if project.owner_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the project lead can accept join requests.")

        updated_inv = await self.team_repo.update_invitation_status(invitation_id, new_status)

        if new_status == "accepted":
            joining_user_id = inv.recipient_id if inv.type == "invite" else inv.sender_id
            await self.team_repo.add_member(
                team_id=inv.team_id,
                user_id=joining_user_id,
                role="member",
                role_title=inv.role_name or "Engineer"
            )

            # Log activity
            joining_user = await self.user_repo.get_by_id(joining_user_id)
            jname = joining_user.full_name if joining_user else "New member"
            await self.notif_repo.log_activity(
                project_id=inv.project_id,
                user_id=joining_user_id,
                action="member_joined",
                entity_type="team",
                description=f"{jname} joined the team as {inv.role_name or 'Member'}."
            )

            # Broadcast to team
            await ws_manager.broadcast_to_project(str(inv.project_id), "team_updated", {
                "user_id": str(joining_user_id),
                "name": jname,
                "role": inv.role_name
            })

        return InvitationResponse.model_validate(updated_inv)
