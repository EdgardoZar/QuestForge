"""User database model."""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.db.session import Base

if TYPE_CHECKING:
    from app.db.models.character import Character


class User(Base):
    """User model for authentication and account management."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime(timezone=True))

    # Settings
    settings = Column(JSONB, default=dict, nullable=False)
    timezone = Column(String(50), default="America/Mexico_City", nullable=False)

    # Telegram integration
    telegram_chat_id = Column(String(50), unique=True, nullable=True)

    # Relationships
    character = relationship("Character", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"
