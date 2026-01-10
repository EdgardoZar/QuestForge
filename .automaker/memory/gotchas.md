---
tags: [gotcha, mistake, edge-case, bug, warning]
summary: Mistakes and edge cases to avoid
relevantTo: [error, bug, fix, issue, problem]
importance: 0.9
relatedFiles: []
usageStats:
  loaded: 54
  referenced: 1
  successfulFeatures: 1
---
# Gotchas

Mistakes and edge cases to avoid. These are lessons learned from past issues.

---



#### [Gotcha] PostgreSQL enum requires explicit type casting in queries (2026-01-10)
- **Situation:** Database queries involving character class enum
- **Root cause:** Asyncpg driver requires explicit type conversion when working with PostgreSQL enums, leading to query failures if not handled
- **How to avoid:** Requires careful query writing but ensures type safety

#### [Gotcha] Host machine network access for Ollama integration in containers (2026-01-10)
- **Situation:** AI features requiring local model access from within Docker containers
- **Root cause:** Docker containers default to their own network isolation but need access to host's Ollama service
- **How to avoid:** Simpler setup using host network access but relies on host machine installation and proper network configuration

#### [Gotcha] Alembic async migration configuration complexity (2026-01-10)
- **Situation:** Database migrations need to work with async SQLAlchemy
- **Root cause:** Standard Alembic configuration assumes synchronous database operations, causing failures when using async FastAPI
- **How to avoid:** Required custom engine configuration and connection handling but enables database schema management