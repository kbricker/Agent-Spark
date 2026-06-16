---
name: Fast-track is the default workflow
description: Fast-track is the main orchestrator path now; ephemeral run-plan-workflow is the escape hatch, not the entry point. Applies to overwatch, verletDev, vaexdev.
type: feedback
scope: global
---

Fast-track is the default orchestration path for all plans across overwatch, verletDev, and vaexdev. The orchestrator plays dev + review inline and is free to spawn Agent/Task subagents at its discretion for fan-out (parallel dev on independent sub-areas), leveraging the shared prompt cache. Ephemeral dev/review/test via `run-plan-workflow` is the **escape hatch** for large, risky, architecturally-unknown, or multi-agent-coordination work — not the default.

**Why:** Kyle set this rule on 2026-04-19 during an orchestrator-comparison discussion. Reasoning: spawning ephemerals has real startup cost, breaks cache sharing, and for the size of most plans is overkill. Fast-track + fan-out via subagents keeps cache warm, parallelizes where useful, and shaves the spawn/clone/kill cycle entirely. This reverses the prior default where run-plan-workflow was the expected path and fast-track required explicit authorization.

**How to apply:**
- On a new plan, default to fast-track (invoke `fast-track-plan` skill).
- Use Agent/Task subagents for parallelizable sub-work — independent files, parallel research, multi-file reviews.
- Only reach for `run-plan-workflow` when the change is genuinely large (broad scope, many files, architectural risk) or when real dev/review/test agent isolation is needed (long-running Playwright tests, destructive experiments, multi-day plans).
- If unsure, propose fast-track and ask Kyle only if the scope feels genuinely heavy.
- Do NOT ask for fast-track authorization on every small plan — that inverts back to the old model.

**Note:** Plan #A (to be filed) formalizes this in the fast-track-plan skill and rolls out to all three orchestrators. Until that ships, follow this memory as the operative rule.
