---
tags: [performance]
summary: performance implementation decisions and patterns
relevantTo: [performance]
importance: 0.7
relatedFiles: []
usageStats:
  loaded: 0
  referenced: 0
  successfulFeatures: 0
---
# performance

#### [Pattern] Filter endpoints with efficient database queries instead of client-side filtering (2026-01-10)
- **Problem solved:** Task list could become very large with many tasks, categories, and statuses
- **Why this works:** Database filtering ensures efficient querying with proper indexing and reduces data transfer
- **Trade-offs:** More complex endpoint signatures vs significantly better performance with large datasets

#### [Gotcha] Daily reset system requires Celery instead of simple cron due to distributed system requirements (2026-01-10)
- **Situation:** Multi-instance backend needing synchronized daily resets
- **Root cause:** Single process-based solutions won't work with multiple backend instances; Redis-based task queue provides coordination
- **How to avoid:** Adds infrastructure complexity but ensures consistency across all instances; handles instance failures gracefully

#### [Pattern] Optimistic updates with mutation rollback (2026-01-11)
- **Problem solved:** Task completion API calls that might fail
- **Why this works:** Prevents UI jank by showing immediate feedback while handling server errors gracefully
- **Trade-offs:** Increased complexity of mutation tracking vs better perceived performance