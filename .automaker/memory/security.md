---
tags: [security]
summary: security implementation decisions and patterns
relevantTo: [security]
importance: 0.7
relatedFiles: []
usageStats:
  loaded: 0
  referenced: 0
  successfulFeatures: 0
---
# security

### Nginx reverse proxy for all services with environment-based configuration (2026-01-10)
- **Context:** Need for proper routing, SSL termination, and CORS management in a multi-container application
- **Why:** Centralized routing and security management, HTTPS termination at proxy level, and consistent port exposure (80/443) regardless of internal service ports
- **Rejected:** Direct service access or application-level routing
- **Trade-offs:** Additional layer of complexity but provides security, routing, and production-readiness benefits
- **Breaking if changed:** Security vulnerabilities and production deployment issues without proper proxy configuration