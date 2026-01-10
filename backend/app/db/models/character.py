"""Character database model."""

from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.db.session import Base

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.task import Task


class Character(Base):
    """Character model representing a player's RPG avatar."""

    __tablename__ = "characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Basic Info
    name = Column(String(100), nullable=False)
    character_class = Column(
        String(20),
        nullable=False,
        comment="warrior, mage, rogue, healer"
    )

    # Level & Experience
    level = Column(Integer, default=1, nullable=False)
    experience = Column(Integer, default=0, nullable=False)
    experience_to_next = Column(Integer, default=100, nullable=False)

    # Resources
    health_current = Column(Integer, default=100, nullable=False)
    health_max = Column(Integer, default=100, nullable=False)
    mana_current = Column(Integer, default=100, nullable=False)
    mana_max = Column(Integer, default=100, nullable=False)
    energy_current = Column(Integer, default=0, nullable=False)
    energy_max = Column(Integer, default=100, nullable=False)

    # Currency
    gold = Column(Integer, default=0, nullable=False)
    gems = Column(Integer, default=0, nullable=False)

    # Stats
    streak_days = Column(Integer, default=0, nullable=False)
    total_tasks_completed = Column(Integer, default=0, nullable=False)

    # Customization
    avatar_url = Column(Text, nullable=True)
    title = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    last_daily_reset = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="character")
    tasks = relationship("Task", back_populates="character", cascade="all, delete-orphan")
    task_completions = relationship("TaskCompletion", back_populates="character", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint("character_class IN ('warrior', 'mage', 'rogue', 'healer')", name="valid_class"),
        CheckConstraint("health_current >= 0 AND health_current <= health_max", name="health_valid"),
        CheckConstraint("mana_current >= 0 AND mana_current <= mana_max", name="mana_valid"),
        CheckConstraint("energy_current >= 0 AND energy_current <= energy_max", name="energy_valid"),
        CheckConstraint("level >= 1", name="level_valid"),
        CheckConstraint("experience >= 0", name="experience_valid"),
        CheckConstraint("gold >= 0", name="gold_valid"),
        CheckConstraint("gems >= 0", name="gems_valid"),
    )

    def __repr__(self):
        return f"<Character {self.name} (Level {self.level} {self.character_class})>"
