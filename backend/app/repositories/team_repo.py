import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.team import Team, TeamMember, Invitation
from app.models.user import User


class TeamRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_project_id(self, project_id: uuid.UUID) -> Optional[Team]:
        stmt = (
            select(Team)
            .where(Team.project_id == project_id)
            .options(
                selectinload(Team.members).joinedload(TeamMember.user),
                selectinload(Team.invitations).joinedload(Invitation.sender),
                selectinload(Team.invitations).joinedload(Invitation.recipient)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_team(self, project_id: uuid.UUID, name: str, owner_id: uuid.UUID) -> Team:
        team = await self.get_by_project_id(project_id)
        if not team:
            team = Team(project_id=project_id, name=name)
            self.db.add(team)
            await self.db.flush()
            # Add owner as initial member
            owner_member = TeamMember(
                team_id=team.id,
                user_id=owner_id,
                role="owner",
                role_title="Project Lead"
            )
            self.db.add(owner_member)
            await self.db.commit()
            return await self.get_by_project_id(project_id)
        return team

    async def add_member(self, team_id: uuid.UUID, user_id: uuid.UUID, role: str = "member", role_title: Optional[str] = None) -> TeamMember:
        # Check if already member
        stmt = select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
        res = await self.db.execute(stmt)
        member = res.scalar_one_or_none()
        if not member:
            member = TeamMember(team_id=team_id, user_id=user_id, role=role, role_title=role_title)
            self.db.add(member)
        else:
            member.role = role
            if role_title:
                member.role_title = role_title
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def remove_member(self, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
        res = await self.db.execute(stmt)
        member = res.scalar_one_or_none()
        if member:
            await self.db.delete(member)
            await self.db.commit()
            return True
        return False

    async def is_member(self, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = select(TeamMember.id).where(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def create_invitation(
        self,
        project_id: uuid.UUID,
        team_id: uuid.UUID,
        sender_id: uuid.UUID,
        recipient_id: Optional[uuid.UUID],
        type_: str, # 'invite' or 'join_request'
        role_name: Optional[str] = None,
        message: Optional[str] = None
    ) -> Invitation:
        invitation = Invitation(
            project_id=project_id,
            team_id=team_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            type=type_,
            role_name=role_name,
            message=message,
            status="pending"
        )
        self.db.add(invitation)
        await self.db.commit()
        await self.db.refresh(invitation)
        return invitation

    async def get_invitation_by_id(self, invitation_id: uuid.UUID) -> Optional[Invitation]:
        stmt = (
            select(Invitation)
            .where(Invitation.id == invitation_id)
            .options(
                joinedload(Invitation.sender),
                joinedload(Invitation.recipient),
                joinedload(Invitation.team),
                joinedload(Invitation.project)
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_project_invitations(self, project_id: uuid.UUID) -> List[Invitation]:
        stmt = (
            select(Invitation)
            .where(Invitation.project_id == project_id)
            .options(
                joinedload(Invitation.sender),
                joinedload(Invitation.recipient)
            )
            .order_by(Invitation.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def list_user_invitations(self, user_id: uuid.UUID) -> List[Invitation]:
        stmt = (
            select(Invitation)
            .where(Invitation.recipient_id == user_id, Invitation.status == "pending")
            .options(
                joinedload(Invitation.sender),
                joinedload(Invitation.project)
            )
            .order_by(Invitation.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_invitation_status(self, invitation_id: uuid.UUID, status: str) -> Optional[Invitation]:
        invitation = await self.get_invitation_by_id(invitation_id)
        if invitation:
            invitation.status = status
            await self.db.commit()
            await self.db.refresh(invitation)
        return invitation
