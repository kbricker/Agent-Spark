---
name: Fast-track is the default workflow
description: Working a plan? Fast-track: dev + review inline, fan out to subagents, no other pipeline. Governs plans, not asks
type: feedback
scope: global
---

Fast-track is the orchestration path for all plans, on every agent. You play dev + review inline and are free to spawn Agent/Task subagents at your discretion for fan-out (parallel dev on independent sub-areas), leveraging the shared prompt cache. **There is no second path.** Work too large for one context gets decomposed across subagents, not handed to a different pipeline.

It governs work that *is* a plan. It does not turn every request into one: whether a plan exists is decided by `feedback_always_plan` — the plan appears at the action gate (PR, merge, shared push, propagate, deploy) or on plan / ship, not before, and a test / sample / quick / try ask gets the thing itself with one check that it runs. Never open a plan in order to have somewhere to run this procedure.

**Why:** Kyle set this rule on 2026-04-19 during an orchestrator-comparison discussion. Reasoning: spawning a separate agent process has real startup cost, breaks cache sharing, and for the size of most plans is overkill. Fast-track + fan-out via subagents keeps the cache warm, parallelises where useful, and shaves the spawn/clone/kill cycle entirely. The separate-process pipeline it replaced was retired outright on 2026-08-16. The plan-only scope was added 2026-09-11 (plan 1027) after a quick test ask was walked through the full procedure.

**How to apply:**
- On a new plan, default to fast-track (invoke `fast-track-plan` skill).
- No plan, no fast-track: a quick ask gets the thing itself and the least-work rule's single verification.
- Use Agent/Task subagents for parallelizable sub-work — independent files, parallel research, multi-file reviews.
- When a plan is too large for one context, DECOMPOSE it across subagents by sub-area. There is nowhere else to send it.
- When work genuinely needs a second independent session — Kyle asking for a review that is not your own, or a project you do not own — that is a handoff to another NAMED agent taking a ticket of its own, and the first thing you tell it is to check out the right branch. It is not a spawn.
- Do NOT ask for fast-track authorization on every small plan — that inverts back to the old model.

The `fast-track-plan` skill holds the operative procedure; this memory is the rule and the why behind it.
