---
name: Use formal plan mode for all non-trivial work
description: Explicit plan mode produces far better results than informal planning + review agent; always use it
type: feedback
scope: global
---

Always use explicit plan mode (thorough design document) for non-trivial work. Do NOT shortcut with informal descriptions sent to review agents.

**Why:** Kyle observed a clear quality regression when switching from formal plan mode to informal planning. The informal flow (quick description → review agent → dev agent) produces fragile, half-baked implementations that seem to work but break quickly. The review agent rubber-stamps shallow specs instead of catching design gaps. A full day was wasted on 2026-03-26 reworking broken implementations.

**How to apply:**
1. For any non-trivial feature or fix, enter plan mode and write a thorough design BEFORE sending to any agent
2. The plan must enumerate all affected code paths, event types, edge cases — not just the happy path
3. Don't rely on the review agent to catch what the plan missed — the plan IS the quality gate
4. Only skip formal planning for true one-liner bug fixes where the change is obvious
5. When Kyle discusses something informally, that's discovery — translate it into a formal plan before moving to development
