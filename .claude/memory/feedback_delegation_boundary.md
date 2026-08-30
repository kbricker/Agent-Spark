---
name: The delegation boundary — inline, subagent, or named agent
description: Handing work off or spawning an agent? Inline for tight loops, subagent by default, named agent only if it earns it
type: feedback
scope: global
---

The three-way rule for where work runs (epic #782, refined by Kyle 2026-08-29):

1. **Inline** — tight iterative loops, phases that share significant context, small work (if the job is three tool calls, a spawn is pure overhead), latency-sensitive steps. A tool loop that round-trips an agent boundary is slowest exactly where speed matters most.
2. **Subagent — the DEFAULT for any discrete job** with no context worth keeping afterward: research, validation, adversarial review, verbose output you will not reference again, parallel independent sub-work. Pick the flavor from the harness's own toolbox: fresh-context by default; a **fork** when the job needs your conversation context rather than a long re-brief; **background** for parallelism; a **custom agent type** when it needs its own tools or model; **worktree isolation** when it edits files alongside you.
3. **Named Hive agent — only when the work earns it**, on one of the six escalation triggers: it outlives your session; others must address it; it runs elsewhere; it needs different authority or attribution; it must be the single owner of a shared resource; it needs isolation stronger than a worktree. **Minting a named agent is overwatch's call alone — every other agent escalates to overwatch, never mints.**

**"To save context" is never a reason to mint.** The deeper test for case 3, from Kyle: a thread earns an agent when it stops being a task and becomes a **project** — context that accumulates and will outlive many sessions. Cloning capacity for a project that already has an owner is not a mint; nothing new accumulates.

**Why:** the boundary was decided across epic #782 and left unwritten until 2026-08-29; agents were applying it from folklore. It is deliberately aligned with Anthropic's harness standards — the subagent do/don't lists above mirror the official Claude Code guidance (tight loops and shared-context phases are their stated when-NOT-to-use; discrete verbose jobs their when-to-use), so cases 1–2 compose harness primitives as-is and only case 3 is Hive's own layer. Agent teams exist in the harness but are experimental and disabled by default — do not build delegation on them.

**How to apply:**
- Default to case 2 for any discrete job — no permission needed, per [[feedback_subagents_are_authorized]], and name the branch in every brief.
- Escalate to case 3 only when a listed trigger genuinely holds, and route the mint request to overwatch with the trigger named.
- Never call hive_spawn_agent — that pipeline is retired ([[feedback_spawn_tools_retired]]); a named agent is reached by ticket and message, not spawned.

Related: [[feedback_fast_track_is_default]], [[feedback_subagents_are_authorized]], [[feedback_spawn_tools_retired]].
