---
name: Always plan before building
description: Always research and write a formal plan before building — never skip to code, never shortcut a shallow spec to a review agent
type: feedback
scope: global
---

ALWAYS research and write a formal plan before implementation. Research first, plan second, build third — never skip straight to code on a new feature or non-trivial change.

**Formal, not informal.** Use explicit plan mode (a thorough design document) for non-trivial work — do NOT shortcut with a quick description handed to a review agent. The plan itself is the quality gate; the reviewer is not there to catch what a shallow spec missed. The plan enumerates all affected code paths, event types, and edge cases — not just the happy path.

**Why:** Kyle corrected jumping straight to code on the Hive Channel feature — the plan system exists for alignment, progress tracking, and cross-agent visibility. And a clear quality regression followed switching from formal plan mode to informal planning: the informal flow (quick description → review agent → dev agent) produced fragile, half-baked implementations that seemed to work but broke quickly, costing a full day of rework (2026-03-26).

**How to apply:**
1. Research the problem — docs, existing code, constraints.
2. Write a formal plan in the Hive plan system (`hive_plan_create`) with a concrete checklist and the affected paths/edge cases enumerated.
3. Get Kyle's alignment when scope is non-trivial.
4. THEN build, checking items off as you go.
5. Only skip formal planning for a true one-line obvious fix. When Kyle discusses something informally, that's discovery — translate it into a formal plan before development.
