import uuid
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Milestone, Task, TaskComment
from app.repositories.task_repo import TaskRepository
from app.repositories.project_repo import ProjectRepository
from app.repositories.notification_repo import NotificationRepository
from app.repositories.user_repo import UserRepository
from app.schemas.task import (
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    TaskCreate, TaskUpdate, TaskMove, TaskResponse, TaskDetailResponse,
    TaskCommentCreate, TaskCommentResponse
)
from app.core.ws import ws_manager


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.project_repo = ProjectRepository(db)
        self.notif_repo = NotificationRepository(db)
        self.user_repo = UserRepository(db)

    # Milestones
    async def get_milestones(self, project_id: uuid.UUID) -> List[MilestoneResponse]:
        items = await self.task_repo.get_milestones(project_id)
        return [MilestoneResponse.model_validate(m) for m in items]

    async def create_milestone(self, project_id: uuid.UUID, user_id: uuid.UUID, m_in: MilestoneCreate) -> MilestoneResponse:
        m = await self.task_repo.create_milestone(project_id, m_in)
        await self.notif_repo.log_activity(
            project_id=project_id,
            user_id=user_id,
            action="milestone_created",
            entity_type="milestone",
            entity_id=str(m.id),
            description=f"Created milestone: {m.title}"
        )
        await ws_manager.broadcast_to_project(str(project_id), "milestone_created", {"id": str(m.id), "title": m.title})
        return MilestoneResponse.model_validate(m)

    async def update_milestone(self, project_id: uuid.UUID, milestone_id: uuid.UUID, user_id: uuid.UUID, m_in: MilestoneUpdate) -> MilestoneResponse:
        m = await self.task_repo.update_milestone(milestone_id, m_in)
        if not m:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found.")
        await self.notif_repo.log_activity(
            project_id=project_id,
            user_id=user_id,
            action="milestone_updated",
            entity_type="milestone",
            entity_id=str(m.id),
            description=f"Updated milestone: {m.title} ({m.status})"
        )
        await ws_manager.broadcast_to_project(str(project_id), "milestone_updated", {"id": str(m.id), "status": m.status})
        return MilestoneResponse.model_validate(m)

    # Tasks
    async def get_tasks(self, project_id: uuid.UUID) -> List[TaskResponse]:
        tasks = await self.task_repo.get_tasks(project_id)
        return [TaskResponse.model_validate(t) for t in tasks]

    async def get_task_detail(self, task_id: uuid.UUID) -> TaskDetailResponse:
        task = await self.task_repo.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
        return TaskDetailResponse.model_validate(task)

    async def create_task(self, project_id: uuid.UUID, user_id: uuid.UUID, t_in: TaskCreate) -> TaskResponse:
        task = await self.task_repo.create_task(project_id, user_id, t_in)

        # Notify assignee if assigned to someone else
        if task.assignee_id and task.assignee_id != user_id:
            actor = await self.user_repo.get_by_id(user_id)
            actor_name = actor.full_name if actor else "Team member"
            notif = await self.notif_repo.create_notification(
                user_id=task.assignee_id,
                actor_id=user_id,
                title="Task Assigned to You",
                message=f"{actor_name} assigned you to '{task.title}' (Priority: {task.priority.upper()}).",
                type_="task_assignment",
                link=f"/projects/{project_id}/workspace?tab=tasks"
            )
            await ws_manager.send_to_user(str(task.assignee_id), "notification", {
                "id": str(notif.id),
                "title": notif.title,
                "message": notif.message,
                "type": notif.type
            })

        await self.notif_repo.log_activity(
            project_id=project_id,
            user_id=user_id,
            action="task_created",
            entity_type="task",
            entity_id=str(task.id),
            description=f"Created task '{task.title}' in [{task.status.upper()}]."
        )

        resp = TaskResponse.model_validate(task)
        await ws_manager.broadcast_to_project(str(project_id), "task_created", resp.model_dump(mode="json"))
        return resp

    async def update_task(self, project_id: uuid.UUID, task_id: uuid.UUID, user_id: uuid.UUID, t_in: TaskUpdate) -> TaskResponse:
        task = await self.task_repo.update_task(task_id, t_in)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

        resp = TaskResponse.model_validate(task)
        await ws_manager.broadcast_to_project(str(project_id), "task_updated", resp.model_dump(mode="json"))
        return resp

    async def move_task(self, project_id: uuid.UUID, task_id: uuid.UUID, user_id: uuid.UUID, move_in: TaskMove) -> TaskResponse:
        task = await self.task_repo.update_task_status_and_order(task_id, move_in.status, move_in.order_index)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

        await self.notif_repo.log_activity(
            project_id=project_id,
            user_id=user_id,
            action="task_moved",
            entity_type="task",
            entity_id=str(task.id),
            description=f"Moved '{task.title}' to [{task.status.upper()}]."
        )

        resp = TaskResponse.model_validate(task)
        await ws_manager.broadcast_to_project(str(project_id), "task_moved", resp.model_dump(mode="json"))
        return resp

    async def add_comment(self, project_id: uuid.UUID, task_id: uuid.UUID, user_id: uuid.UUID, c_in: TaskCommentCreate) -> TaskCommentResponse:
        task = await self.task_repo.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

        comment = await self.task_repo.add_comment(task_id, user_id, c_in.content)
        resp = TaskCommentResponse.model_validate(comment)

        await ws_manager.broadcast_to_project(str(project_id), "task_comment_added", {
            "task_id": str(task_id),
            "comment": resp.model_dump(mode="json")
        })
        return resp
