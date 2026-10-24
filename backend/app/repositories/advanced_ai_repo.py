import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.advanced_ai import MeetingNote, MeetingActionItem, ProjectDecision
from app.models.task import Task, Milestone
from app.models.project import Project
from app.models.team import Team, TeamMember
from app.models.user import User
from app.models.rag import Document
from app.schemas.advanced_ai import DecisionCreate


class AdvancedAIRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # 1. Meetings & Action Items
    async def create_meeting_note_with_actions(
        self,
        project_id: uuid.UUID,
        organizer_id: uuid.UUID,
        title: str,
        raw_transcript: str,
        executive_summary: str,
        key_topics: List[str],
        overall_sentiment: str,
        action_items: List[Dict[str, Any]],
    ) -> MeetingNote:
        note = MeetingNote(
            project_id=project_id,
            organizer_id=organizer_id,
            title=title,
            raw_transcript=raw_transcript,
            executive_summary=executive_summary,
            key_topics_json=key_topics,
            overall_sentiment=overall_sentiment,
        )
        self.db.add(note)
        await self.db.flush()

        for item in action_items:
            action_item = MeetingActionItem(
                meeting_id=note.id,
                project_id=project_id,
                title=item.get("title", "Action item"),
                description=item.get("description", ""),
                suggested_assignee=item.get("suggested_assignee"),
                priority=item.get("priority", "medium"),
                estimated_hours=int(item.get("estimated_hours", 4)),
                is_converted=False,
            )
            self.db.add(action_item)

        await self.db.commit()
        await self.db.refresh(note)

        # Reload with action items
        stmt = (
            select(MeetingNote)
            .where(MeetingNote.id == note.id)
            .options(selectinload(MeetingNote.action_items))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def get_project_meetings(self, project_id: uuid.UUID) -> List[MeetingNote]:
        stmt = (
            select(MeetingNote)
            .where(MeetingNote.project_id == project_id)
            .options(selectinload(MeetingNote.action_items))
            .order_by(MeetingNote.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_meeting_note_by_id(self, meeting_id: uuid.UUID) -> Optional[MeetingNote]:
        stmt = (
            select(MeetingNote)
            .where(MeetingNote.id == meeting_id)
            .options(selectinload(MeetingNote.action_items))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def convert_action_items_to_tasks(
        self,
        project_id: uuid.UUID,
        creator_id: uuid.UUID,
        action_item_ids: List[uuid.UUID],
        target_milestone_id: Optional[uuid.UUID] = None,
    ) -> List[Task]:
        stmt = (
            select(MeetingActionItem)
            .where(
                MeetingActionItem.project_id == project_id,
                MeetingActionItem.id.in_(action_item_ids),
                MeetingActionItem.is_converted.is_(False),
            )
        )
        res = await self.db.execute(stmt)
        items_to_convert = list(res.scalars().all())

        created_tasks: List[Task] = []
        for index, item in enumerate(items_to_convert):
            task = Task(
                project_id=project_id,
                creator_id=creator_id,
                title=item.title,
                description=f"{item.description}\n\n*Generated from Meeting Action Item (suggested assignee: {item.suggested_assignee or 'unassigned'})*",
                status="backlog",
                priority=item.priority or "medium",
                estimated_hours=item.estimated_hours or 4,
                milestone_id=target_milestone_id,
                order_index=index,
            )
            self.db.add(task)
            await self.db.flush()

            item.is_converted = True
            item.converted_task_id = task.id
            created_tasks.append(task)

        await self.db.commit()

        # Reload created tasks with relations
        task_ids = [t.id for t in created_tasks]
        if not task_ids:
            return []

        reload_stmt = (
            select(Task)
            .where(Task.id.in_(task_ids))
            .options(
                joinedload(Task.assignee),
                joinedload(Task.creator),
                joinedload(Task.milestone),
                selectinload(Task.dependencies),
            )
        )
        reload_res = await self.db.execute(reload_stmt)
        return list(reload_res.scalars().all())

    # 2. Decision Records
    async def create_decision(
        self,
        project_id: uuid.UUID,
        recorder_id: uuid.UUID,
        d_in: DecisionCreate,
    ) -> ProjectDecision:
        decision = ProjectDecision(
            project_id=project_id,
            recorder_id=recorder_id,
            what=d_in.what,
            why=d_in.why,
            who=d_in.who or "Team Consensus",
            alternatives_json=d_in.alternatives or [],
            tags_json=d_in.tags or [],
            linked_task_id=d_in.linked_task_id,
            linked_document_id=d_in.linked_document_id,
        )
        self.db.add(decision)
        await self.db.commit()
        await self.db.refresh(decision)
        return decision

    async def get_project_decisions(self, project_id: uuid.UUID) -> List[ProjectDecision]:
        stmt = (
            select(ProjectDecision)
            .where(ProjectDecision.project_id == project_id)
            .order_by(ProjectDecision.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # 3. Context aggregator for Orchestrator & Project Readiness
    async def get_project_context(self, project_id: uuid.UUID) -> Dict[str, Any]:
        # Project info
        p_stmt = select(Project).where(Project.id == project_id)
        p_res = await self.db.execute(p_stmt)
        project = p_res.scalar_one_or_none()

        # Milestones
        m_stmt = (
            select(Milestone)
            .where(Milestone.project_id == project_id)
            .order_by(Milestone.order_index.asc())
        )
        m_res = await self.db.execute(m_stmt)
        milestones = list(m_res.scalars().all())

        # Tasks
        t_stmt = select(Task).where(Task.project_id == project_id)
        t_res = await self.db.execute(t_stmt)
        tasks = list(t_res.scalars().all())

        # Documents
        d_stmt = select(Document).where(Document.project_id == project_id)
        d_res = await self.db.execute(d_stmt)
        documents = list(d_res.scalars().all())

        # Decisions
        dec_stmt = select(ProjectDecision).where(ProjectDecision.project_id == project_id)
        dec_res = await self.db.execute(dec_stmt)
        decisions = list(dec_res.scalars().all())

        # Team members
        tm_stmt = (
            select(TeamMember)
            .join(Team, TeamMember.team_id == Team.id)
            .where(Team.project_id == project_id)
            .options(joinedload(TeamMember.user))
        )
        tm_res = await self.db.execute(tm_stmt)
        team_members = list(tm_res.scalars().all())

        return {
            "project": project,
            "milestones": milestones,
            "tasks": tasks,
            "documents": documents,
            "decisions": decisions,
            "team_members": team_members,
        }
