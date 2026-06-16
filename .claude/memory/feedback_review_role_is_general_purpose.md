---
name: The 'review' ephemeral role is general-purpose — use it for any non-dev/non-test work
description: review-role ephemeral agents are fine for plan review, implementation research, audits, investigations, analysis — anything that isn't writing product code (dev) or running Playwright tests (test).
type: feedback
scope: global
---

The three ephemeral roles are `dev`, `review`, and `test`. Think of them as:
- **dev** — writes product code, makes commits
- **test** — runs Playwright against a live dev server, screenshots, visual/functional validation
- **review** — EVERYTHING ELSE. Code review IS the canonical use case, but the role is general-purpose. Use it freely for plan review, API research, architecture investigation, codebase audits, library research, spec work, design docs, or any analytical/read-heavy task that doesn't fit dev or test.

**Why:** Kyle clarified on 2026-04-11 after I hesitated about spawning a review agent for a plan-review+research task. "yes review is sort of generic we can use it for most any other functions just not dev and test". Don't create bespoke roles for planning / research / audit — just spawn a review agent and brief it clearly in the initial message.

**How to apply:**
- Need someone to read a plan and refine its checklist? Spawn review, brief the task.
- Need someone to research an unfamiliar library API before dev starts? Spawn review, brief the task.
- Need someone to audit the codebase for a pattern or anti-pattern? Spawn review.
- Need someone to investigate a bug without fixing it? Spawn review.
- The briefing message is where you tell the agent what to actually do. The role is the permission/tool bundle, not the job description.

Only escalate to a custom role folder if you genuinely need different permissions than review has — and that's rare.
