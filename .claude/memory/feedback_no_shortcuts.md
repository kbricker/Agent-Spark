---
name: No shortcuts — build it right the first time
description: Kyle's direct feedback that Hive platform quality is poor because of shortcuts and sloppy architecture, creating endless maintenance that steals time from game development
type: feedback
scope: global
---

Stop taking shortcuts. The Hive dashboard and platform have recurring quality problems because things were built sloppily: single 3000-line JS file with duplicate functions, stale compressed static assets in the deploy pipeline, rogue services nobody asked for (PlanOrchestrationService), wrong field types in specs. Every shortcut becomes a maintenance burden that pulls Kyle away from VaEx game development.

**Why:** Kyle has spent weeks fixing Hive infrastructure instead of building the game. The platform exists to support game development — every hour spent debugging bad platform code is an hour not spent on VaEx.

**How to apply:**
- Use proper architecture from the start (modules, linting, structure) even for "simple" features
- Don't ship "good enough for now" code — it becomes permanent
- Don't add features or services that weren't requested (like PlanOrchestrationService auto-assignment)
- Verify deploys actually work end-to-end before declaring done
- When building dashboard features, use ES modules and proper JS structure
- Test rendering output, don't just verify the server returns the right data

**Boundary — "right" is not "over-built":** building it right means correct, clean, and properly structured. It does NOT mean elaborate. Write the minimum code that actually solves today's problem — no speculative abstractions for single-use code, no flexibility / configurability / extra options nobody asked for, no error handling for impossible scenarios. Gold-plating is its own kind of shortcut: it's avoiding the discipline of solving exactly the stated problem. If 200 lines could be 50, rewrite it; if a senior engineer would call it overcomplicated, simplify. Proper structure and minimalism are the same goal, not opposites.
