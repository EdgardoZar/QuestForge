# Agent Task: Character API

## Task ID: CHUNK-1.5
## Priority: CRITICAL
## Estimated Time: 4-5 hours
## Dependencies: CHUNK-1.4 (Authentication)

---

## Objective

Implement the Character API with CRUD operations, class selection, and stats management.

---

## Deliverables

### 1. Character Schemas

Create `backend/app/schemas/character.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class CharacterClass(str, Enum):
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    HEALER = "healer"


class CharacterCreate(BaseModel):
    """Schema for creating a character."""
    name: str = Field(..., min_length=1, max_length=100)
    character_class: CharacterClass


class CharacterUpdate(BaseModel):
    """Schema for updating a character."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    title: Optional[str] = Field(None, max_length=100)


class CharacterStats(BaseModel):
    """Schema for character stats."""
    level: int
    experience: int
    experience_to_next: int
    health_current: int
    health_max: int
    mana_current: int
    mana_max: int
    energy_current: int
    energy_max: int
    gold: int
    gems: int
    streak_days: int
    total_tasks_completed: int


class CharacterResponse(BaseModel):
    """Schema for character response."""
    id: UUID
    user_id: UUID
    name: str
    character_class: CharacterClass
    level: int
    experience: int
    experience_to_next: int
    health_current: int
    health_max: int
    mana_current: int
    mana_max: int
    energy_current: int
    energy_max: int
    gold: int
    gems: int
    streak_days: int
    total_tasks_completed: int
    avatar_url: Optional[str]
    title: Optional[str]
    created_at: datetime
    last_daily_reset: datetime

    class Config:
        from_attributes = True


class CharacterStatsResponse(BaseModel):
    """Schema for detailed stats response."""
    character: CharacterResponse
    xp_progress_percent: float
    health_percent: float
    mana_percent: float
    energy_percent: float


class ClassInfo(BaseModel):
    """Schema for class information."""
    name: CharacterClass
    display_name: str
    description: str
    specialty: str
    icon: str


# Class definitions for frontend
CLASS_INFO = {
    CharacterClass.WARRIOR: ClassInfo(
        name=CharacterClass.WARRIOR,
        display_name="Warrior",
        description="Masters of discipline and strength. Warriors excel at consistent daily routines and pushing through challenges.",
        specialty="HP Recovery, Protection, Task Persistence",
        icon="sword",
    ),
    CharacterClass.MAGE: ClassInfo(
        name=CharacterClass.MAGE,
        display_name="Mage",
        description="Scholars of arcane knowledge. Mages manipulate time and energy to maximize productivity.",
        specialty="XP Boosts, Mana Efficiency, Task Automation",
        icon="wand",
    ),
    CharacterClass.ROGUE: ClassInfo(
        name=CharacterClass.ROGUE,
        display_name="Rogue",
        description="Cunning opportunists. Rogues find shortcuts and bonuses, turning challenges into advantages.",
        specialty="Gold Bonuses, Task Skipping, Multi-tasking",
        icon="dagger",
    ),
    CharacterClass.HEALER: ClassInfo(
        name=CharacterClass.HEALER,
        display_name="Healer",
        description="Nurturers of growth. Healers sustain long-term progress and recover from setbacks gracefully.",
        specialty="HP/Mana Restoration, Energy Generation, Resilience",
        icon="heart",
    ),
}
```

### 2. Character Service

Create `backend/app/services/character_service.py`:

```python
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Character, User
from app.schemas.character import (
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse,
    CharacterStatsResponse,
)


class CharacterService:
    """Service for character operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_character_by_user_id(self, user_id: UUID) -> Optional[Character]:
        """Get character by user ID."""
        result = await self.db.execute(
            select(Character).where(Character.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_character_by_id(self, character_id: UUID) -> Optional[Character]:
        """Get character by ID."""
        result = await self.db.execute(
            select(Character).where(Character.id == character_id)
        )
        return result.scalar_one_or_none()

    async def create_character(
        self, user_id: UUID, character_data: CharacterCreate
    ) -> Character:
        """Create a new character for a user."""
        character = Character(
            user_id=user_id,
            name=character_data.name,
            character_class=character_data.character_class.value,
        )
        self.db.add(character)
        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def update_character(
        self, character: Character, update_data: CharacterUpdate
    ) -> Character:
        """Update character fields."""
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(character, field, value)
        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def delete_character(self, character: Character) -> None:
        """Delete a character."""
        await self.db.delete(character)
        await self.db.commit()

    async def add_experience(self, character: Character, amount: int) -> Character:
        """Add experience to character (triggers level-up automatically via DB trigger)."""
        character.experience += amount
        character.total_tasks_completed += 1
        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def add_gold(self, character: Character, amount: int) -> Character:
        """Add gold to character."""
        character.gold += amount
        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def modify_health(self, character: Character, amount: int) -> Character:
        """Modify character health (can be positive or negative)."""
        new_health = character.health_current + amount
        character.health_current = max(0, min(new_health, character.health_max))
        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def modify_mana(self, character: Character, amount: int) -> Character:
        """Modify character mana (can be positive or negative)."""
        new_mana = character.mana_current + amount
        character.mana_current = max(0, min(new_mana, character.mana_max))
        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def modify_energy(self, character: Character, amount: int) -> Character:
        """Modify character energy (can be positive or negative)."""
        new_energy = character.energy_current + amount
        character.energy_current = max(0, min(new_energy, character.energy_max))
        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def update_streak(self, character: Character, increment: bool) -> Character:
        """Update streak (increment or reset)."""
        if increment:
            character.streak_days += 1
        else:
            character.streak_days = 0
        await self.db.commit()
        await self.db.refresh(character)
        return character

    def to_response(self, character: Character) -> CharacterResponse:
        """Convert character to response schema."""
        return CharacterResponse(
            id=character.id,
            user_id=character.user_id,
            name=character.name,
            character_class=character.character_class,
            level=character.level,
            experience=character.experience,
            experience_to_next=character.experience_to_next,
            health_current=character.health_current,
            health_max=character.health_max,
            mana_current=character.mana_current,
            mana_max=character.mana_max,
            energy_current=character.energy_current,
            energy_max=character.energy_max,
            gold=character.gold,
            gems=character.gems,
            streak_days=character.streak_days,
            total_tasks_completed=character.total_tasks_completed,
            avatar_url=character.avatar_url,
            title=character.title,
            created_at=character.created_at,
            last_daily_reset=character.last_daily_reset,
        )

    def to_stats_response(self, character: Character) -> CharacterStatsResponse:
        """Convert character to detailed stats response."""
        return CharacterStatsResponse(
            character=self.to_response(character),
            xp_progress_percent=(character.experience / character.experience_to_next) * 100 if character.experience_to_next > 0 else 0,
            health_percent=(character.health_current / character.health_max) * 100 if character.health_max > 0 else 0,
            mana_percent=(character.mana_current / character.mana_max) * 100 if character.mana_max > 0 else 0,
            energy_percent=(character.energy_current / character.energy_max) * 100 if character.energy_max > 0 else 0,
        )
```

### 3. Character Router

Create `backend/app/api/v1/character.py`:

```python
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.api.deps import DBSession, CurrentUser
from app.schemas.character import (
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse,
    CharacterStatsResponse,
    ClassInfo,
    CLASS_INFO,
    CharacterClass,
)
from app.services.character_service import CharacterService

router = APIRouter(prefix="/character", tags=["Character"])


@router.get("/classes", response_model=List[ClassInfo])
async def get_classes():
    """Get available character classes with descriptions."""
    return list(CLASS_INFO.values())


@router.post("", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    character_data: CharacterCreate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Create a new character for the current user."""
    service = CharacterService(db)

    # Check if user already has a character
    existing = await service.get_character_by_user_id(current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a character"
        )

    character = await service.create_character(current_user.id, character_data)
    return service.to_response(character)


@router.get("", response_model=CharacterResponse)
async def get_character(current_user: CurrentUser, db: DBSession):
    """Get current user's character."""
    service = CharacterService(db)
    character = await service.get_character_by_user_id(current_user.id)

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    return service.to_response(character)


@router.get("/stats", response_model=CharacterStatsResponse)
async def get_character_stats(current_user: CurrentUser, db: DBSession):
    """Get detailed character stats."""
    service = CharacterService(db)
    character = await service.get_character_by_user_id(current_user.id)

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    return service.to_stats_response(character)


@router.patch("", response_model=CharacterResponse)
async def update_character(
    update_data: CharacterUpdate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Update current user's character."""
    service = CharacterService(db)
    character = await service.get_character_by_user_id(current_user.id)

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    character = await service.update_character(character, update_data)
    return service.to_response(character)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(current_user: CurrentUser, db: DBSession):
    """Delete current user's character (WARNING: This is permanent!)."""
    service = CharacterService(db)
    character = await service.get_character_by_user_id(current_user.id)

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    await service.delete_character(character)
    return None
```

### 4. Update Main App

Update `backend/app/main.py` to include character router:

```python
# Add import
from app.api.v1.character import router as character_router

# Add after auth router
app.include_router(character_router, prefix="/api/v1")
```

---

## Success Criteria

- [ ] GET /api/v1/character/classes returns all 4 classes
- [ ] POST /api/v1/character creates character with correct class
- [ ] GET /api/v1/character returns user's character
- [ ] GET /api/v1/character/stats returns detailed stats with percentages
- [ ] PATCH /api/v1/character updates name/avatar/title
- [ ] DELETE /api/v1/character removes character
- [ ] Cannot create second character for same user

---

## Test Instructions

1. Get classes:
```bash
curl http://localhost:8000/api/v1/character/classes
```

2. Create character:
```bash
curl -X POST http://localhost:8000/api/v1/character \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "MyHero", "character_class": "warrior"}'
```

3. Get character:
```bash
curl http://localhost:8000/api/v1/character \
  -H "Authorization: Bearer <token>"
```

4. Get stats:
```bash
curl http://localhost:8000/api/v1/character/stats \
  -H "Authorization: Bearer <token>"
```

5. Update character:
```bash
curl -X PATCH http://localhost:8000/api/v1/character \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "NewName", "title": "The Brave"}'
```
