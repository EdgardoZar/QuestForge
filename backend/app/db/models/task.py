"""Task and TaskCompletion database models."""

from datetime import datetime, date
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Column, String, Integer, DateTime, Date, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from uuid import uuid4
import enum

from app.db.session import Base

if TYPE_CHECKING:
    from app.db.models.character import Character


class TaskType(str, enum.Enum):
    """Types of tasks available in the system."""
    DAILY = "daily"
    TODO = "todo"
    HABIT = "habit"


class TaskDifficulty(str, enum.Enum):
    """Difficulty levels for tasks."""
    TRIVIAL = "trivial"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class RitualTime(str, enum.Enum):
    """Time of day for ritual tasks."""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


class Task(Base):
    """Task model for dailies, todos, and habits."""

    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)

    # Basic Info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(SQLEnum(TaskType), nullable=False)
    difficulty = Column(SQLEnum(TaskDifficulty), default=TaskDifficulty.MEDIUM, nullable=False)

    # Rewards (calculated based on difficulty)
    experience_reward = Column(Integer, nullable=False)
    gold_reward = Column(Integer, default=0, nullable=False)
    mana_reward = Column(Integer, default=0, nullable=False)
    energy_reward = Column(Integer, default=0, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # For Dailies
    repeat_days = Column(ARRAY(Integer), default=[1, 2, 3, 4, 5, 6, 7], nullable=True)  # 1=Monday, 7=Sunday
    ritual_time = Column(SQLEnum(RitualTime), nullable=True)

    # For Habits
    is_positive = Column(Boolean, default=True, nullable=True)

    # For Todos
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Dice Roller
    dice_weight = Column(Integer, default=1, nullable=False)  # 1-10

    # Metadata
    tags = Column(ARRAY(String), default=list, nullable=False)
    notes = Column(JSONB, default=dict, nullable=False)

    # Relationships
    character = relationship("Character", back_populates="tasks")
    completions = relationship("TaskCompletion", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task {self.title} ({self.task_type.value})>"


class TaskCompletion(Base):
    """TaskCompletion model for tracking task completion history."""

    __tablename__ = "task_completions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)

    # Timestamp
    completed_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Rewards granted
    experience_gained = Column(Integer, nullable=False)
    gold_gained = Column(Integer, default=0, nullable=False)
    mana_gained = Column(Integer, default=0, nullable=False)
    energy_gained = Column(Integer, default=0, nullable=False)

    # Context at completion
    streak_at_completion = Column(Integer, nullable=True)
    level_at_completion = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    task = relationship("Task", back_populates="completions")
    character = relationship("Character", back_populates="task_completions")

    def __repr__(self):
        return f"<TaskCompletion {self.task_id} at {self.completed_at}>"
