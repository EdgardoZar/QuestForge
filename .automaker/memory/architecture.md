---
tags: [architecture]
summary: architecture implementation decisions and patterns
relevantTo: [architecture]
importance: 0.7
relatedFiles: []
usageStats:
  loaded: 1
  referenced: 1
  successfulFeatures: 1
---
# architecture

#### [Pattern] Separated game mechanics (level progression, stats tracking) into database triggers instead of service layer (2026-01-10)
- **Problem solved:** RPG habit tracker needs consistent game mechanics that work regardless of how data is accessed
- **Why this works:** Database triggers ensure game mechanics are enforced consistently across all data access methods, preventing logic duplication and ensuring consistent behavior
- **Trade-offs:** More complex database schema but provides consistency and reduces application logic complexity

### Used dependency injection for database sessions instead of global session (2026-01-10)
- **Context:** Database session management in FastAPI
- **Why:** Dependency injection provides better resource management, prevents connection leaks, and allows for easier testing with mocks
- **Rejected:** Global database session - rejected because it would cause connection leaks in concurrent requests and make testing difficult
- **Trade-offs:** More boilerplate code but better resource management and testability
- **Breaking if changed:** Removing dependency injection would require manual session management and break the current API structure

### Separated development and production Docker Compose configurations (2026-01-10)
- **Context:** Need for different configurations between development and production environments
- **Why:** Development requires hot reload, volume mounts, and debug features while production needs security hardening and optimized resource usage
- **Rejected:** Single docker-compose.yml with environment variables for configuration differences
- **Trade-offs:** More configuration files to maintain but cleaner separation of concerns and environment-specific optimizations
- **Breaking if changed:** Any production deployment would break security and performance requirements without the dedicated prod configuration

#### [Pattern] Makefile abstraction for Docker operations (2026-01-10)
- **Problem solved:** Need for consistent and repeatable build/deploy operations across team members
- **Why this works:** Abstracts Docker Compose complexity, provides standardized commands, and handles environment-specific operations with a single interface
- **Trade-offs:** Learning curve for Makefile syntax but provides maintainability and consistency benefits

### Separation of API versions with router structure (2026-01-10)
- **Context:** API versioning strategy for multi-version endpoint management
- **Why:** Router isolation enables independent version maintenance and backward compatibility without breaking existing client integrations
- **Rejected:** Single router with version path parameters - harder to maintain version-specific middleware and documentation
- **Trade-offs:** Slightly more boilerplate code but cleaner version separation and easier future version migration
- **Breaking if changed:** Version-specific API changes won't break other versions; new API versions can be added without affecting existing ones

#### [Pattern] Pydantic Settings for environment configuration (2026-01-10)
- **Problem solved:** Configuration management with environment variable validation
- **Why this works:** Type-safe configuration with automatic validation and required field enforcement prevents runtime configuration errors
- **Trade-offs:** Increased startup validation but eliminates common configuration-related runtime bugs

#### [Pattern] Lifespan events for async resource management (2026-01-10)
- **Problem solved:** Application startup and shutdown sequence
- **Why this works:** FastAPI lifespan events provide proper async resource initialization and cleanup, ensuring database connections are properly established and released
- **Trade-offs:** Slightly more complex setup but guarantees proper resource management and prevents connection leaks

### Separated task completion from deletion to allow undo functionality (2026-01-10)
- **Context:** Task deletion was initially considered the primary way to handle task completion
- **Why:** Users frequently complete tasks accidentally or change their mind, and allowing same-day undo (via uncomplete endpoint) significantly improves user experience
- **Rejected:** Standard REST approach would use DELETE for completion, but this breaks UX for task management apps
- **Trade-offs:** Added complexity to service layer (separate complete/uncomplete methods vs single delete operation) but greatly improved usability
- **Breaking if changed:** If changed to standard DELETE, users lose ability to undo completions, causing frustration and requiring additional UI workarounds

### Chunked development approach with explicit dependency ordering (2026-01-10)
- **Context:** Large gamification platform with complex dependencies between authentication, characters, tasks, and daily systems
- **Why:** Prevents circular dependencies and allows incremental testing; each chunk can be validated independently
- **Rejected:** Monolithic development or random feature order
- **Trade-offs:** Requires careful planning overhead but reduces integration complexity
- **Breaking if changed:** Breaking any chunk dependency order would create broken API contracts

### Separate Celery worker and beat processes with dedicated entry points (2026-01-11)
- **Context:** Initial approach considered running worker and beat in same process, but this creates coupling issues
- **Why:** Separate processes allow independent scaling, monitoring, and lifecycle management
- **Rejected:** Single process approach would make it impossible to scale workers independently of beat scheduler
- **Trade-offs:** More complex orchestration vs better reliability and scalability
- **Breaking if changed:** Changes to worker lifecycle would affect beat scheduling if combined

### Containerized entire Celery stack with Flower monitoring (2026-01-11)
- **Context:** Initial approach considered running Redis and Celery locally
- **Why:** Docker provides consistent environment, resource isolation, and easy monitoring via Flower
- **Rejected:** Local deployment would create environment inconsistencies and monitoring complexity
- **Trade-offs:** Deployment complexity vs reproducibility and production readiness
- **Breaking if changed:** Removing Docker would break monitoring and require manual service coordination

### Redux Toolkit + React Query hybrid approach instead of React Query only (2026-01-11)
- **Context:** Managing both cached API data and local application state (filters, UI state)
- **Why:** React Query for server state caching/optimistic updates, Redux Toolkit for complex local state (filters, form state) and derived state
- **Rejected:** Using React Query for everything would struggle with complex local state management and derived calculations
- **Trade-offs:** Increased complexity for state management setup vs better separation of concerns and maintainability
- **Breaking if changed:** Removing Redux would require migrating filter state, form state, and complex UI logic to React Query, risking performance issues on complex state updates

#### [Gotcha] Mock character data structure mismatch with API contract (2026-01-11)
- **Situation:** Frontend built with static mock data before API spec finalization
- **Root cause:** Developers assumed character model structure, leading to potential interface mismatches
- **How to avoid:** Faster development vs risk of breaking changes when API contract is finalized

### Dual state management with Redux Toolkit + React Query (2026-01-11)
- **Context:** Client-side state vs server state management
- **Why:** Redux for persistent UI/auth state, React Query for server/cached data with automatic refetching and stale-while-revalidate
- **Rejected:** Using only Redux for everything (would require manual caching/refetch logic)
- **Trade-offs:** Easier server data handling but adds complexity with two state systems
- **Breaking if changed:** Tasks would lose automatic refetching and caching capabilities

#### [Pattern] Multi-stage Docker build with nginx for production (2026-01-11)
- **Problem solved:** Optimized container image size and serving performance
- **Why this works:** Separate build and production stages reduce final image size and serve static files efficiently
- **Trade-offs:** Smaller production images but more complex Docker configuration

### Used Redux Toolkit with async thunks instead of local state (2026-01-11)
- **Context:** Character data management across multiple pages
- **Why:** Ensures consistent state management across components and provides proper loading/error states
- **Rejected:** Local useState would have led to prop drilling and inconsistent state management across the app
- **Trade-offs:** More complex setup but better maintainability and predictable state
- **Breaking if changed:** Switching to local state would break the current data flow and require significant refactoring of component connections