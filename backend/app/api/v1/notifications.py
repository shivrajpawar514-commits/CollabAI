import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.notification import NotificationResponse, ActivityLogResponse
from app.repositories.notification_repo import NotificationRepository

router = APIRouter(tags=["Notifications & Activity Feed"])


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_my_notifications(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List in-app notifications for the logged-in student."""
    repo = NotificationRepository(db)
    items = await repo.list_user_notifications(current_user.id)
    return [NotificationResponse.model_validate(n) for n in items]


@router.get("/notifications/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the unread notification count badge."""
    repo = NotificationRepository(db)
    count = await repo.count_unread(current_user.id)
    return {"unread_count": count}


@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a notification as read."""
    repo = NotificationRepository(db)
    success = await repo.mark_as_read(notification_id, current_user.id)
    return {"success": success}


@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all user notifications as read."""
    repo = NotificationRepository(db)
    count = await repo.mark_all_as_read(current_user.id)
    return {"count": count}


@router.get("/projects/{project_id}/activity-feed", response_model=List[ActivityLogResponse])
async def get_project_activity_feed(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve audit activity feed for a project (used by team & AI context)."""
    repo = NotificationRepository(db)
    items = await repo.list_project_activities(project_id)
    return [ActivityLogResponse.model_validate(a) for a in items]
