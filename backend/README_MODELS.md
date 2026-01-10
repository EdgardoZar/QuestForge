# QuestForge Database Models - Implementation Summary

## Overview

This document summarizes the implementation of the core database models for QuestForge, an RPG habit tracker application.

## Files Created

### 1. Database Models (`backend/app/db/models/`)

#### `user.py` - User Model
- **Purpose**: Authentication and account management
- **Key Fields**:
  - UUID primary key
  - username (unique, indexed)
  - email (unique, indexed)
  - password_hash
  - is_active, is_verified (status flags)
  - settings (JSONB for flexible user preferences)
  - timezone (defaults to "America/Mexico_City")
  - telegram_chat_id (for bot integration)
- **Relationships**: One-to-one with Character

#### `character.py` - Character Model
- **Purpose**: Player's RPG avatar with stats and progression
- **Key Fields**:
  - UUID primary key
  - user_id (foreign key to users)
  - name, character_class (warrior, mage, rogue, healer)
  - Level & Experience: level, experience, experience_to_next
  - Resources: health_current/max, mana_current/max, energy_current/max
  - Currency: gold, gems
  - Stats: streak_days, total_tasks_completed
  - Customization: avatar_url, title
  - Timestamps: created_at, last_daily_reset
- **Constraints**:
  - Valid character classes
  - Health/mana/energy bounds checking
  - Non-negative stats (level, experience, gold, gems)
- **Relationships**:
  - Belongs to User
  - Has many Tasks
  - Has many TaskCompletions

#### `task.py` - Task and TaskCompletion Models
- **Purpose**: Manage dailies, todos, and habits
- **Task Fields**:
  - UUID primary key
  - character_id (foreign key)
  - title, description
  - task_type (daily, todo, habit)
  - difficulty (trivial, easy, medium, hard)
  - Rewards: experience_reward, gold_reward, mana_reward, energy_reward
  - Status: is_active, created_at
  - Daily-specific: repeat_days (array), ritual_time
  - Habit-specific: is_positive
  - Todo-specific: due_date, completed_at
  - dice_weight (1-10 for dice roller feature)
  - Metadata: tags (array), notes (JSONB)
- **Enums**:
  - TaskType: DAILY, TODO, HABIT
  - TaskDifficulty: TRIVIAL, EASY, MEDIUM, HARD
  - RitualTime: MORNING, AFTERNOON, EVENING
- **Relationships**:
  - Belongs to Character
  - Has many TaskCompletions

#### `TaskCompletion Model**:
- **Purpose**: Track task completion history
- **Key Fields**:
  - UUID primary key
  - task_id, character_id (foreign keys)
  - completed_at (indexed timestamp)
  - Rewards granted: experience_gained, gold_gained, mana_gained, energy_gained
  - Context: streak_at_completion, level_at_completion, notes
- **Relationships**:
  - Belongs to Task
  - Belongs to Character

#### `stats.py` - DailyStats Model
- **Purpose**: Track daily character metrics
- **Key Fields**:
  - UUID primary key
  - character_id (foreign key)
  - date (indexed, unique per character)
  - Metrics: tasks_completed, rituals_completed, abilities_used
  - Progress: experience_gained, gold_earned
  - Health: health_lost, health_restored
  - Time: active_time_minutes
- **Constraints**: Unique constraint on (character_id, date)

### 2. Database Configuration

#### `backend/app/db/session.py`
- Defines SQLAlchemy Base for model inheritance
- Used for metadata and table creation

#### `backend/app/db/models/__init__.py`
- Exports all models for easy importing
- Provides clean API: `from app.db.models import User, Character, Task, ...`

### 3. Alembic Migration

#### `backend/alembic/versions/001_initial_schema.py`
- **Tables Created**:
  - users (with indexes on username, email)
  - characters (with index on user_id)
  - tasks (with indexes on character_id, task_type, is_active)
  - task_completions (with indexes on task_id, completed_at)
  - daily_stats (with composite index on character_id, date)

- **PostgreSQL Functions**:
  - `calculate_exp_to_next(level)`: Calculates XP needed for next level (100 * 1.1^(level-1))
  - `check_level_up()`: Trigger function for automatic level-up
  - `update_daily_stats()`: Trigger function for daily stats aggregation

- **Triggers**:
  - `trigger_level_up`: Fires on character experience update
    - Automatically levels up when XP threshold is met
    - Increases max health/mana by 5 each level
    - Fully restores health/mana on level up
  - `trigger_update_daily_stats`: Fires on task completion
    - Automatically updates daily stats
    - Aggregates tasks completed, XP gained, gold earned

- **Enums Created**:
  - tasktype: 'daily', 'todo', 'habit'
  - taskdifficulty: 'trivial', 'easy', 'medium', 'hard'
  - ritualtime: 'morning', 'afternoon', 'evening'

### 4. Supporting Files

#### `backend/alembic/env.py`
- Alembic environment configuration
- Imports all models for migration support
- Configures target_metadata for autogenerate

#### `backend/alembic.ini`
- Alembic configuration file
- Database URL: postgresql://questforge:questforge@localhost:5432/questforge

#### `backend/alembic/script.py.mako`
- Template for generating migration scripts

## Database Design Features

### 1. Automatic Level-Up System
- PostgreSQL trigger automatically handles level progression
- XP formula: 100 * 1.1^(level-1)
- Stat increases on level up (+5 max health/mana)
- Full restore on level up

### 2. Daily Stats Tracking
- Automatic aggregation via trigger
- Unique per character per day
- Tracks completion metrics, health changes, time spent

### 3. Flexible Task System
- Supports three task types: dailies, todos, habits
- Difficulty-based reward system
- Tags and JSONB notes for flexibility
- Dice roller integration with weighted tasks

### 4. Data Integrity
- Check constraints ensure valid data
- Foreign keys with CASCADE delete
- Unique constraints prevent duplicates
- Indexed columns for query performance

### 5. PostgreSQL Features
- Native UUID support
- JSONB for flexible metadata
- ARRAY for tags and repeat days
- Custom ENUM types
- Triggers for automation

## Testing

### Import Test
Run `python backend/test_models.py` to verify all models import correctly.

Expected output:
```
Testing model imports...
[OK] Base imported successfully
[OK] User model imported successfully
[OK] Character model imported successfully
[OK] Task models imported successfully
  - TaskType: ['daily', 'todo', 'habit']
  - TaskDifficulty: ['trivial', 'easy', 'medium', 'hard']
  - RitualTime: ['morning', 'afternoon', 'evening']
[OK] DailyStats model imported successfully
[OK] All models imported from __init__.py

Checking model registration with Base metadata:
  - users
  - characters
  - tasks
  - task_completions
  - daily_stats

[PASS] All tests passed!
```

### Manual Database Testing
Once PostgreSQL is running, you can test with:

```sql
-- Insert test user
INSERT INTO users (id, username, email, password_hash, created_at)
VALUES (gen_random_uuid(), 'testuser', 'test@test.com', 'hash', NOW());

-- Insert test character
INSERT INTO characters (id, user_id, name, character_class, created_at, last_daily_reset)
SELECT gen_random_uuid(), id, 'Hero', 'warrior', NOW(), NOW()
FROM users WHERE username = 'testuser';

-- Test level-up trigger (150 XP should trigger level up to level 2)
UPDATE characters
SET experience = experience + 150
WHERE name = 'Hero';

-- Verify level up occurred
SELECT name, level, experience, experience_to_next, health_max, mana_max
FROM characters
WHERE name = 'Hero';
```

Expected results:
- Level should be 2
- experience should be remainder (150 - 100 = 50)
- experience_to_next should be 110 (100 * 1.1^1)
- health_max and mana_max should be 105 (100 + 5)

## Next Steps

1. **Run Migration**: Once PostgreSQL is set up, run:
   ```bash
   cd backend
   alembic upgrade head
   ```

2. **Verify Tables**: Connect to PostgreSQL and run:
   ```sql
   \dt
   \d characters
   ```

3. **Implement Services**: Create service layer for business logic:
   - CharacterService (level-up, rewards)
   - TaskService (completion, scheduling)
   - UserService (authentication, profile)

4. **Create API Endpoints**: Build REST API:
   - POST /auth/register
   - GET /characters/me
   - POST /tasks
   - POST /tasks/{id}/complete

5. **Add Tests**: Write unit tests for:
   - Model validation
   - Trigger behavior
   - Relationship constraints

## Success Criteria

- [x] All models are created without import errors
- [x] Migration file created with all tables
- [ ] Migration runs successfully (requires PostgreSQL)
- [ ] All tables exist in PostgreSQL (requires running migration)
- [x] Foreign key relationships defined
- [x] Check constraints enforce valid data
- [x] Level-up trigger defined in migration
- [x] Daily stats trigger defined in migration

## Notes

- All models use SQLAlchemy 2.0 syntax
- PostgreSQL-specific features (UUID, JSONB, ARRAY, ENUM) used
- Automatic triggers handle common game mechanics
- Cascade delete ensures referential integrity
- Type hints provided for better IDE support
- Docstrings included for documentation
