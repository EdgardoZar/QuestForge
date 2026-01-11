---
tags: [database]
summary: database implementation decisions and patterns
relevantTo: [database]
importance: 0.7
relatedFiles: []
usageStats:
  loaded: 1
  referenced: 1
  successfulFeatures: 1
---
# database

### Used PostgreSQL ENUM types instead of SQLAlchemy Enum for task types, difficulties, and ritual times (2026-01-10)
- **Context:** Needed database-enforced constraints for task categorization system
- **Why:** PostgreSQL ENUM provides database-level validation and prevents invalid enum values, ensuring data consistency at the database layer rather than relying only on application-level validation
- **Rejected:** SQLAlchemy Enum class with constraint validation
- **Trade-offs:** Easier database validation and consistency but requires manual DDL management in migrations
- **Breaking if changed:** Changing to SQLAlchemy Enum would require removing database constraints and relying on application validation only

### Implemented automatic level-up system using PostgreSQL triggers instead of application logic (2026-01-10)
- **Context:** RPG character progression system needs to be atomic and consistent with database state
- **Why:** PostgreSQL triggers ensure level progression happens atomically with data updates, preventing race conditions and ensuring consistent state even if multiple processes are updating character data
- **Rejected:** Application-level service methods for character progression
- **Trade-offs:** More complex migration setup but provides better data consistency and performance
- **Breaking if changed:** Removing triggers would require implementing complex application logic with race condition handling and transaction management

#### [Gotcha] Alembic migrations require explicit ENUM creation in DDL, not just model definitions (2026-01-10)
- **Situation:** Initial migration failed because SQLAlchemy Enum doesn't automatically create database ENUM types
- **Root cause:** Alembic only generates DDL for SQLAlchemy constructs that map directly to SQL. PostgreSQL ENUM types require explicit op.create_table() calls with _column_kwargs
- **How to avoid:** Required more verbose migration code but provides proper database type support

#### [Pattern] Used check constraints for character resource validation instead of application logic (2026-01-10)
- **Problem solved:** Need to ensure character stats stay within reasonable ranges (health/mana between 0 and max, level positive, etc.)
- **Why this works:** Database constraints provide immediate validation regardless of application layer, preventing corrupt data even if application logic has bugs
- **Trade-offs:** Harder to change validation rules dynamically but provides stronger data integrity guarantees

### Implemented daily stats aggregation using PostgreSQL triggers instead of nightly batch jobs (2026-01-10)
- **Context:** Need to track daily character progress metrics for the habit tracking system
- **Why:** Triggers provide real-time statistics and eliminate the need for scheduled jobs, ensuring stats are always up-to-date without external dependencies
- **Rejected:** Cron job or background task that runs nightly to aggregate stats
- **Trade-offs:** More complex database setup but eliminates scheduling dependencies and provides real-time analytics
- **Breaking if changed:** Would lose real-time stats tracking and require implementing complex job scheduling

### Used PostgreSQL enum for character classes instead of string validation (2026-01-10)
- **Context:** Character class validation and database integrity
- **Why:** PostgreSQL enums provide built-in type safety and database constraints, preventing invalid values from being stored at the database level
- **Rejected:** String validation with Pydantic enum - rejected because it only works at application level and invalid data could still be stored directly to database
- **Trade-offs:** Gained database-level validation but lost flexibility for runtime class additions without schema migration
- **Breaking if changed:** Would require database migration if new classes need to be added

### Separate Alembic migration script from application models (2026-01-10)
- **Context:** Database schema evolution and migration management in a FastAPI application
- **Why:** Ensures proper migration workflow, separates concerns, and provides a clear pattern for database changes across development teams
- **Rejected:** Migrations embedded directly in application code or database-first approach
- **Trade-offs:** Additional file structure complexity but provides better version control and migration management
- **Breaking if changed:** Database schema changes would become error-prone and team coordination would be difficult without the migration setup

#### [Gotcha] Async SQLAlchemy engine vs connection configuration complexity (2026-01-10)
- **Situation:** Database connection setup for async operations
- **Root cause:** Initial attempts failed due to synchronous connection patterns not working with async FastAPI
- **How to avoid:** Required additional configuration complexity but enables proper async database operations

#### [Pattern] Streak bonus calculation centralized in service layer with configurable maximum (2026-01-10)
- **Problem solved:** XP/gold rewards needed to encourage consistent user engagement
- **Why this works:** Centralized calculation ensures consistency across all task completion paths and allows easy adjustment of reward mechanics
- **Trade-offs:** Business logic in service layer vs pure data access pattern, but necessary for reward system consistency

### PostgreSQL with automatic level-up triggers instead of application-level logic (2026-01-10)
- **Context:** Character progression system requiring XP calculation and level thresholds
- **Why:** Ensures data consistency and prevents race conditions; database enforces rules without application coordination
- **Rejected:** Application-level level-up checks in API endpoints
- **Trade-offs:** More complex database setup but simpler application logic; ensures consistency even if multiple instances run
- **Breaking if changed:** Removing PostgreSQL would require complete rewrite of progression logic

#### [Pattern] Separate database session management from Celery configuration (2026-01-11)
- **Problem solved:** Need to handle database connections in Celery workers reliably
- **Why this works:** Workers may be restarted frequently, creating new sessions each time prevents connection leaks
- **Trade-offs:** More boilerplate code vs better resource management and reliability

#### [Gotcha] Character stats updates require transactional consistency (2026-01-11)
- **Situation:** Task completion updates both task status and character stats
- **Root cause:** Race conditions could occur if multiple tasks complete simultaneously, updating stats inconsistently
- **How to avoid:** Added backend complexity for atomic operations vs data consistency integrity