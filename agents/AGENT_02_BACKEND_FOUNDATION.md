# Agent Task: Backend Foundation - FastAPI Setup

## Task ID: CHUNK-1.2
## Priority: CRITICAL
## Estimated Time: 3-4 hours
## Dependencies: CHUNK-1.1 (Infrastructure)

---

## Objective

Setup the FastAPI backend foundation with proper project structure, configuration, database connection, and migrations.

---

## Context

QuestForge backend uses:
- FastAPI 0.109+ with async support
- SQLAlchemy 2.0 with async driver (asyncpg)
- Alembic for database migrations
- Pydantic Settings for configuration

---

## Deliverables

### 1. Configuration Module

Create `backend/app/core/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "QuestForge"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.3:70b"

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Timezone
    TIMEZONE: str = "America/Mexico_City"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

### 2. Database Session

Create `backend/app/db/session.py`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """Dependency for getting async database session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

### 3. Database Base Models

Create `backend/app/db/base.py`:

```python
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class UUIDMixin:
    """Mixin for UUID primary key."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)


# Import all models here for Alembic to detect
# This will be populated as models are created
```

### 4. API Dependencies

Create `backend/app/api/deps.py`:

```python
from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Type alias for dependency injection
DBSession = Annotated[AsyncSession, Depends(get_db)]
```

### 5. Main Application

Create `backend/app/main.py`:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting {settings.APP_NAME}...")
    yield
    # Shutdown
    print(f"Shutting down {settings.APP_NAME}...")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="RPG-style habit tracker with AI-generated narratives",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": settings.APP_NAME}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "health": "/health"
    }


# Import and include routers here as they are created
# from app.api.v1 import auth, character, tasks
# app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
```

### 6. API Router Structure

Create `backend/app/api/__init__.py`:
```python
# API module
```

Create `backend/app/api/v1/__init__.py`:
```python
# API v1 module
```

Create placeholder router `backend/app/api/v1/health.py`:
```python
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def api_health():
    """API health check."""
    return {"status": "ok", "version": "v1"}
```

### 7. Alembic Configuration

Initialize Alembic:
```bash
cd backend
alembic init alembic
```

Update `backend/alembic/env.py`:

```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Import your models' Base
from app.db.session import Base
from app.core.config import settings

# Import all models so they are registered with Base.metadata
# from app.db.models import user, character, task  # Uncomment as models are added

config = context.config

# Set the database URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

Update `backend/alembic.ini`:
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### 8. Utility Modules

Create `backend/app/utils/__init__.py`:
```python
# Utilities module
```

Create `backend/app/utils/calculations.py`:
```python
"""Game mechanics calculations."""


def calculate_xp_to_next_level(level: int) -> int:
    """Calculate XP required to reach the next level.

    Formula: 100 * (1.1 ^ (level - 1))

    Examples:
        Level 1 -> 2: 100 XP
        Level 2 -> 3: 110 XP
        Level 5 -> 6: 146 XP
        Level 10 -> 11: 236 XP
    """
    return int(100 * (1.1 ** (level - 1)))


def calculate_task_rewards(difficulty: str, streak_days: int = 0) -> dict:
    """Calculate rewards for completing a task.

    Args:
        difficulty: Task difficulty (trivial, easy, medium, hard)
        streak_days: Current streak for bonus calculation

    Returns:
        dict with experience, gold, mana, energy rewards
    """
    base_rewards = {
        "trivial": {"experience": 5, "gold": 1},
        "easy": {"experience": 10, "gold": 2},
        "medium": {"experience": 20, "gold": 5},
        "hard": {"experience": 40, "gold": 10},
    }

    rewards = base_rewards.get(difficulty, base_rewards["medium"]).copy()

    # Streak bonus (1% per day, max 50%)
    streak_multiplier = 1 + min(streak_days * 0.01, 0.5)
    rewards["experience"] = int(rewards["experience"] * streak_multiplier)

    return rewards
```

### 9. Init Files

Create empty `__init__.py` files:
- `backend/app/__init__.py`
- `backend/app/core/__init__.py`
- `backend/app/db/__init__.py`
- `backend/app/db/models/__init__.py`
- `backend/app/schemas/__init__.py`
- `backend/app/services/__init__.py`

---

## Success Criteria

- [ ] FastAPI application starts without errors
- [ ] `/health` endpoint returns `{"status": "healthy"}`
- [ ] `/docs` shows Swagger documentation
- [ ] `/redoc` shows ReDoc documentation
- [ ] Database connection is established (check logs)
- [ ] Alembic is configured and can create migrations
- [ ] Configuration loads from environment variables

---

## Test Instructions

1. Ensure infrastructure is running (`docker-compose up -d`)
2. Check backend logs: `docker-compose logs backend`
3. Visit http://localhost:8000/health
4. Visit http://localhost:8000/docs
5. Run Alembic check: `docker-compose exec backend alembic current`

---

## Notes

- Database models will be added by AGENT_03
- Authentication will be added by AGENT_04
- API routers will be added progressively by other agents
