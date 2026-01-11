---
tags: [api]
summary: api implementation decisions and patterns
relevantTo: [api]
importance: 0.7
relatedFiles: []
usageStats:
  loaded: 2
  referenced: 2
  successfulFeatures: 2
---
# api

#### [Pattern] Separate service layer for business logic between API endpoints and database models (2026-01-10)
- **Problem solved:** Character CRUD operations and stats management
- **Why this works:** Creates a clear separation of concerns, making the code more maintainable and testable
- **Trade-offs:** Increased code complexity but made business logic reusable and easier to test

#### [Gotcha] Type aliases for dependencies (DBSession, CurrentUser) are critical for maintainability (2026-01-10)
- **Situation:** API dependencies initially returned concrete types, causing coupling
- **Root cause:** Type aliases allow changing underlying implementation without breaking endpoint signatures
- **How to avoid:** Slightly more boilerplate code upfront, but massive long-term maintainability benefits

#### [Pattern] Separated API endpoints for different task types (dailies vs todos vs habits) (2026-01-10)
- **Problem solved:** Task system with different behaviors and completion mechanics
- **Why this works:** Reduces API complexity and provides type-specific optimizations; allows different validation rules per type
- **Trade-offs:** Cleaner API structure but requires more endpoint management; prevents cross-type contamination

#### [Gotcha] Auto token refresh on 401 doesn't account for concurrent requests (2026-01-11)
- **Situation:** Multiple API calls receiving 401 simultaneously
- **Root cause:** Token refresh mechanism needs to deduplicate refresh attempts and prevent race conditions
- **How to avoid:** Added complexity to manage refresh token queue vs risk of failed requests during token refresh

#### [Pattern] Centralized Axios service with token refresh interceptors (2026-01-11)
- **Problem solved:** Authentication token management across multiple API calls
- **Why this works:** Automatic token renewal without requiring each component to handle auth refresh
- **Trade-offs:** Simplified API calls but creates dependency on centralized service

#### [Pattern] Centralized API client with interceptors (2026-01-11)
- **Problem solved:** Backend integration setup
- **Why this works:** Provides consistent error handling, authentication, and request/response transformations
- **Trade-offs:** Single source of truth for API communication makes debugging easier but requires careful intercept management