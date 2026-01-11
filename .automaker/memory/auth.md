---
tags: [auth]
summary: auth implementation decisions and patterns
relevantTo: [auth]
importance: 0.7
relatedFiles: []
usageStats:
  loaded: 2
  referenced: 2
  successfulFeatures: 2
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

#### [Gotcha] JWT token refresh cycle creates complex frontend state management (2026-01-10)
- **Situation:** Long-running sessions requiring token refresh without forcing re-authentication
- **Root cause:** Discovered during implementation that token refresh timing creates race conditions between API calls and token expiration
- **How to avoid:** Better UX but requires sophisticated token refresh logic; API calls must handle concurrent token refresh

#### [Gotcha] Authentication assumption broke development workflow (2026-01-11)
- **Situation:** No authentication pages implemented
- **Root cause:** Assuming localStorage tokens would work without proper auth flow led to development bottlenecks
- **How to avoid:** Faster initial development but created technical debt