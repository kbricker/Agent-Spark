---
name: Never call hive_spawn_agent — that pipeline is retired
description: Never call hive_spawn_agent — the pipeline is retired though the tool still advertises it; fan out subagents instead
type: feedback
scope: global
---

**`hive_spawn_agent` is retired (Kyle, 2026-08-16). Do not call it.** This rule is about that ONE tool, deliberately — see the boundary below before generalising it. Fan out in-process subagents instead (`fast-track-plan`, Fan-out pattern), or hand the work to another named agent as its own ticket.

**Why this rule exists even though the tool looks available.** The tool was NOT removed — Kyle kept the infrastructure deliberately, pending a later cleanup — so it is still listed in your tools with a description that actively markets it: a per-plan clone, a choice of roles, a shared workspace. Everything that used to bound it was deleted when the pipeline was retired. **A capability that is still advertised with its manual and its guardrails removed is more dangerous than one that was never there**, because the tool description is what an agent consults at the moment it reaches for a tool, and it now reads as an endorsement.

**THE BOUNDARY — do not restate this rule as "never create a separate agent process".** That phrasing sounds like the same rule and is not: it sweeps in two tools that are fine, and both sit inside do-not-skip steps.

- **`hive_agent_wake` is NOT forbidden by THIS rule** — it starts an EXISTING named, configured agent that is merely Offline, on its own clone, with its own identity. That is the opposite of spawning a plan-scoped throwaway, not a variation of it, so the retirement does not reach it. **But a different gate does, and this rule does not lift it:** whether to hand work to another named agent at all is Kyle's call, not yours. Wake is what you do AFTER he agrees a handoff — never the way you make one. Deploy and restart procedures that wake an agent as a documented step are fine; those are the sub-skill's business and it also puts the agent back to sleep.
- **`hive_kill_agent` is NOT forbidden.** Cleanup runs with the retirement rather than against it, and the server refuses it on any non-ephemeral agent anyway, so it can only ever reach a stray from the retired pipeline. That target set can only shrink to empty now that nothing spawns.

What is retired is **creating a NEW, plan-scoped, throwaway agent process** — and `hive_spawn_agent` is the only tool that does that.

**How to apply:**
- Reaching for `hive_spawn_agent` because a plan feels too large is the exact moment this rule is for. Too large means decompose across subagents, or take the fork to Kyle — never reach for a second pipeline.
- If you genuinely believe a case needs a throwaway plan-scoped agent, that is a conversation with Kyle, not a call you make. Say so and stop.
- If you are working on the cleanup itself, you are doing so under a ticket that says so, and this rule is not in your way.
