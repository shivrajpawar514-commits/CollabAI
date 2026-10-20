import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.notification import Notification, ActivityLog


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        user_id: uuid.UUID,
        title: str,
        message: str,
        type_: str = "system",
        actor_id: Optional[uuid.UUID] = None,
        link: Optional[str] = None
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            actor_id=actor_id,
            title=title,
            message=message,
            type=type_,
            link=link,
            is_read=False
        )
        self.db.add(notif)
        await self.db.commit()
        await self.db.refresh(notif)
        return notif

    async def list_user_notifications(self, user_id: uuid.UUID, limit: int = 30) -> List[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .options(joinedload(Notification.actor))
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def count_unread(self, user_id: uuid.UUID) -> int:
        stmt = select(func.count(Notification.id)).where(Notification.user_id == user_id, Notification.is_read == False)
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def mark_as_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
        res = await self.db.execute(stmt)
        notif = res.scalar_one_or_none()
        if notif:
            notif.is_read = True
            await self.db.commit()
            return True
        return False

    async def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        stmt = select(Notification).where(Notification.user_id == user_id, Notification.is_read == False)
        res = await self.db.execute(stmt)
        notifs = list(res.scalars().all())
        for n in notifs:
            n.is_read = True
        await self.db.commit()
        return len(notifs)

    # Activity Logs
    async def log_activity(
        self,
        project_id: uuid.UUID,
        action: str,
        entity_type: str,
        description: str,
        user_id: Optional[uuid.UUID] = None,
        entity_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> ActivityLog:
        act = ActivityLog(
            project_id=project_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            extra_data=extra_data or {}
        )
        self.db.add(act)
        await self.db.commit()
        await self.db.refresh(act)
        return act

    async def list_project_activities(self, project_id: uuid.UUID, limit: int = 50) -> List[ActivityLog]:
        stmt = (
            select(ActivityLog)
            .where(ActivityLog.project_id == project_id)
            .options(joinedload(ActivityLog.user))
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
