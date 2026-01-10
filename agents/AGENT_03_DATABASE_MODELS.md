# Agent Task: Database Models - Core Entities

## Task ID: CHUNK-1.3
## Priority: CRITICAL
## Estimated Time: 4-5 hours
## Dependencies: CHUNK-1.2 (Backend Foundation)

---

## Objective

Create all core SQLAlchemy database models with proper relationships, constraints, and PostgreSQL triggers for automatic game mechanics.

---

## Context

QuestForge requires the following core entities:
- User (authentication)
- Character (player avatar with RPG stats)
- Task (dailies, todos, habits)
- TaskCompletion (history)

---

## Deliverables

### 1. User Model

Create `backend/app/db/models/user.py`:

```python
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
```

### 2. Character Model

Create `backend/app/db/models/character.py`:

```python
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
```

### 3. Task Model

Create `backend/app/db/models/task.py`:

```python
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
    DAILY = "daily"
    TODO = "todo"
    HABIT = "habit"


class TaskDifficulty(str, enum.Enum):
    TRIVIAL = "trivial"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class RitualTime(str, enum.Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


class Task(Base):
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
```

### 4. Daily Stats Model

Create `backend/app/db/models/stats.py`:

```python
from datetime import datetime, date
from sqlalchemy import Column, Integer, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from app.db.session import Base


class DailyStats(Base):
    __tablename__ = "daily_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)

    # Daily metrics
    tasks_completed = Column(Integer, default=0, nullable=False)
    rituals_completed = Column(Integer, default=0, nullable=False)
    abilities_used = Column(Integer, default=0, nullable=False)
    experience_gained = Column(Integer, default=0, nullable=False)
    gold_earned = Column(Integer, default=0, nullable=False)

    # Health tracking
    health_lost = Column(Integer, default=0, nullable=False)
    health_restored = Column(Integer, default=0, nullable=False)

    # Time tracking
    active_time_minutes = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("character_id", "date", name="unique_character_date"),
    )

    def __repr__(self):
        return f"<DailyStats {self.character_id} on {self.date}>"
```

### 5. Models Init File

Update `backend/app/db/models/__init__.py`:

```python
"""Database models package."""

from app.db.models.user import User
from app.db.models.character import Character
from app.db.models.task import Task, TaskCompletion, TaskType, TaskDifficulty, RitualTime
from app.db.models.stats import DailyStats

__all__ = [
    "User",
    "Character",
    "Task",
    "TaskCompletion",
    "TaskType",
    "TaskDifficulty",
    "RitualTime",
    "DailyStats",
]
```

### 6. Update Alembic env.py

Update imports in `backend/alembic/env.py`:

```python
# Add after existing imports
from app.db.models import User, Character, Task, TaskCompletion, DailyStats
```

### 7. Create Initial Migration

Create migration file `backend/alembic/versions/001_initial_schema.py`:

```python
"""Initial schema with core models

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default={}),
        sa.Column('timezone', sa.String(50), nullable=False, default='America/Mexico_City'),
        sa.Column('telegram_chat_id', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('telegram_chat_id')
    )
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_email', 'users', ['email'])

    # Create characters table
    op.create_table(
        'characters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('character_class', sa.String(20), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False, default=1),
        sa.Column('experience', sa.Integer(), nullable=False, default=0),
        sa.Column('experience_to_next', sa.Integer(), nullable=False, default=100),
        sa.Column('health_current', sa.Integer(), nullable=False, default=100),
        sa.Column('health_max', sa.Integer(), nullable=False, default=100),
        sa.Column('mana_current', sa.Integer(), nullable=False, default=100),
        sa.Column('mana_max', sa.Integer(), nullable=False, default=100),
        sa.Column('energy_current', sa.Integer(), nullable=False, default=0),
        sa.Column('energy_max', sa.Integer(), nullable=False, default=100),
        sa.Column('gold', sa.Integer(), nullable=False, default=0),
        sa.Column('gems', sa.Integer(), nullable=False, default=0),
        sa.Column('streak_days', sa.Integer(), nullable=False, default=0),
        sa.Column('total_tasks_completed', sa.Integer(), nullable=False, default=0),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('title', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_daily_reset', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id'),
        sa.CheckConstraint("character_class IN ('warrior', 'mage', 'rogue', 'healer')", name='valid_class'),
        sa.CheckConstraint('health_current >= 0 AND health_current <= health_max', name='health_valid'),
        sa.CheckConstraint('mana_current >= 0 AND mana_current <= mana_max', name='mana_valid'),
        sa.CheckConstraint('energy_current >= 0 AND energy_current <= energy_max', name='energy_valid'),
        sa.CheckConstraint('level >= 1', name='level_valid'),
        sa.CheckConstraint('experience >= 0', name='experience_valid'),
        sa.CheckConstraint('gold >= 0', name='gold_valid'),
        sa.CheckConstraint('gems >= 0', name='gems_valid'),
    )
    op.create_index('idx_characters_user', 'characters', ['user_id'])

    # Create task type enum
    task_type = postgresql.ENUM('daily', 'todo', 'habit', name='tasktype')
    task_type.create(op.get_bind())

    # Create task difficulty enum
    task_difficulty = postgresql.ENUM('trivial', 'easy', 'medium', 'hard', name='taskdifficulty')
    task_difficulty.create(op.get_bind())

    # Create ritual time enum
    ritual_time = postgresql.ENUM('morning', 'afternoon', 'evening', name='ritualtime')
    ritual_time.create(op.get_bind())

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('task_type', sa.Enum('daily', 'todo', 'habit', name='tasktype'), nullable=False),
        sa.Column('difficulty', sa.Enum('trivial', 'easy', 'medium', 'hard', name='taskdifficulty'), nullable=False),
        sa.Column('experience_reward', sa.Integer(), nullable=False),
        sa.Column('gold_reward', sa.Integer(), nullable=False, default=0),
        sa.Column('mana_reward', sa.Integer(), nullable=False, default=0),
        sa.Column('energy_reward', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('repeat_days', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('ritual_time', sa.Enum('morning', 'afternoon', 'evening', name='ritualtime'), nullable=True),
        sa.Column('is_positive', sa.Boolean(), nullable=True, default=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dice_weight', sa.Integer(), nullable=False, default=1),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=False, default=[]),
        sa.Column('notes', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default={}),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_tasks_character', 'tasks', ['character_id'])
    op.create_index('idx_tasks_type', 'tasks', ['task_type'])
    op.create_index('idx_tasks_active', 'tasks', ['is_active'], postgresql_where=sa.text('is_active = true'))

    # Create task_completions table
    op.create_table(
        'task_completions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('experience_gained', sa.Integer(), nullable=False),
        sa.Column('gold_gained', sa.Integer(), nullable=False, default=0),
        sa.Column('mana_gained', sa.Integer(), nullable=False, default=0),
        sa.Column('energy_gained', sa.Integer(), nullable=False, default=0),
        sa.Column('streak_at_completion', sa.Integer(), nullable=True),
        sa.Column('level_at_completion', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_task_completions_task', 'task_completions', ['task_id'])
    op.create_index('idx_task_completions_date', 'task_completions', ['completed_at'])

    # Create daily_stats table
    op.create_table(
        'daily_stats',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('tasks_completed', sa.Integer(), nullable=False, default=0),
        sa.Column('rituals_completed', sa.Integer(), nullable=False, default=0),
        sa.Column('abilities_used', sa.Integer(), nullable=False, default=0),
        sa.Column('experience_gained', sa.Integer(), nullable=False, default=0),
        sa.Column('gold_earned', sa.Integer(), nullable=False, default=0),
        sa.Column('health_lost', sa.Integer(), nullable=False, default=0),
        sa.Column('health_restored', sa.Integer(), nullable=False, default=0),
        sa.Column('active_time_minutes', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('character_id', 'date', name='unique_character_date'),
    )
    op.create_index('idx_daily_stats_character_date', 'daily_stats', ['character_id', 'date'])

    # Create XP calculation function
    op.execute("""
        CREATE OR REPLACE FUNCTION calculate_exp_to_next(current_level INTEGER)
        RETURNS INTEGER AS $$
        BEGIN
            RETURN FLOOR(100 * POWER(1.1, current_level - 1));
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
    """)

    # Create auto level-up trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION check_level_up()
        RETURNS TRIGGER AS $$
        BEGIN
            WHILE NEW.experience >= NEW.experience_to_next LOOP
                NEW.experience := NEW.experience - NEW.experience_to_next;
                NEW.level := NEW.level + 1;
                NEW.experience_to_next := calculate_exp_to_next(NEW.level);

                -- Increase max stats on level up
                NEW.health_max := NEW.health_max + 5;
                NEW.mana_max := NEW.mana_max + 5;
                NEW.health_current := NEW.health_max;  -- Full restore on level up
                NEW.mana_current := NEW.mana_max;
            END LOOP;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create level-up trigger
    op.execute("""
        CREATE TRIGGER trigger_level_up
        BEFORE UPDATE OF experience ON characters
        FOR EACH ROW
        EXECUTE FUNCTION check_level_up();
    """)

    # Create daily stats update trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_daily_stats()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO daily_stats (id, character_id, date, tasks_completed, experience_gained, gold_earned, created_at)
            VALUES (
                gen_random_uuid(),
                NEW.character_id,
                CURRENT_DATE,
                1,
                NEW.experience_gained,
                NEW.gold_gained,
                NOW()
            )
            ON CONFLICT (character_id, date)
            DO UPDATE SET
                tasks_completed = daily_stats.tasks_completed + 1,
                experience_gained = daily_stats.experience_gained + NEW.experience_gained,
                gold_earned = daily_stats.gold_earned + NEW.gold_gained;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create daily stats trigger
    op.execute("""
        CREATE TRIGGER trigger_update_daily_stats
        AFTER INSERT ON task_completions
        FOR EACH ROW
        EXECUTE FUNCTION update_daily_stats();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trigger_update_daily_stats ON task_completions")
    op.execute("DROP TRIGGER IF EXISTS trigger_level_up ON characters")

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS update_daily_stats()")
    op.execute("DROP FUNCTION IF EXISTS check_level_up()")
    op.execute("DROP FUNCTION IF EXISTS calculate_exp_to_next(INTEGER)")

    # Drop tables
    op.drop_table('daily_stats')
    op.drop_table('task_completions')
    op.drop_table('tasks')
    op.drop_table('characters')
    op.drop_table('users')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS ritualtime")
    op.execute("DROP TYPE IF EXISTS taskdifficulty")
    op.execute("DROP TYPE IF EXISTS tasktype")
```

---

## Success Criteria

- [ ] All models are created without import errors
- [ ] Migration runs successfully: `alembic upgrade head`
- [ ] All tables exist in PostgreSQL
- [ ] Foreign key relationships work correctly
- [ ] Check constraints enforce valid data
- [ ] Level-up trigger fires when experience is added
- [ ] Daily stats trigger fires on task completion

---

## Test Instructions

1. Run migration: `docker-compose exec backend alembic upgrade head`
2. Connect to PostgreSQL: `docker-compose exec postgres psql -U questforge`
3. Verify tables: `\dt`
4. Check constraints: `\d characters`
5. Test level-up trigger manually:
   ```sql
   -- Insert a test user and character
   INSERT INTO users (id, username, email, password_hash, created_at)
   VALUES (gen_random_uuid(), 'test', 'test@test.com', 'hash', NOW());

   INSERT INTO characters (id, user_id, name, character_class, created_at, last_daily_reset)
   SELECT gen_random_uuid(), id, 'Hero', 'warrior', NOW(), NOW() FROM users WHERE username = 'test';

   -- Add XP and check level up
   UPDATE characters SET experience = experience + 150 WHERE name = 'Hero';
   SELECT name, level, experience, experience_to_next, health_max FROM characters WHERE name = 'Hero';
   ```

---

## Notes

- Enums are created as PostgreSQL types for better performance
- Triggers handle automatic level-up calculations
- Daily stats are automatically updated on task completion
- All UUIDs use PostgreSQL's native UUID type
