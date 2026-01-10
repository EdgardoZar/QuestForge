# Agent Task: Tasks API

## Task ID: CHUNK-1.6
## Priority: CRITICAL
## Estimated Time: 5-6 hours
## Dependencies: CHUNK-1.5 (Character API)

---

## Objective

Implement the Tasks API with CRUD operations, task completion with rewards, and filtering by type/difficulty.

---

## Deliverables

### 1. Task Schemas

Create `backend/app/schemas/task.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from enum import Enum


class TaskType(str, Enum):
    DAILY = "daily"
    TODO = "todo"
    HABIT = "habit"


class TaskDifficulty(str, Enum):
    TRIVIAL = "trivial"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class RitualTime(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


# Reward constants
DIFFICULTY_REWARDS = {
    TaskDifficulty.TRIVIAL: {"experience": 5, "gold": 1},
    TaskDifficulty.EASY: {"experience": 10, "gold": 2},
    TaskDifficulty.MEDIUM: {"experience": 20, "gold": 5},
    TaskDifficulty.HARD: {"experience": 40, "gold": 10},
}


class TaskCreate(BaseModel):
    """Schema for creating a task."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    task_type: TaskType
    difficulty: TaskDifficulty = TaskDifficulty.MEDIUM
    dice_weight: int = Field(default=1, ge=1, le=10)

    # For dailies
    repeat_days: Optional[List[int]] = Field(default=[1, 2, 3, 4, 5, 6, 7])
    ritual_time: Optional[RitualTime] = None

    # For habits
    is_positive: Optional[bool] = True

    # For todos
    due_date: Optional[date] = None

    # Metadata
    tags: Optional[List[str]] = []


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    difficulty: Optional[TaskDifficulty] = None
    dice_weight: Optional[int] = Field(None, ge=1, le=10)
    repeat_days: Optional[List[int]] = None
    ritual_time: Optional[RitualTime] = None
    is_positive: Optional[bool] = None
    due_date: Optional[date] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: UUID
    character_id: UUID
    title: str
    description: Optional[str]
    task_type: TaskType
    difficulty: TaskDifficulty
    experience_reward: int
    gold_reward: int
    mana_reward: int
    energy_reward: int
    is_active: bool
    created_at: datetime
    repeat_days: Optional[List[int]]
    ritual_time: Optional[RitualTime]
    is_positive: Optional[bool]
    due_date: Optional[date]
    completed_at: Optional[datetime]
    dice_weight: int
    tags: List[str]
    completed_today: bool = False

    class Config:
        from_attributes = True


class TaskCompletionResponse(BaseModel):
    """Schema for task completion result."""
    task: TaskResponse
    rewards: dict
    character_update: dict
    level_up: bool = False
    new_level: Optional[int] = None


class TaskListResponse(BaseModel):
    """Schema for task list response."""
    tasks: List[TaskResponse]
    total: int


class TaskFilters(BaseModel):
    """Schema for task filtering."""
    task_type: Optional[TaskType] = None
    difficulty: Optional[TaskDifficulty] = None
    is_active: Optional[bool] = True
    ritual_time: Optional[RitualTime] = None
```

### 2. Task Service

Create `backend/app/services/task_service.py`:

```python
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date, timedelta
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Task, TaskCompletion, Character
from app.db.models.task import TaskType as TaskTypeEnum, TaskDifficulty as TaskDifficultyEnum
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskCompletionResponse,
    TaskFilters,
    TaskDifficulty,
    DIFFICULTY_REWARDS,
)
from app.services.character_service import CharacterService


class TaskService:
    """Service for task operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _calculate_rewards(self, difficulty: str) -> dict:
        """Calculate rewards based on difficulty."""
        diff_enum = TaskDifficulty(difficulty)
        base = DIFFICULTY_REWARDS.get(diff_enum, DIFFICULTY_REWARDS[TaskDifficulty.MEDIUM])
        return {
            "experience_reward": base["experience"],
            "gold_reward": base["gold"],
            "mana_reward": 0,
            "energy_reward": 0,
        }

    async def get_tasks(
        self,
        character_id: UUID,
        filters: Optional[TaskFilters] = None
    ) -> List[Task]:
        """Get tasks for a character with optional filtering."""
        query = select(Task).where(Task.character_id == character_id)

        if filters:
            if filters.task_type:
                query = query.where(Task.task_type == filters.task_type.value)
            if filters.difficulty:
                query = query.where(Task.difficulty == filters.difficulty.value)
            if filters.is_active is not None:
                query = query.where(Task.is_active == filters.is_active)
            if filters.ritual_time:
                query = query.where(Task.ritual_time == filters.ritual_time.value)

        query = query.order_by(Task.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_task_by_id(self, task_id: UUID, character_id: UUID) -> Optional[Task]:
        """Get a specific task by ID."""
        result = await self.db.execute(
            select(Task).where(
                and_(Task.id == task_id, Task.character_id == character_id)
            )
        )
        return result.scalar_one_or_none()

    async def create_task(self, character_id: UUID, task_data: TaskCreate) -> Task:
        """Create a new task."""
        rewards = self._calculate_rewards(task_data.difficulty.value)

        task = Task(
            character_id=character_id,
            title=task_data.title,
            description=task_data.description,
            task_type=task_data.task_type.value,
            difficulty=task_data.difficulty.value,
            dice_weight=task_data.dice_weight,
            repeat_days=task_data.repeat_days,
            ritual_time=task_data.ritual_time.value if task_data.ritual_time else None,
            is_positive=task_data.is_positive,
            due_date=task_data.due_date,
            tags=task_data.tags or [],
            **rewards,
        )

        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update_task(self, task: Task, update_data: TaskUpdate) -> Task:
        """Update a task."""
        update_dict = update_data.model_dump(exclude_unset=True)

        # If difficulty changed, recalculate rewards
        if "difficulty" in update_dict:
            rewards = self._calculate_rewards(update_dict["difficulty"].value)
            update_dict.update(rewards)
            update_dict["difficulty"] = update_dict["difficulty"].value

        # Convert enums to values
        if "ritual_time" in update_dict and update_dict["ritual_time"]:
            update_dict["ritual_time"] = update_dict["ritual_time"].value

        for field, value in update_dict.items():
            setattr(task, field, value)

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete_task(self, task: Task) -> None:
        """Delete a task."""
        await self.db.delete(task)
        await self.db.commit()

    async def is_completed_today(self, task_id: UUID, character_id: UUID) -> bool:
        """Check if task was completed today."""
        today = date.today()
        result = await self.db.execute(
            select(TaskCompletion).where(
                and_(
                    TaskCompletion.task_id == task_id,
                    TaskCompletion.character_id == character_id,
                    TaskCompletion.completed_at >= datetime.combine(today, datetime.min.time()),
                    TaskCompletion.completed_at < datetime.combine(today + timedelta(days=1), datetime.min.time()),
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def complete_task(
        self,
        task: Task,
        character: Character,
    ) -> TaskCompletionResponse:
        """Complete a task and grant rewards."""
        char_service = CharacterService(self.db)

        # Store level before completion
        level_before = character.level

        # Calculate rewards with streak bonus
        streak_multiplier = 1 + min(character.streak_days * 0.01, 0.5)
        xp_reward = int(task.experience_reward * streak_multiplier)
        gold_reward = task.gold_reward

        # Create completion record
        completion = TaskCompletion(
            task_id=task.id,
            character_id=character.id,
            experience_gained=xp_reward,
            gold_gained=gold_reward,
            mana_gained=task.mana_reward,
            energy_gained=task.energy_reward,
            streak_at_completion=character.streak_days,
            level_at_completion=character.level,
        )
        self.db.add(completion)

        # Apply rewards to character
        character.experience += xp_reward
        character.gold += gold_reward
        character.total_tasks_completed += 1

        if task.mana_reward > 0:
            character.mana_current = min(
                character.mana_current + task.mana_reward,
                character.mana_max
            )

        if task.energy_reward > 0:
            character.energy_current = min(
                character.energy_current + task.energy_reward,
                character.energy_max
            )

        # For todos, mark as completed
        if task.task_type == "todo":
            task.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(character)
        await self.db.refresh(task)

        # Check for level up
        level_up = character.level > level_before

        return TaskCompletionResponse(
            task=await self.to_response(task, character.id),
            rewards={
                "experience": xp_reward,
                "gold": gold_reward,
                "mana": task.mana_reward,
                "energy": task.energy_reward,
            },
            character_update={
                "level": character.level,
                "experience": character.experience,
                "experience_to_next": character.experience_to_next,
                "gold": character.gold,
                "health_current": character.health_current,
                "health_max": character.health_max,
                "mana_current": character.mana_current,
                "mana_max": character.mana_max,
            },
            level_up=level_up,
            new_level=character.level if level_up else None,
        )

    async def uncomplete_task(self, task_id: UUID, character_id: UUID) -> bool:
        """Undo task completion (same day only)."""
        today = date.today()

        # Find today's completion
        result = await self.db.execute(
            select(TaskCompletion).where(
                and_(
                    TaskCompletion.task_id == task_id,
                    TaskCompletion.character_id == character_id,
                    TaskCompletion.completed_at >= datetime.combine(today, datetime.min.time()),
                    TaskCompletion.completed_at < datetime.combine(today + timedelta(days=1), datetime.min.time()),
                )
            )
        )
        completion = result.scalar_one_or_none()

        if not completion:
            return False

        # Get character to reverse rewards
        char_result = await self.db.execute(
            select(Character).where(Character.id == character_id)
        )
        character = char_result.scalar_one()

        # Reverse rewards (don't reverse XP to avoid level-down complexity)
        character.gold = max(0, character.gold - completion.gold_gained)
        character.total_tasks_completed = max(0, character.total_tasks_completed - 1)

        # Delete completion
        await self.db.delete(completion)
        await self.db.commit()

        return True

    async def get_dailies_for_today(self, character_id: UUID) -> List[Task]:
        """Get dailies that should be done today."""
        today_weekday = date.today().isoweekday()  # 1=Monday, 7=Sunday

        result = await self.db.execute(
            select(Task).where(
                and_(
                    Task.character_id == character_id,
                    Task.task_type == "daily",
                    Task.is_active == True,
                    Task.repeat_days.contains([today_weekday]),
                )
            )
        )
        return list(result.scalars().all())

    async def get_pending_todos(self, character_id: UUID) -> List[Task]:
        """Get pending todos."""
        result = await self.db.execute(
            select(Task).where(
                and_(
                    Task.character_id == character_id,
                    Task.task_type == "todo",
                    Task.is_active == True,
                    Task.completed_at.is_(None),
                )
            ).order_by(Task.due_date.asc().nullsfirst())
        )
        return list(result.scalars().all())

    async def to_response(self, task: Task, character_id: UUID) -> TaskResponse:
        """Convert task to response schema."""
        completed_today = await self.is_completed_today(task.id, character_id)

        return TaskResponse(
            id=task.id,
            character_id=task.character_id,
            title=task.title,
            description=task.description,
            task_type=task.task_type,
            difficulty=task.difficulty,
            experience_reward=task.experience_reward,
            gold_reward=task.gold_reward,
            mana_reward=task.mana_reward,
            energy_reward=task.energy_reward,
            is_active=task.is_active,
            created_at=task.created_at,
            repeat_days=task.repeat_days,
            ritual_time=task.ritual_time,
            is_positive=task.is_positive,
            due_date=task.due_date,
            completed_at=task.completed_at,
            dice_weight=task.dice_weight,
            tags=task.tags or [],
            completed_today=completed_today,
        )
```

### 3. Tasks Router

Create `backend/app/api/v1/tasks.py`:

```python
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query

from app.api.deps import DBSession, CurrentUser
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskCompletionResponse,
    TaskListResponse,
    TaskFilters,
    TaskType,
    TaskDifficulty,
    RitualTime,
)
from app.services.task_service import TaskService
from app.services.character_service import CharacterService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


async def get_user_character(current_user, db):
    """Helper to get user's character."""
    char_service = CharacterService(db)
    character = await char_service.get_character_by_user_id(current_user.id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found. Create a character first."
        )
    return character


@router.get("", response_model=TaskListResponse)
async def get_tasks(
    current_user: CurrentUser,
    db: DBSession,
    task_type: Optional[TaskType] = None,
    difficulty: Optional[TaskDifficulty] = None,
    is_active: Optional[bool] = True,
    ritual_time: Optional[RitualTime] = None,
):
    """Get all tasks with optional filtering."""
    character = await get_user_character(current_user, db)
    service = TaskService(db)

    filters = TaskFilters(
        task_type=task_type,
        difficulty=difficulty,
        is_active=is_active,
        ritual_time=ritual_time,
    )

    tasks = await service.get_tasks(character.id, filters)
    task_responses = [await service.to_response(t, character.id) for t in tasks]

    return TaskListResponse(tasks=task_responses, total=len(task_responses))


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Create a new task."""
    character = await get_user_character(current_user, db)
    service = TaskService(db)

    task = await service.create_task(character.id, task_data)
    return await service.to_response(task, character.id)


@router.get("/daily/today", response_model=List[TaskResponse])
async def get_today_dailies(current_user: CurrentUser, db: DBSession):
    """Get dailies scheduled for today."""
    character = await get_user_character(current_user, db)
    service = TaskService(db)

    tasks = await service.get_dailies_for_today(character.id)
    return [await service.to_response(t, character.id) for t in tasks]


@router.get("/todos/pending", response_model=List[TaskResponse])
async def get_pending_todos(current_user: CurrentUser, db: DBSession):
    """Get pending todos."""
    character = await get_user_character(current_user, db)
    service = TaskService(db)

    tasks = await service.get_pending_todos(character.id)
    return [await service.to_response(t, character.id) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """Get a specific task."""
    character = await get_user_character(current_user, db)
    service = TaskService(db)

    task = await service.get_task_by_id(task_id, character.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return await service.to_response(task, character.id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    update_data: TaskUpdate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Update a task."""
    character = await get_user_character(current_user, db)
    service = TaskService(db)

    task = await service.get_task_by_id(task_id, character.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task = await service.update_task(task, update_data)
    return await service.to_response(task, character.id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """Delete a task."""
    character = await get_user_character(current_user, db)
    service = TaskService(db)

    task = await service.get_task_by_id(task_id, character.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    await service.delete_task(task)
    return None


@router.post("/{task_id}/complete", response_model=TaskCompletionResponse)
async def complete_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """Complete a task and receive rewards."""
    character = await get_user_character(current_user, db)
    service = TaskService(db)

    task = await service.get_task_by_id(task_id, character.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Check if daily already completed today
    if task.task_type == "daily":
        if await service.is_completed_today(task.id, character.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Daily already completed today"
            )

    # Check if todo already completed
    if task.task_type == "todo" and task.completed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Todo already completed"
        )

    return await service.complete_task(task, character)


@router.post("/{task_id}/uncomplete", status_code=status.HTTP_200_OK)
async def uncomplete_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """Undo task completion (same day only)."""
    character = await get_user_character(current_user, db)
    service = TaskService(db)

    task = await service.get_task_by_id(task_id, character.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    success = await service.uncomplete_task(task.id, character.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No completion found for today"
        )

    return {"message": "Task completion undone"}
```

### 4. Update Main App

Update `backend/app/main.py`:

```python
# Add import
from app.api.v1.tasks import router as tasks_router

# Add after character router
app.include_router(tasks_router, prefix="/api/v1")
```

---

## Success Criteria

- [ ] GET /api/v1/tasks returns all user's tasks
- [ ] POST /api/v1/tasks creates task with correct rewards
- [ ] GET /api/v1/tasks/{id} returns specific task
- [ ] PATCH /api/v1/tasks/{id} updates task
- [ ] DELETE /api/v1/tasks/{id} removes task
- [ ] POST /api/v1/tasks/{id}/complete grants correct rewards
- [ ] Cannot complete daily twice in same day
- [ ] Filtering by type/difficulty works
- [ ] GET /api/v1/tasks/daily/today returns today's dailies
- [ ] GET /api/v1/tasks/todos/pending returns pending todos

---

## Test Instructions

1. Create daily task:
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Morning Exercise",
    "task_type": "daily",
    "difficulty": "medium",
    "repeat_days": [1,2,3,4,5],
    "ritual_time": "morning"
  }'
```

2. Complete task:
```bash
curl -X POST http://localhost:8000/api/v1/tasks/<task_id>/complete \
  -H "Authorization: Bearer <token>"
```

3. Get today's dailies:
```bash
curl http://localhost:8000/api/v1/tasks/daily/today \
  -H "Authorization: Bearer <token>"
```

4. Filter by type:
```bash
curl "http://localhost:8000/api/v1/tasks?task_type=daily" \
  -H "Authorization: Bearer <token>"
```
