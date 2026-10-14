import uuid
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.task import Milestone, Task, TaskDependency, TaskComment
from app.schemas.task import MilestoneCreate, MilestoneUpdate, TaskCreate, TaskUpdate


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Milestones
    async def get_milestones(self, project_id: uuid.UUID) -> List[Milestone]:
        stmt = (
            select(Milestone)
            .where(Milestone.project_id == project_id)
            .order_by(Milestone.order_index.asc(), Milestone.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_milestone_by_id(self, milestone_id: uuid.UUID) -> Optional[Milestone]:
        stmt = select(Milestone).where(Milestone.id == milestone_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_milestone(self, project_id: uuid.UUID, m_in: MilestoneCreate) -> Milestone:
        milestone = Milestone(
            project_id=project_id,
            title=m_in.title,
            description=m_in.description,
            deadline=m_in.deadline,
            order_index=m_in.order_index,
            status=m_in.status
        )
        self.db.add(milestone)
        await self.db.commit()
        await self.db.refresh(milestone)
        return milestone

    async def update_milestone(self, milestone_id: uuid.UUID, m_in: MilestoneUpdate) -> Optional[Milestone]:
        milestone = await self.get_milestone_by_id(milestone_id)
        if not milestone:
            return None
        for k, v in m_in.model_dump(exclude_unset=True).items():
            setattr(milestone, k, v)
        await self.db.commit()
        await self.db.refresh(milestone)
        return milestone

    async def delete_milestone(self, milestone_id: uuid.UUID) -> bool:
        milestone = await self.get_milestone_by_id(milestone_id)
        if milestone:
            await self.db.delete(milestone)
            await self.db.commit()
            return True
        return False

    # Tasks
    async def get_tasks(self, project_id: uuid.UUID) -> List[Task]:
        stmt = (
            select(Task)
            .where(Task.project_id == project_id)
            .options(
                joinedload(Task.assignee),
                joinedload(Task.creator),
                joinedload(Task.milestone),
                selectinload(Task.dependencies).joinedload(TaskDependency.depends_on_task)
            )
            .order_by(Task.order_index.asc(), Task.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_task_by_id(self, task_id: uuid.UUID) -> Optional[Task]:
        stmt = (
            select(Task)
            .where(Task.id == task_id)
            .options(
                joinedload(Task.assignee),
                joinedload(Task.creator),
                joinedload(Task.milestone),
                selectinload(Task.comments).joinedload(TaskComment.user),
                selectinload(Task.dependencies).joinedload(TaskDependency.depends_on_task)
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_task(self, project_id: uuid.UUID, creator_id: uuid.UUID, t_in: TaskCreate) -> Task:
        task = Task(
            project_id=project_id,
            creator_id=creator_id,
            title=t_in.title,
            description=t_in.description,
            status=t_in.status,
            priority=t_in.priority,
            deadline=t_in.deadline,
            estimated_hours=t_in.estimated_hours,
            order_index=t_in.order_index,
            milestone_id=t_in.milestone_id,
            assignee_id=t_in.assignee_id
        )
        self.db.add(task)
        await self.db.flush()

        for dep_id in t_in.dependency_ids:
            dep = TaskDependency(task_id=task.id, depends_on_task_id=dep_id)
            self.db.add(dep)

        await self.db.commit()
        return await self.get_task_by_id(task.id)

    async def update_task(self, task_id: uuid.UUID, t_in: TaskUpdate) -> Optional[Task]:
        task = await self.get_task_by_id(task_id)
        if not task:
            return None
        for k, v in t_in.model_dump(exclude_unset=True).items():
            setattr(task, k, v)
        await self.db.commit()
        return await self.get_task_by_id(task.id)

    async def update_task_status_and_order(self, task_id: uuid.UUID, status: str, order_index: int) -> Optional[Task]:
        task = await self.get_task_by_id(task_id)
        if not task:
            return None
        task.status = status
        task.order_index = order_index
        await self.db.commit()
        return await self.get_task_by_id(task.id)

    async def delete_task(self, task_id: uuid.UUID) -> bool:
        task = await self.get_task_by_id(task_id)
        if task:
            await self.db.delete(task)
            await self.db.commit()
            return True
        return False

    # Comments
    async def add_comment(self, task_id: uuid.UUID, user_id: uuid.UUID, content: str) -> TaskComment:
        comment = TaskComment(task_id=task_id, user_id=user_id, content=content)
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        # re-fetch with user
        stmt = select(TaskComment).where(TaskComment.id == comment.id).options(joinedload(TaskComment.user))
        res = await self.db.execute(stmt)
        return res.scalar_one()
