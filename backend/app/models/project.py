import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.skill import Skill
    from app.models.team import Team
    from app.models.task import Milestone, Task
    from app.models.chat import Message, FileAttachment
    from app.models.notification import ActivityLog
    from app.models.rag import Document, DocumentChunk


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    problem_statement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    owner_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="recruiting", index=True, nullable=False)
    max_team_size: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    
    repo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    demo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="owned_projects", lazy="joined")
    required_skills: Mapped[List["ProjectSkill"]] = relationship("ProjectSkill", back_populates="project", cascade="all, delete-orphan", lazy="selectin")
    roles: Mapped[List["ProjectRole"]] = relationship("ProjectRole", back_populates="project", cascade="all, delete-orphan", lazy="selectin")
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="project", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    milestones: Mapped[List["Milestone"]] = relationship("Milestone", back_populates="project", cascade="all, delete-orphan", lazy="selectin")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="project", cascade="all, delete-orphan", lazy="selectin")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="project", cascade="all, delete-orphan", lazy="selectin")
    files: Mapped[List["FileAttachment"]] = relationship("FileAttachment", back_populates="project", cascade="all, delete-orphan", lazy="selectin")
    activities: Mapped[List["ActivityLog"]] = relationship("ActivityLog", back_populates="project", cascade="all, delete-orphan", lazy="selectin")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="project", cascade="all, delete-orphan", lazy="selectin")
    chunks: Mapped[List["DocumentChunk"]] = relationship("DocumentChunk", back_populates="project", cascade="all, delete-orphan", lazy="selectin")



class ProjectSkill(Base):
    __tablename__ = "project_skills"

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
    skill_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="required_skills")
    skill: Mapped["Skill"] = relationship("Skill", lazy="joined")


class ProjectRole(Base):
    __tablename__ = "project_roles"

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
    role_name: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "Frontend Engineer", "ML Researcher"
    capacity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    filled_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="roles")
