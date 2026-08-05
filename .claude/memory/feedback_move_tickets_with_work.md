---
name: Move tickets when work starts
description: Ticket status tracks reality — first edit→Development, PR opened→CodeReview, merged+deployed→Completed; inline work too
type: feedback
scope: global
---

A plan's status must match what is actually happening to it, at three moments:

- **Before the first edit** → `Development` (walk `Planning → Review → Ready → Development`)
- **The moment the PR exists** → `CodeReview`, with `prUrl` and `gitBranch` set
- **After merge and any deploy** → `Completed`, with every checklist item checked

**This applies to work YOU do inline, not just work you dispatch.** The old wording was keyed entirely on "when spawning a dev agent" — but fast-track is the default path and it never spawns a dev agent, so the trigger condition was never met on the workflow we actually use. The rule fired only on the escape hatch. If you are editing files for a plan, the plan is in Development, no matter whose hands are on the keyboard.

**Why:** the dashboard is Kyle's only view of what is in flight. A plan in Planning while its code is being written — or in CodeReview after it shipped — makes the board describe a world that does not exist, and a stalled plan becomes indistinguishable from a healthy one. Kyle has raised this repeatedly. Measured 2026-07-30: of 190 open plans, 143 sat in Planning; 16 of those had checklist items already checked and 2 were fully checked; 5 more carried a branch or PR while still pre-Development; 5 had a PR and had never been closed.

**How to apply:**
- Do the `Planning → Review → Ready → Development` walk as one batch before the first edit. Set `assignedAgent` + `reviewAgent` + `fastTrack` FIRST — `fastTrack` skips dashboard-approval gates but not the agent-required gate, and a direct `Planning → Development` hop is rejected as "not an allowed transition". The ceremony is four calls; pay it up front rather than skipping it.
- Move to `CodeReview` in the same breath as `gh pr create` — not after CodeRabbit replies.
- Move to `Completed` immediately on merge+deploy. Don't batch it with the next task.
- **If a plan cannot close because it is blocked on something only Kyle can do, say so explicitly in your report and name the item.** A silently-parked plan is invisible — nothing chases it and it looks abandoned. Blocked is a fine state; blocked and unsaid is not.

The operative gates live inline in the `fast-track-plan` skill at steps 4, 6 and 8. Do not rely on recalling this memory at the moment of action — see [[feedback_subagents_are_authorized]] for the same lesson learned the hard way about review.

Related: [[feedback_plans_default_planning]], [[feedback_review_vs_done]].
