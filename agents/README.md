# QuestForge Agent Task Files

This directory contains individual task specifications for parallel agent development of QuestForge.

## Overview

Each agent file (AGENT_XX_*.md) contains:
- Task ID and priority
- Dependencies on other tasks
- Detailed implementation requirements
- Success criteria
- Test instructions

## Task Execution Order

### Phase 1: MVP Core (Weeks 1-3)

```
AGENT_01 (Infrastructure)
    ↓
AGENT_02 (Backend Foundation) ←→ AGENT_08 (Frontend Setup)
    ↓                               ↓
AGENT_03 (Database Models)      AGENT_09 (Auth Pages)
    ↓                               ↓
AGENT_04 (Authentication)       AGENT_10 (Character UI)
    ↓                               ↓
AGENT_05 (Character API)        AGENT_11 (Task UI)
    ↓
AGENT_06 (Tasks API)
    ↓
AGENT_07 (Daily Reset/Celery)
```

### Phase 2: Game Features (Weeks 4-5)

```
AGENT_12 (Abilities Models + Seed)
    ↓
AGENT_13 (Abilities API) ←→ AGENT_14 (Rituals API)
    ↓                           ↓
AGENT_15 (Abilities UI)     AGENT_16 (Rituals UI)
```

### Phase 3: Paths & Narrative (Weeks 6-7)

```
AGENT_17 (Paths Models + Seed)
    ↓
AGENT_18 (Paths API) ←→ AGENT_19 (Ollama Integration)
    ↓                       ↓
AGENT_20 (Paths UI)     AGENT_21 (Narrative Service)
                            ↓
                        AGENT_22 (Narrative UI)
```

### Phase 4: Extras (Week 8)

```
AGENT_23 (Dice Roller Backend)    AGENT_25 (Telegram Bot Basic)
    ↓                                   ↓
AGENT_24 (Dice Roller UI)         AGENT_26 (Telegram Advanced)
```

### Phase 5: Polish (Week 9+)

```
AGENT_27 (PWA Setup)
AGENT_28 (Mobile Optimization)
AGENT_29 (Backend Tests)
AGENT_30 (Frontend Tests)
```

## Available Agent Tasks

| File | Task | Priority | Est. Time | Dependencies |
|------|------|----------|-----------|--------------|
| AGENT_01_INFRASTRUCTURE.md | Docker, project structure | CRITICAL | 4-6h | None |
| AGENT_02_BACKEND_FOUNDATION.md | FastAPI setup | CRITICAL | 3-4h | AGENT_01 |
| AGENT_03_DATABASE_MODELS.md | SQLAlchemy models | CRITICAL | 4-5h | AGENT_02 |
| AGENT_04_AUTHENTICATION.md | JWT auth system | CRITICAL | 3-4h | AGENT_03 |
| AGENT_05_CHARACTER_API.md | Character CRUD | CRITICAL | 4-5h | AGENT_04 |
| AGENT_06_TASKS_API.md | Tasks CRUD + completion | CRITICAL | 5-6h | AGENT_05 |

## Parallel Execution Opportunities

The following tasks can be executed in parallel:

### Stream A (Backend):
1. AGENT_01 → AGENT_02 → AGENT_03 → AGENT_04 → AGENT_05 → AGENT_06 → AGENT_07

### Stream B (Frontend - can start after AGENT_01):
1. AGENT_08 → AGENT_09 → AGENT_10 → AGENT_11

### Stream C (Game Features - after Phase 1):
1. AGENT_12 → AGENT_13/AGENT_14 (parallel) → AGENT_15/AGENT_16 (parallel)

### Stream D (Narrative - after Phase 1):
1. AGENT_17 → AGENT_18 → AGENT_20
2. AGENT_19 → AGENT_21 → AGENT_22

### Stream E (Extras - after Phase 1):
1. AGENT_23 → AGENT_24
2. AGENT_25 → AGENT_26

## How to Use These Files

### For Single Agent Execution:
```
Read the agent file and implement all deliverables in order.
Verify against success criteria before marking complete.
```

### For Parallel Agent Orchestration:
```
1. Check dependencies are satisfied
2. Assign independent streams to different agents
3. Synchronize at dependency points
4. Verify integration between streams
```

## Quick Reference

### Tech Stack
- **Backend**: FastAPI 0.109+, SQLAlchemy 2.0 async, PostgreSQL 16, Redis, Celery
- **Frontend**: React 18, TypeScript, Vite, TailwindCSS, shadcn/ui, Redux Toolkit
- **AI**: Ollama with Llama 3.3 70B
- **Bot**: python-telegram-bot 20.x

### Key Ports
- Frontend: 5173 (dev), 80 (nginx)
- Backend: 8000
- PostgreSQL: 5432
- Redis: 6379
- Ollama: 11434 (host)

### Common Commands
```bash
make build    # Build all containers
make up       # Start services
make down     # Stop services
make logs     # View all logs
make migrate  # Run migrations
make seed     # Seed data
make test     # Run tests
```

## Notes

- Each agent task is designed to be completed in one focused session
- All code should follow existing patterns established in earlier tasks
- Test your work against the success criteria before moving on
- Document any deviations from the plan
