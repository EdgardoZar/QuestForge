---
tags: [auth]
summary: auth implementation decisions and patterns
relevantTo: [auth]
importance: 0.7
relatedFiles: []
usageStats:
  loaded: 0
  referenced: 0
  successfulFeatures: 0
---
# auth

#### [Pattern] JWT token validation via dependency function instead of middleware (2026-01-10)
- **Problem solved:** Authentication for protected endpoints
- **Why this works:** FastAPI's dependency system provides cleaner separation and automatic error handling compared to custom middleware
- **Trade-offs:** Simpler implementation but less flexible for complex authentication scenarios

#### [Gotcha] Placeholder authentication (501 error) prevents full API testing (2026-01-10)
- **Situation:** Task completion returns user/character data for reward distribution
- **Root cause:** Authentication is essential for identifying which user completed which task and updating their character stats
- **How to avoid:** Delayed full API testing capability vs maintaining security from the start