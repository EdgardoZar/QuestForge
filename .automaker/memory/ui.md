---
tags: [ui]
summary: ui implementation decisions and patterns
relevantTo: [ui]
importance: 0.7
relatedFiles: []
usageStats:
  loaded: 0
  referenced: 0
  successfulFeatures: 0
---
# ui

### Redux Toolkit for state management instead of React Context or MobX (2026-01-10)
- **Context:** Complex frontend with multiple interconnected features (auth, character, tasks)
- **Why:** Provides predictable state updates with middleware support; integrates well with TypeScript and Redux DevTools
- **Rejected:** React Context (insufficient for complex state) or MobX (steeper learning curve)
- **Trade-offs:** More boilerplate but better debugging and time-travel capabilities; easier to maintain complex state hierarchies
- **Breaking if changed:** Changing state management would require complete rewrite of all component interactions

### Radix UI primitives over custom components despite learning curve (2026-01-11)
- **Context:** Accessibility-first component library selection
- **Why:** Radix provides WAI-ARIA compliant primitives without the accessibility overhead of building from scratch
- **Rejected:** Building custom components would be faster but would require extensive accessibility work
- **Trade-offs:** More complex styling setup (CVA + clsx + tailwind-merge) vs guaranteed accessibility and keyboard navigation
- **Breaking if changed:** Removing Radix would require rebuilding accessibility layer (keyboard nav, focus management, ARIA attributes) for all components

#### [Pattern] Component composition with ProtectedRoute and AppLayout wrappers (2026-01-11)
- **Problem solved:** Authentication and layout consistency across pages
- **Why this works:** Reusable route protection and layout structure prevents duplication and ensures consistent sidebar/auth state
- **Trade-offs:** Cleaner code but requires careful provider ordering in App.tsx

### Implemented inline stats bars instead of separate components (2026-01-11)
- **Context:** Character stats display in dashboard
- **Why:** Kept stats bars as inline elements within the CharacterCard component for better visual cohesion and to avoid unnecessary component nesting
- **Rejected:** Creating separate StatsBar components would have led to too many small components and visual fragmentation
- **Trade-offs:** Reduced component reusability but improved visual cohesion and performance
- **Breaking if changed:** Moving stats bars to separate components would break the current visual design and require restructuring the CharacterCard layout

#### [Gotcha] Framer Motion animations caused layout thrashing during fast state updates (2026-01-11)
- **Situation:** Animated stats bars during character updates
- **Root cause:** Rapid state changes combined with continuous animation requests led to performance issues
- **How to avoid:** Animations provide visual feedback but can impact performance

#### [Gotcha] Class gradient theming created visual inconsistencies (2026-01-11)
- **Situation:** Different color schemes for character classes
- **Root cause:** Using different gradient intensities (950 to 900) across classes made them look unbalanced
- **How to avoid:** Visual distinction achieved but required additional fine-tuning