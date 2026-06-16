---
name: HOLD / stand-down messages must explicitly forbid plan metadata edits too
description: When telling a dev agent to stand down, "don't write code" is NOT sufficient — they will still edit plan checklists/descriptions if they think they're applying a review. Name every forbidden surface explicitly.
type: feedback
scope: global
---

When pausing a dev agent mid-flight, do NOT say "don't write any code" as your only restriction. Dev agents interpret that literally: no file edits, no commits, no branch work — but **plan metadata edits via MCP (checklist items, descriptions, status) are NOT code** and they will happily proceed.

**Why:** on 2026-04-15, a misrouted review report landed in `dev-plan187`'s inbox. I sent "HOLD — do not write any code" and dev stood down on files but then went ahead and deleted 5 checklist items on plan #187 (4 of which were meant as refinements, not removals). The HOLD succeeded for its literal scope and failed for its intent. I had to reconstruct the items.

**How to apply:** every stand-down message to a dev agent must explicitly enumerate forbidden actions. Minimum set:

> HOLD — stand down immediately. Do NOT:
> - edit any files (code, configs, docs, anything)
> - make commits or touch git state
> - edit the plan checklist, description, or status via MCP (hive_plan_* tools)
> - add, refine, remove, or check off checklist items
> - send messages to other agents
>
> Reply with "standing down" to confirm and stay idle until you receive explicit new instructions from {your orchestrator key}.

The same principle applies to review and test agents, adapted to their surfaces — review's stand-down should also forbid plan checklist edits since review is often in the "propose changes" role.

**Broader principle:** when an agent takes initiative you didn't want, the fix is in your next briefing, not in hoping it won't happen again. Error on the side of over-enumeration in HOLD messages — the token cost is trivial next to the cost of reconstructing mutated state.
