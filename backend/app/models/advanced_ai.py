import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project
    from app.models.task import Task


class ProjectDecision(Base):
    __tablename__ = "project_decisions"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    recorder_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    what: Mapped[str] = mapped_column(Text, nullable=False)
    why: Mapped[str] = mapped_column(Text, nullable=False)
    who: Mapped[str] = mapped_column(String(255), default="Team Consensus", nullable=False)
    alternatives_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    tags_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    linked_task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True
    )
    linked_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    recorder: Mapped["User"] = relationship("User", lazy="joined")


class MeetingNote(Base):
    __tablename__ = "meeting_notes"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    organizer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(255), default="Team Standup", nullable=False)
    raw_transcript: Mapped[str] = mapped_column(Text, nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    key_topics_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    overall_sentiment: Mapped[str] = mapped_column(String(50), default="productive", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    organizer: Mapped["User"] = relationship("User", lazy="joined")
    action_items: Mapped[List["MeetingActionItem"]] = relationship(
        "MeetingActionItem",
        back_populates="meeting",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class MeetingActionItem(Base):
    __tablename__ = "meeting_action_items"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("meeting_notes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    suggested_assignee: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    priority: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)
    estimated_hours: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    is_converted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    converted_task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    meeting: Mapped["MeetingNote"] = relationship("MeetingNote", back_populates="action_items")
    converted_task: Mapped[Optional["Task"]] = relationship("Task", lazy="joined")
