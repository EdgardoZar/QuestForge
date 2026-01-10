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