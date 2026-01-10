# QuestForge - Implementation Task Plan

> **Comprehensive task breakdown for agent delegation**
> Generated from the QuestForge Development Plan

---

## Overview

This document breaks down the QuestForge RPG habit tracker into executable work chunks suitable for parallel agent development. Each chunk is designed to be:

- **Self-contained**: Can be developed independently
- **Testable**: Has clear success criteria
- **Sized appropriately**: 2-8 hours of focused work
- **Well-documented**: Clear inputs/outputs

---

## Phase 1: MVP Core (Weeks 1-3)

### CHUNK 1.1: Project Setup & Infrastructure
**Priority**: CRITICAL | **Estimated Time**: 4-6 hours | **Dependencies**: None

#### Tasks:
1. Create project directory structure:
   ```
   questforge/
   ├── backend/
   ├── frontend/
   ├── telegram-bot/
   ├── nginx/
   ├── docker-compose.yml
   ├── .env.example
   └── Makefile
   ```

2. Create Docker Compose configuration with services:
   - PostgreSQL 16
   - Redis 7
   - Backend (FastAPI)
   - Frontend (React/Vite)
   - Celery Worker
   - Celery Beat
   - Nginx

3. Create environment configuration (.env.example)

4. Create Makefile with common commands

#### Success Criteria:
- [ ] `docker-compose up` starts all services without errors
- [ ] Services can communicate with each other
- [ ] Environment variables are properly loaded

#### Agent Instruction:
```
Create the complete project infrastructure for QuestForge including:
- Docker Compose with PostgreSQL, Redis, FastAPI backend, React frontend, Celery
- Environment configuration template
- Makefile for common operations
Follow the structure defined in the plan document.
```

---

### CHUNK 1.2: Backend Foundation - FastAPI Setup
**Priority**: CRITICAL | **Estimated Time**: 3-4 hours | **Dependencies**: CHUNK 1.1

#### Tasks:
1. Setup FastAPI application structure:
   ```
   backend/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py
   │   ├── config.py
   │   ├── api/
   │   ├── core/
   │   ├── db/
   │   ├── schemas/
   │   ├── services/
   │   └── utils/
   ├── requirements.txt
   └── Dockerfile
   ```

2. Implement core configuration (Pydantic Settings)

3. Setup SQLAlchemy 2.0 with async support

4. Configure Alembic for migrations

5. Implement base health check endpoint

#### Success Criteria:
- [ ] FastAPI app starts and responds on `/health`
- [ ] Database connection established
- [ ] Alembic migrations run successfully

#### Agent Instruction:
```
Setup the FastAPI backend foundation for QuestForge:
- FastAPI 0.109+ with async support
- SQLAlchemy 2.0 async configuration
- Alembic migrations setup
- Pydantic settings configuration
- Basic project structure as defined in plan
```

---

### CHUNK 1.3: Database Models - Core Entities
**Priority**: CRITICAL | **Estimated Time**: 4-5 hours | **Dependencies**: CHUNK 1.2

#### Tasks:
1. Create SQLAlchemy models:
   - `User` - authentication and settings
   - `Character` - player character with stats
   - `Task` - habits, dailies, and todos
   - `TaskCompletion` - task completion history

2. Create Alembic migration for initial schema

3. Add database constraints and indexes

4. Implement PostgreSQL triggers:
   - Auto level-up trigger
   - Daily stats update trigger

#### Success Criteria:
- [ ] All models created with proper relationships
- [ ] Migrations apply successfully
- [ ] Constraints enforce data integrity
- [ ] Triggers work as expected

#### Agent Instruction:
```
Create the core database models for QuestForge:
- User, Character, Task, TaskCompletion models
- Follow the SQL schema from the plan document exactly
- Include all JSONB fields, enums, constraints
- Create the experience calculation function and level-up trigger
- Include proper indexes for performance
```

---

### CHUNK 1.4: Authentication System
**Priority**: CRITICAL | **Estimated Time**: 3-4 hours | **Dependencies**: CHUNK 1.3

#### Tasks:
1. Implement security utilities:
   - Password hashing (bcrypt)
   - JWT token generation/validation
   - Token refresh mechanism

2. Create authentication endpoints:
   - `POST /api/v1/auth/register`
   - `POST /api/v1/auth/login`
   - `POST /api/v1/auth/refresh`
   - `GET /api/v1/auth/me`

3. Create authentication dependency for protected routes

4. Add Pydantic schemas for auth requests/responses

#### Success Criteria:
- [ ] User can register with email/password
- [ ] User can login and receive JWT token
- [ ] Protected endpoints reject invalid tokens
- [ ] Token refresh works correctly

#### Agent Instruction:
```
Implement JWT authentication for QuestForge backend:
- bcrypt password hashing
- JWT token generation with configurable expiry
- Token refresh mechanism
- Auth endpoints: register, login, refresh, me
- FastAPI dependency for protected routes
```

---

### CHUNK 1.5: Character API
**Priority**: CRITICAL | **Estimated Time**: 4-5 hours | **Dependencies**: CHUNK 1.4

#### Tasks:
1. Create Pydantic schemas:
   - `CharacterCreate`
   - `CharacterUpdate`
   - `CharacterResponse`
   - `CharacterStats`

2. Implement Character service:
   - Create character with class selection
   - Get character with computed stats
   - Update character (name, avatar)
   - Delete character

3. Create Character endpoints:
   - `POST /api/v1/character`
   - `GET /api/v1/character`
   - `PATCH /api/v1/character`
   - `DELETE /api/v1/character`
   - `GET /api/v1/character/stats`

4. Implement XP and leveling calculations

#### Success Criteria:
- [ ] Character creation with class selection works
- [ ] Character stats are computed correctly
- [ ] XP to next level calculation is accurate
- [ ] Character updates persist correctly

#### Agent Instruction:
```
Implement the Character API for QuestForge:
- Character CRUD operations
- Class selection (warrior, mage, rogue, healer)
- Stats computation (HP, Mana, Energy, XP)
- XP calculation formula: 100 * (1.1 ^ (level - 1))
- Proper Pydantic schemas with validation
```

---

### CHUNK 1.6: Tasks API
**Priority**: CRITICAL | **Estimated Time**: 5-6 hours | **Dependencies**: CHUNK 1.5

#### Tasks:
1. Create Pydantic schemas:
   - `TaskCreate`, `TaskUpdate`, `TaskResponse`
   - `TaskCompletion`, `TaskCompletionResponse`

2. Implement Task service:
   - CRUD operations for tasks
   - Task completion with reward calculation
   - Task uncomplete (same day only)
   - Filter by type, difficulty, active status

3. Create Task endpoints:
   - `GET /api/v1/tasks`
   - `POST /api/v1/tasks`
   - `GET /api/v1/tasks/{id}`
   - `PATCH /api/v1/tasks/{id}`
   - `DELETE /api/v1/tasks/{id}`
   - `POST /api/v1/tasks/{id}/complete`
   - `POST /api/v1/tasks/{id}/uncomplete`

4. Implement reward calculation:
   - XP rewards by difficulty
   - Gold rewards
   - Mana/Energy rewards

#### Success Criteria:
- [ ] Tasks can be created with all types (daily, todo, habit)
- [ ] Task completion grants correct rewards
- [ ] Character stats update after completion
- [ ] Filtering works correctly

#### Agent Instruction:
```
Implement the Tasks API for QuestForge:
- Task CRUD with types: daily, todo, habit
- Difficulty levels: trivial (5 XP), easy (10 XP), medium (20 XP), hard (40 XP)
- Task completion logic with rewards
- Character stat updates on completion
- Filtering by type, difficulty, active status
```

---

### CHUNK 1.7: Daily Reset System (Celery)
**Priority**: HIGH | **Estimated Time**: 4-5 hours | **Dependencies**: CHUNK 1.6

#### Tasks:
1. Setup Celery with Redis broker

2. Create daily reset task:
   - Regenerate Mana to 100%
   - Check incomplete dailies → -10 HP each
   - Update streak (increment if all dailies done, reset otherwise)
   - Reset daily task completion flags
   - Generate daily stats record

3. Setup Celery Beat schedule (00:00 user timezone)

4. Create notification triggers (placeholder for Telegram)

#### Success Criteria:
- [ ] Celery worker processes tasks
- [ ] Daily reset runs at scheduled time
- [ ] HP decreases for missed dailies
- [ ] Mana regenerates to max
- [ ] Streak updates correctly

#### Agent Instruction:
```
Implement the Celery daily reset system for QuestForge:
- Celery + Redis configuration
- Daily reset task at midnight:
  - Mana regeneration (100%)
  - HP decay (-10 per missed daily)
  - Streak calculation
  - Daily stats generation
- Celery Beat scheduling
```

---

### CHUNK 1.8: Frontend Setup - React/Vite
**Priority**: CRITICAL | **Estimated Time**: 3-4 hours | **Dependencies**: CHUNK 1.1

#### Tasks:
1. Create React + TypeScript + Vite project:
   ```
   frontend/
   ├── src/
   │   ├── main.tsx
   │   ├── App.tsx
   │   ├── components/
   │   ├── features/
   │   ├── hooks/
   │   ├── pages/
   │   ├── services/
   │   ├── store/
   │   ├── types/
   │   └── utils/
   ├── package.json
   └── Dockerfile
   ```

2. Setup TailwindCSS + shadcn/ui

3. Configure Redux Toolkit store

4. Setup Axios + React Query for API calls

5. Create basic routing with React Router

#### Success Criteria:
- [ ] Vite dev server starts correctly
- [ ] TailwindCSS styles apply
- [ ] Redux store is accessible
- [ ] API client configured

#### Agent Instruction:
```
Setup the React frontend for QuestForge:
- Vite + React 18 + TypeScript
- TailwindCSS 3.x + shadcn/ui components
- Redux Toolkit for state management
- Axios + React Query for API calls
- React Router for navigation
- Follow the project structure from plan
```

---

### CHUNK 1.9: Frontend - Auth Pages
**Priority**: HIGH | **Estimated Time**: 4-5 hours | **Dependencies**: CHUNK 1.8, CHUNK 1.4

#### Tasks:
1. Create auth Redux slice:
   - Login action
   - Register action
   - Logout action
   - Token storage

2. Create Login page:
   - Email/password form
   - Validation
   - Error handling
   - Redirect on success

3. Create Register page:
   - Email/username/password form
   - Validation
   - Success redirect to character creation

4. Implement protected route wrapper

#### Success Criteria:
- [ ] User can register new account
- [ ] User can login and see dashboard
- [ ] Invalid credentials show error
- [ ] Protected routes redirect to login

#### Agent Instruction:
```
Implement authentication pages for QuestForge frontend:
- Redux auth slice with login/register/logout
- Login page with form validation
- Register page with form validation
- Protected route component
- Token storage in localStorage
- Redirect flows
```

---

### CHUNK 1.10: Frontend - Character Creation & Dashboard
**Priority**: HIGH | **Estimated Time**: 5-6 hours | **Dependencies**: CHUNK 1.9, CHUNK 1.5

#### Tasks:
1. Create character Redux slice

2. Create Character Creation page:
   - Name input
   - Class selection (4 cards with descriptions)
   - Class preview with stats
   - Create button

3. Create Dashboard layout:
   - Character card with avatar/name/class
   - Stats bars (HP, Mana, Energy)
   - XP progress bar with level
   - Navigation sidebar

4. Create reusable components:
   - `StatsBar` component
   - `LevelProgress` component
   - `CharacterCard` component

#### Success Criteria:
- [ ] Character creation flow works end-to-end
- [ ] Dashboard displays character stats
- [ ] Stats bars are animated
- [ ] Class theming applied

#### Agent Instruction:
```
Implement character creation and dashboard for QuestForge:
- Character creation page with class selection
- Class cards showing: Warrior, Mage, Rogue, Healer
- Dashboard layout with character stats
- Animated HP/Mana/Energy bars
- XP progress bar with level display
- Use shadcn/ui components and Framer Motion for animations
```

---

### CHUNK 1.11: Frontend - Task Management
**Priority**: HIGH | **Estimated Time**: 6-7 hours | **Dependencies**: CHUNK 1.10, CHUNK 1.6

#### Tasks:
1. Create tasks Redux slice:
   - Fetch tasks
   - Create task
   - Complete task
   - Filter tasks

2. Create Task List page:
   - Tabs: Dailies, Todos, Habits
   - Task cards with difficulty indicator
   - Complete button with animation
   - Filter/sort options

3. Create Task Form component:
   - Title, description
   - Type selection
   - Difficulty selection
   - Repeat days (for dailies)
   - Due date (for todos)

4. Create Task Item component:
   - Task info display
   - Complete action
   - Edit/delete actions
   - Completion animation

#### Success Criteria:
- [ ] Tasks display by category
- [ ] Task creation works with all types
- [ ] Task completion updates character stats
- [ ] Completion animation shows rewards

#### Agent Instruction:
```
Implement task management UI for QuestForge:
- Task list with tabs for Dailies, Todos, Habits
- Task creation form with type, difficulty, schedule
- Task completion with reward animation
- Redux integration for state
- Optimistic updates with React Query
- Use Framer Motion for completion animations
```

---

## Phase 2: Abilities & Rituals (Weeks 4-5)

### CHUNK 2.1: Database Models - Abilities & Rituals
**Priority**: HIGH | **Estimated Time**: 3-4 hours | **Dependencies**: Phase 1

#### Tasks:
1. Create SQLAlchemy models:
   - `Ability` - class abilities definition
   - `CharacterAbility` - unlocked abilities per character
   - `Ritual` - ritual groups (morning/afternoon/evening)
   - `RitualCompletion` - ritual completion history

2. Create Alembic migration

3. Add ability effect type enum

#### Success Criteria:
- [ ] Models created with relationships
- [ ] Migration applies successfully
- [ ] Cooldown tracking works

#### Agent Instruction:
```
Create database models for abilities and rituals:
- Ability model with effect types (restore_hp, xp_boost, skip_daily, etc.)
- CharacterAbility with cooldown tracking
- Ritual model with task array reference
- RitualCompletion for bonus tracking
Follow the SQL schema from the plan exactly.
```

---

### CHUNK 2.2: Abilities Seed Data
**Priority**: HIGH | **Estimated Time**: 3-4 hours | **Dependencies**: CHUNK 2.1

#### Tasks:
1. Create seed script with all 16 abilities:
   - 4 Warrior abilities (Second Wind, Battle Cry, Iron Will, Victory Rush)
   - 4 Mage abilities (Meditation, Time Warp, Arcane Insight, Mana Surge)
   - 4 Rogue abilities (Lucky Break, Stealth, Perfect Execution, Shadow Clone)
   - 4 Healer abilities (Divine Blessing, Inspiration, Serenity, Phoenix Rebirth)

2. Include all ability stats:
   - Mana/Energy costs
   - Cooldowns
   - Level requirements
   - Effect data (JSON)

#### Success Criteria:
- [ ] All 16 abilities seeded correctly
- [ ] Effect data is properly structured
- [ ] Level requirements are set

#### Agent Instruction:
```
Create seed data for all 16 class abilities:
Follow the exact specifications from the plan:
- Warrior: Second Wind (L1), Battle Cry (L3), Iron Will (L5), Victory Rush (L8)
- Mage: Meditation (L1), Time Warp (L3), Arcane Insight (L5), Mana Surge (L8)
- Rogue: Lucky Break (L1), Stealth (L3), Perfect Execution (L5), Shadow Clone (L8)
- Healer: Divine Blessing (L1), Inspiration (L3), Serenity (L5), Phoenix Rebirth (L8)
Include all mana costs, cooldowns, and effect data.
```

---

### CHUNK 2.3: Abilities API
**Priority**: HIGH | **Estimated Time**: 5-6 hours | **Dependencies**: CHUNK 2.2

#### Tasks:
1. Create ability service:
   - Get available abilities (unlocked + ready)
   - Check cooldown status
   - Use ability (apply effect)
   - Validate resources (mana/energy)

2. Implement ability effects:
   - `restore_hp` - Add HP
   - `restore_mana` - Add Mana
   - `gain_energy` - Add Energy
   - `xp_boost` - Multiplier for N tasks
   - `skip_daily` - Skip without HP loss
   - `auto_complete` - Complete task automatically
   - `protect_hp` - Prevent HP loss for duration

3. Create ability endpoints:
   - `GET /api/v1/abilities`
   - `GET /api/v1/abilities/available`
   - `POST /api/v1/abilities/{id}/use`

#### Success Criteria:
- [ ] Abilities unlock at correct levels
- [ ] Cooldowns are enforced
- [ ] Effects apply correctly to character
- [ ] Resources deducted properly

#### Agent Instruction:
```
Implement the Abilities API for QuestForge:
- Ability service with effect handlers
- Resource validation (mana, energy)
- Cooldown management
- All effect types implemented
- Ability use endpoint with response showing effect applied
```

---

### CHUNK 2.4: Rituals API
**Priority**: HIGH | **Estimated Time**: 4-5 hours | **Dependencies**: CHUNK 2.1

#### Tasks:
1. Create ritual service:
   - CRUD operations
   - Check ritual completion status
   - Grant bonus rewards
   - Update streak

2. Create ritual endpoints:
   - `GET /api/v1/rituals`
   - `POST /api/v1/rituals`
   - `GET /api/v1/rituals/today`
   - `POST /api/v1/rituals/{id}/complete`

3. Implement completion logic:
   - Check all tasks completed
   - Award bonus XP and Energy
   - Update streak counters

#### Success Criteria:
- [ ] Rituals can be created with task groups
- [ ] Today's rituals show completion status
- [ ] Bonus rewards granted on full completion
- [ ] Streaks tracked correctly

#### Agent Instruction:
```
Implement the Rituals API for QuestForge:
- Ritual CRUD operations
- Morning/Afternoon/Evening time slots
- Task group management
- Completion bonus logic (XP + Energy)
- Streak tracking (current + best)
```

---

### CHUNK 2.5: Frontend - Abilities UI
**Priority**: HIGH | **Estimated Time**: 5-6 hours | **Dependencies**: CHUNK 2.3, Phase 1 Frontend

#### Tasks:
1. Create abilities Redux slice

2. Create Abilities page:
   - Grid of ability cards
   - Class-specific theming
   - Locked/unlocked states
   - Cooldown indicators

3. Create AbilityCard component:
   - Icon and name
   - Mana/Energy cost display
   - Cooldown timer
   - Level requirement badge

4. Create AbilityModal component:
   - Ability description
   - Effect preview
   - Cast button
   - Confirmation for high-cost abilities

5. Add cast animations with Framer Motion

#### Success Criteria:
- [ ] Abilities display with correct states
- [ ] Cooldown timers count down
- [ ] Cast modal shows confirmation
- [ ] Effect animations play on use

#### Agent Instruction:
```
Implement the Abilities UI for QuestForge:
- Abilities grid page with class theming
- Ability cards showing cost, cooldown, level req
- Modal for casting with confirmation
- Cooldown timer component
- Cast animation effects
- Use Framer Motion for animations
```

---

### CHUNK 2.6: Frontend - Rituals UI
**Priority**: HIGH | **Estimated Time**: 4-5 hours | **Dependencies**: CHUNK 2.4, Phase 1 Frontend

#### Tasks:
1. Create rituals Redux slice

2. Create Rituals page:
   - Three ritual slots (Morning, Afternoon, Evening)
   - Progress indicators
   - Completion status

3. Create RitualCard component:
   - Time icon
   - Task list with checkmarks
   - Progress bar
   - Complete ritual button

4. Create ritual management (create/edit)

#### Success Criteria:
- [ ] Three ritual slots displayed
- [ ] Task completion updates ritual progress
- [ ] Bonus animation on full completion
- [ ] Streak displayed

#### Agent Instruction:
```
Implement the Rituals UI for QuestForge:
- Ritual cards for Morning, Afternoon, Evening
- Task checklist within each ritual
- Progress bar showing completion
- Bonus reward animation
- Ritual creation/editing modal
- Streak display
```

---

## Phase 3: Paths & Narrative (Weeks 6-7)

### CHUNK 3.1: Database Models - Paths & Narrative
**Priority**: MEDIUM | **Estimated Time**: 3-4 hours | **Dependencies**: Phase 2

#### Tasks:
1. Create SQLAlchemy models:
   - `Path` - path definition
   - `Milestone` - milestones within paths
   - `CharacterPath` - path progress per character
   - `MilestoneCompletion` - milestone completions
   - `NarrativeCard` - card templates
   - `CharacterCard` - delivered cards

2. Create Alembic migration

#### Success Criteria:
- [ ] Models created with relationships
- [ ] Migration applies successfully
- [ ] Path progression trackable

#### Agent Instruction:
```
Create database models for paths and narrative cards:
- Path with milestones relationship
- CharacterPath for tracking progress
- NarrativeCard templates with AI prompt fields
- CharacterCard for delivered personalized cards
Follow the SQL schema from the plan.
```

---

### CHUNK 3.2: Paths Seed Data
**Priority**: MEDIUM | **Estimated Time**: 3-4 hours | **Dependencies**: CHUNK 3.1

#### Tasks:
1. Create 3 complete paths:
   - "Disciplined Creator" (creativity theme)
   - "Health Warrior" (health/exercise theme)
   - "Productive Mage" (productivity theme)

2. Each path with 5-7 milestones:
   - Progressive difficulty
   - XP rewards
   - Narrative card triggers

3. Create base narrative cards for milestones

#### Success Criteria:
- [ ] 3 paths with all milestones seeded
- [ ] Narrative cards linked to milestones
- [ ] Progression structure complete

#### Agent Instruction:
```
Create seed data for paths and narrative cards:
- 3 paths: Disciplined Creator, Health Warrior, Productive Mage
- 5-7 milestones per path with escalating requirements
- Base narrative card templates for each milestone
- Welcome card template for new characters
- Level-up card templates
```

---

### CHUNK 3.3: Paths API
**Priority**: MEDIUM | **Estimated Time**: 4-5 hours | **Dependencies**: CHUNK 3.2

#### Tasks:
1. Create path service:
   - List available paths
   - Start path
   - Track progress
   - Complete milestones

2. Create path endpoints:
   - `GET /api/v1/paths`
   - `GET /api/v1/paths/{id}`
   - `POST /api/v1/paths/{id}/start`
   - `GET /api/v1/paths/current`
   - `POST /api/v1/paths/milestones/{id}/complete`

#### Success Criteria:
- [ ] Paths can be browsed and started
- [ ] Progress tracks correctly
- [ ] Milestones complete with rewards
- [ ] Path completion detected

#### Agent Instruction:
```
Implement the Paths API for QuestForge:
- Path listing with requirements (level, class)
- Start path functionality
- Progress tracking (tasks completed, days on path)
- Milestone completion with rewards
- Current path status endpoint
```

---

### CHUNK 3.4: Ollama Integration
**Priority**: MEDIUM | **Estimated Time**: 4-5 hours | **Dependencies**: Phase 1

#### Tasks:
1. Create Ollama client:
   - Async HTTP client for Ollama API
   - Chat completion endpoint
   - Configurable model and parameters

2. Create prompt templates:
   - System prompt for QuestForge narrator
   - Level-up template
   - Milestone template
   - Welcome template
   - Achievement template

3. Test generation quality

#### Success Criteria:
- [ ] Ollama client connects successfully
- [ ] Prompts generate appropriate content
- [ ] Response parsing works
- [ ] Error handling for timeouts

#### Agent Instruction:
```
Implement Ollama AI integration for QuestForge:
- Async HTTP client for Ollama API (localhost:11434)
- Model: llama3.3:70b (configurable)
- Prompt templates for narrative cards
- System prompt establishing narrator personality
- Temperature and token configuration
- Error handling and timeouts
```

---

### CHUNK 3.5: Narrative Service
**Priority**: MEDIUM | **Estimated Time**: 5-6 hours | **Dependencies**: CHUNK 3.4, CHUNK 3.1

#### Tasks:
1. Create narrative service:
   - Generate level-up cards
   - Generate milestone cards
   - Generate welcome cards
   - Generate achievement cards

2. Implement card delivery:
   - Save personalized content
   - Create CharacterCard records
   - Trigger notifications

3. Create event hooks:
   - On level up
   - On milestone complete
   - On character create
   - On achievement unlock

4. Create card endpoints:
   - `GET /api/v1/cards`
   - `GET /api/v1/cards/unread`
   - `PATCH /api/v1/cards/{id}/read`

#### Success Criteria:
- [ ] Cards generate on events
- [ ] Content is personalized
- [ ] Unread cards tracked
- [ ] Mark as read works

#### Agent Instruction:
```
Implement the Narrative Service for QuestForge:
- Card generation using Ollama with templates
- Context injection (level, class, streak, achievements)
- Event triggers (level_up, milestone, welcome)
- Card delivery and storage
- Unread tracking
- Endpoints for card management
```

---

### CHUNK 3.6: Frontend - Paths UI
**Priority**: MEDIUM | **Estimated Time**: 5-6 hours | **Dependencies**: CHUNK 3.3, Phase 2 Frontend

#### Tasks:
1. Create paths Redux slice

2. Create Paths page:
   - Available paths grid
   - Current path highlight
   - Completed paths section

3. Create PathCard component:
   - Theme icon and color
   - Description
   - Progress indicator
   - Start/Continue button

4. Create MilestoneTracker component:
   - Timeline view
   - Completed/current/upcoming milestones
   - Rewards preview

#### Success Criteria:
- [ ] Paths display with themes
- [ ] Start path flow works
- [ ] Progress visible on timeline
- [ ] Milestone completion triggers

#### Agent Instruction:
```
Implement the Paths UI for QuestForge:
- Paths list page with themed cards
- Path detail view with milestone timeline
- Progress tracking visualization
- Start path confirmation modal
- Milestone completion celebration
- Current path widget for dashboard
```

---

### CHUNK 3.7: Frontend - Narrative Cards UI
**Priority**: MEDIUM | **Estimated Time**: 4-5 hours | **Dependencies**: CHUNK 3.5, Phase 2 Frontend

#### Tasks:
1. Create narrative Redux slice

2. Create CardModal component:
   - Stylized card display
   - AI-generated content
   - Mark as read action
   - Close animation

3. Create CardList (inbox):
   - Unread indicator
   - Card previews
   - Read/unread filter

4. Implement card notifications:
   - New card badge in navbar
   - Auto-show on delivery

#### Success Criteria:
- [ ] Cards display beautifully
- [ ] New card notification shows
- [ ] Inbox lists all cards
- [ ] Mark as read works

#### Agent Instruction:
```
Implement the Narrative Cards UI for QuestForge:
- Card modal with styled presentation
- Card inbox/list view
- Unread notification badge
- Mark as read functionality
- Card type theming (level_up, milestone, welcome)
- Smooth animations for card display
```

---

## Phase 4: Dice Roller & Telegram (Week 8)

### CHUNK 4.1: Dice Roller Backend
**Priority**: MEDIUM | **Estimated Time**: 3-4 hours | **Dependencies**: Phase 1

#### Tasks:
1. Create dice service:
   - Filter eligible tasks
   - Create weighted pool
   - Determine dice type (d4-d20)
   - Perform random selection

2. Create dice endpoint:
   - `POST /api/v1/tasks/dice-roll`
   - Request: filters (type, difficulty, exclude)
   - Response: selected task, dice result, animation data

#### Success Criteria:
- [ ] Filtering works correctly
- [ ] Weights influence selection
- [ ] Dice type matches pool size
- [ ] Response includes animation data

#### Agent Instruction:
```
Implement the Dice Roller backend for QuestForge:
- Task filtering by type, difficulty, active status
- Weighted pool creation using task.dice_weight
- Dice type selection: d4 (≤4), d6 (≤6), d8 (≤8), d12 (≤12), d20 (>12)
- Random selection with roll result
- Response with animation metadata
```

---

### CHUNK 4.2: Dice Roller Frontend
**Priority**: MEDIUM | **Estimated Time**: 4-5 hours | **Dependencies**: CHUNK 4.1, Phase 1 Frontend

#### Tasks:
1. Create DiceRoller component:
   - Filter selection UI
   - Roll button
   - Animated dice roll
   - Result display

2. Create dice animation:
   - 3D dice rolling effect
   - Dice type visualization
   - Number reveal

3. Create result card:
   - Selected task display
   - Quick complete button
   - Roll again option

#### Success Criteria:
- [ ] Dice animation plays smoothly
- [ ] Correct dice type shown
- [ ] Result displays selected task
- [ ] Quick complete works

#### Agent Instruction:
```
Implement the Dice Roller UI for QuestForge:
- Filter selection (task type, difficulty)
- Animated dice roll using Framer Motion
- Dice type visualization (d4, d6, d8, d12, d20)
- Result card with selected task
- Quick complete action
- Roll again functionality
```

---

### CHUNK 4.3: Telegram Bot - Basic Setup
**Priority**: MEDIUM | **Estimated Time**: 4-5 hours | **Dependencies**: Phase 1

#### Tasks:
1. Create Telegram bot application:
   - python-telegram-bot 20.x setup
   - Command handlers
   - Callback handlers

2. Implement basic commands:
   - `/start` - Welcome message
   - `/link` - Account linking flow
   - `/status` - Character status

3. Create backend endpoints for Telegram:
   - `POST /api/v1/telegram/link`
   - `GET /api/v1/telegram/status/{chat_id}`

#### Success Criteria:
- [ ] Bot responds to commands
- [ ] Account linking works
- [ ] Status shows character info

#### Agent Instruction:
```
Implement basic Telegram bot for QuestForge:
- python-telegram-bot 20.x with async
- /start command with welcome
- /link command with code generation
- /status command showing character stats
- Backend endpoints for Telegram integration
- Account linking flow
```

---

### CHUNK 4.4: Telegram Bot - Advanced Features
**Priority**: LOW | **Estimated Time**: 4-5 hours | **Dependencies**: CHUNK 4.3

#### Tasks:
1. Add commands:
   - `/rituals` - Today's rituals
   - `/dice` - Roll dice for task

2. Implement inline buttons:
   - Task type selection for dice
   - Complete task button
   - Ritual completion

3. Create notification service:
   - Scheduled ritual reminders
   - Daily reset summary
   - Level up notifications

4. Setup Celery task for notifications

#### Success Criteria:
- [ ] Rituals command works
- [ ] Dice command with callbacks
- [ ] Task completion from Telegram
- [ ] Notifications send correctly

#### Agent Instruction:
```
Implement advanced Telegram features for QuestForge:
- /rituals command showing today's rituals
- /dice command with type selection buttons
- Complete task via callback buttons
- Notification service for reminders
- Daily reset summary notifications
- Level up and achievement notifications
```

---

## Phase 5: PWA & Polish (Week 9)

### CHUNK 5.1: PWA Setup
**Priority**: LOW | **Estimated Time**: 3-4 hours | **Dependencies**: Phase 1 Frontend

#### Tasks:
1. Configure Workbox service worker:
   - Cache static assets
   - Cache API responses (stale-while-revalidate)
   - Offline fallback page

2. Create manifest.json:
   - App name and icons
   - Theme colors
   - Display mode (standalone)

3. Add install prompt:
   - Detect installability
   - Show custom prompt
   - Track installation

#### Success Criteria:
- [ ] App installable on mobile
- [ ] Offline mode works
- [ ] Assets cached correctly

#### Agent Instruction:
```
Implement PWA features for QuestForge:
- Workbox service worker configuration
- Caching strategies for static and API
- Offline fallback page
- Manifest.json with icons
- Install prompt component
- Mobile-optimized meta tags
```

---

### CHUNK 5.2: Mobile UI Optimization
**Priority**: LOW | **Estimated Time**: 4-5 hours | **Dependencies**: All Frontend Chunks

#### Tasks:
1. Responsive audit:
   - Test all pages on mobile
   - Fix layout issues
   - Optimize touch targets

2. Create mobile navigation:
   - Bottom navigation bar
   - Mobile-friendly menus
   - Swipe gestures

3. Performance optimization:
   - Image lazy loading
   - Code splitting
   - Bundle size analysis

#### Success Criteria:
- [ ] All pages work on mobile
- [ ] Navigation is thumb-friendly
- [ ] Performance score > 90

#### Agent Instruction:
```
Optimize QuestForge for mobile:
- Responsive layout fixes
- Bottom navigation bar for mobile
- Touch-friendly controls (min 44px targets)
- Code splitting with React.lazy
- Image optimization
- Performance audit and fixes
```

---

## Phase 6: Testing & Documentation

### CHUNK 6.1: Backend Testing
**Priority**: MEDIUM | **Estimated Time**: 6-8 hours | **Dependencies**: All Backend Chunks

#### Tasks:
1. Setup pytest + pytest-asyncio

2. Write tests:
   - Authentication tests
   - Character CRUD tests
   - Task completion tests
   - Ability usage tests
   - Ritual completion tests

3. Create test fixtures

#### Success Criteria:
- [ ] 80%+ code coverage
- [ ] All critical paths tested
- [ ] Tests run in CI

#### Agent Instruction:
```
Write comprehensive backend tests for QuestForge:
- pytest + pytest-asyncio setup
- Test fixtures for users, characters, tasks
- Authentication flow tests
- Character operations tests
- Task completion with rewards tests
- Ability cooldown tests
- Ritual bonus tests
```

---

### CHUNK 6.2: Frontend Testing
**Priority**: LOW | **Estimated Time**: 5-6 hours | **Dependencies**: All Frontend Chunks

#### Tasks:
1. Setup Jest + React Testing Library

2. Write tests:
   - Component rendering tests
   - User interaction tests
   - Redux slice tests

3. Create E2E test suite (Playwright)

#### Success Criteria:
- [ ] Key components tested
- [ ] User flows covered
- [ ] E2E tests pass

#### Agent Instruction:
```
Write frontend tests for QuestForge:
- Jest + React Testing Library setup
- Component unit tests
- Redux slice tests
- User interaction tests
- Playwright E2E tests for critical flows
```

---

## Agent Delegation Summary

### Parallel Work Streams

The following work can be parallelized across multiple agents:

**Stream 1 (Backend Core):**
- CHUNK 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6 → 1.7

**Stream 2 (Frontend Core):** (Can start after CHUNK 1.1)
- CHUNK 1.8 → 1.9 → 1.10 → 1.11

**Stream 3 (Game Features):** (After Phase 1)
- CHUNK 2.1 → 2.2 → 2.3 → 2.5 (Abilities)
- CHUNK 2.1 → 2.4 → 2.6 (Rituals) - Can parallel with abilities

**Stream 4 (Narrative):** (After Phase 2)
- CHUNK 3.1 → 3.2 → 3.3 → 3.6 (Paths)
- CHUNK 3.4 → 3.5 → 3.7 (AI/Cards) - Can parallel after 3.1

**Stream 5 (Extras):** (Can run in parallel after Phase 1)
- CHUNK 4.1 → 4.2 (Dice Roller)
- CHUNK 4.3 → 4.4 (Telegram)
- CHUNK 5.1 → 5.2 (PWA)

### Agent Task Assignment Template

```
## Agent Task: [CHUNK ID] - [CHUNK NAME]

### Context
You are implementing a feature for QuestForge, an RPG-style habit tracker.

### Requirements
[Copy requirements from chunk]

### Success Criteria
[Copy criteria from chunk]

### Technical Constraints
- Backend: FastAPI 0.109+, SQLAlchemy 2.0 async, PostgreSQL 16
- Frontend: React 18, TypeScript, TailwindCSS, shadcn/ui, Redux Toolkit
- Follow existing code patterns and naming conventions
- Include proper error handling
- Write docstrings/comments for complex logic

### Deliverables
- [ ] Implementation code
- [ ] Any new dependencies listed
- [ ] Brief test instructions
```

---

## Quick Reference

### Priority Levels
- **CRITICAL**: Must be done first, blocks other work
- **HIGH**: Important for core functionality
- **MEDIUM**: Important features, can be deferred
- **LOW**: Nice to have, polish items

### Time Estimates
- Small chunk: 2-4 hours
- Medium chunk: 4-6 hours
- Large chunk: 6-8 hours

### Dependencies Legend
- "None" = Can start immediately
- "CHUNK X.X" = Must complete that chunk first
- "Phase X" = Must complete all chunks in that phase

---

*This task plan is designed to be used with Claude Code or similar AI coding assistants for systematic implementation of QuestForge.*
