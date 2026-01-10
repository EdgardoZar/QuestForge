---
tags: [api]
summary: api implementation decisions and patterns
relevantTo: [api]
importance: 0.7
relatedFiles: []
usageStats:
  loaded: 0
  referenced: 0
  successfulFeatures: 0
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