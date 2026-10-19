import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.user import User


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    college: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    branch: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    year: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # e.g., '1st Year', '2nd Year', 'Final Year'
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    
    languages: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    interests: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    preferred_roles: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list) # e.g. ['Backend Dev', 'ML Engineer']
    
    availability_hours_per_week: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    
    github_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

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
    user: Mapped["User"] = relationship("User", back_populates="profile")
