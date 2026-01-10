# Agent Task: Infrastructure Setup

## Task ID: CHUNK-1.1
## Priority: CRITICAL
## Estimated Time: 4-6 hours
## Dependencies: None

---

## Objective

Create the complete project infrastructure for QuestForge, an RPG-style habit tracking application.

---

## Context

QuestForge is a self-hosted webapp that combines habit tracking with RPG game mechanics. It uses:
- **Backend**: FastAPI + PostgreSQL + Redis + Celery
- **Frontend**: React + TypeScript + Vite
- **Additional Services**: Telegram Bot, Nginx reverse proxy
- **AI Integration**: Ollama for narrative generation (external)

---

## Deliverables

### 1. Project Directory Structure

Create the following directory structure:

```
questforge/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── alembic/
│   ├── tests/
│   ├── scripts/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── telegram-bot/
│   ├── bot.py
│   ├── handlers/
│   ├── requirements.txt
│   └── Dockerfile
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
├── Makefile
└── README.md
```

### 2. Docker Compose Configuration

Create `docker-compose.yml` with:

- **postgres**: PostgreSQL 16-alpine
  - Port: 5432
  - Health check configured
  - Volume for data persistence

- **redis**: Redis 7-alpine
  - Port: 6379
  - Health check configured

- **backend**: FastAPI application
  - Port: 8000
  - Depends on postgres, redis
  - Volume mount for development
  - Extra host for Ollama access

- **celery-worker**: Celery worker
  - Depends on redis, postgres
  - Same image as backend

- **celery-beat**: Celery beat scheduler
  - Depends on redis, postgres
  - Same image as backend

- **telegram-bot**: Telegram bot service
  - Port: 8001
  - Depends on backend

- **frontend**: React development server
  - Port: 5173
  - Volume mount for development

- **nginx**: Reverse proxy
  - Ports: 80, 443
  - Depends on backend, frontend

### 3. Environment Configuration

Create `.env.example`:

```env
# Database
POSTGRES_USER=questforge
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=questforge
DATABASE_URL=postgresql+asyncpg://questforge:your_password@postgres:5432/questforge

# Backend
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.3:70b

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Frontend
VITE_API_URL=http://localhost:8000/api/v1

# Timezone
TZ=America/Mexico_City
```

### 4. Makefile

Create `Makefile` with commands:

```makefile
.PHONY: help build up down logs clean migrate seed test shell

help:
	@echo "QuestForge Development Commands"
	@echo "================================"
	@echo "make build     - Build all containers"
	@echo "make up        - Start all services"
	@echo "make down      - Stop all services"
	@echo "make logs      - View logs (all services)"
	@echo "make logs-api  - View backend logs"
	@echo "make migrate   - Run database migrations"
	@echo "make seed      - Seed initial data"
	@echo "make test      - Run backend tests"
	@echo "make shell     - Open backend shell"
	@echo "make clean     - Remove all containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f backend

migrate:
	docker-compose exec backend alembic upgrade head

seed:
	docker-compose exec backend python scripts/seed_data.py

test:
	docker-compose exec backend pytest -v

shell:
	docker-compose exec backend /bin/bash

clean:
	docker-compose down -v --remove-orphans
```

### 5. Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:5173;
    }

    server {
        listen 80;
        server_name localhost;

        # Frontend (development)
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # API
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API Docs
        location /docs {
            proxy_pass http://backend/docs;
            proxy_set_header Host $host;
        }

        location /redoc {
            proxy_pass http://backend/redoc;
            proxy_set_header Host $host;
        }
    }
}
```

### 6. Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 7. Backend Requirements

Create `backend/requirements.txt`:

```
# FastAPI
fastapi==0.109.2
uvicorn[standard]==0.27.1
python-multipart==0.0.9

# Database
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
alembic==1.13.1
greenlet==3.0.3

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Validation
pydantic==2.6.1
pydantic-settings==2.1.0
email-validator==2.1.0

# Celery
celery==5.3.6
redis==5.0.1

# HTTP Client (for Ollama)
httpx==0.26.0

# Utilities
python-dateutil==2.8.2
pytz==2024.1

# Testing
pytest==8.0.0
pytest-asyncio==0.23.4
httpx==0.26.0

# Linting
ruff==0.2.1
```

### 8. Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 5173

# Default command
CMD ["npm", "run", "dev", "--", "--host"]
```

### 9. Telegram Bot Dockerfile

Create `telegram-bot/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

Create `telegram-bot/requirements.txt`:

```
python-telegram-bot==20.8
httpx==0.26.0
python-dotenv==1.0.1
```

### 10. Git Configuration

Create `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
ENV/
.eggs/
*.egg-info/

# Node
node_modules/
dist/
build/
.cache/

# Environment
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# Docker
*.log

# Database
*.db
*.sqlite3

# OS
.DS_Store
Thumbs.db

# Test
.coverage
htmlcov/
.pytest_cache/

# Build
*.egg
*.whl
```

---

## Success Criteria

- [ ] `docker-compose up` starts all services without errors
- [ ] PostgreSQL is accessible on port 5432
- [ ] Redis is accessible on port 6379
- [ ] Backend responds on http://localhost:8000/health (after backend setup)
- [ ] Frontend dev server runs on http://localhost:5173
- [ ] Nginx proxies requests correctly on port 80
- [ ] All Makefile commands work
- [ ] Environment variables load correctly

---

## Test Instructions

1. Copy `.env.example` to `.env`
2. Run `make build`
3. Run `make up`
4. Check `docker-compose ps` - all services should be "Up"
5. Run `make logs` to verify no errors

---

## Notes

- The backend won't fully work until AGENT_02 completes FastAPI setup
- Frontend won't build until AGENT_08 completes React setup
- Telegram bot is a placeholder until AGENT_15 implements it
- Ollama connection assumes it's running on the host machine
