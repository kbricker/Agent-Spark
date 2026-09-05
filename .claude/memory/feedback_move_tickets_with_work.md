---
name: Move and declare tickets as work starts and stops
description: Started or stopped a ticket? Move it (Development/CodeReview/Completed) and declare it: hive_set_status planId or ""
type: feedback
scope: global
---

A plan's status must match what is actually happening to it, at three moments:

- **Before the first edit** → `Development` (walk `Planning → Review → Ready → Development`)
- **The moment the PR exists** → `CodeReview`, with `prUrl` and `gitBranch` set
- **After merge and any deploy** → `Completed`, with every checklist item checked

**Declare the ticket as you move it (#937).** The burn ledger stamps every turn with the plan you have DECLARED and nothing else — never inferred from a branch, a commit or prose, never split across tickets — so an undeclared ticket costs nothing on paper, and a stale declaration bills unrelated work to a ticket that looks right:

- **When you start working a ticket** — shaping Q&A included, from the moment the plan exists — `hive_set_status(planId: "<bare number>")`. The bare id, never a dotted display number: the route rejects anything but digits.
- **When you stop** — switching tickets, parking it, finishing — `hive_set_status(planId: "")`. Overwatch billed four days and 718M tokens to a Completed #936 by skipping this (2026-08-31 to 09-04).
- The declaration also EXPIRES on its own when the plan reaches Completed or Cancelled and when your session restarts (#937) — a restart handoff re-declares. Expiry fails toward unattributed, which Kyle prefers to mis-attributed; it does not replace the explicit clear.

**This applies to work YOU do inline, not just work you delegate.** An older wording keyed the trigger entirely on dispatching work to someone else, so on the path we actually use — you editing files yourself — the condition was never met and the rule never fired. If you are editing files for a plan, the plan is in Development, no matter whose hands are on the keyboard.

**Why:** the dashboard is Kyle's only view of what is in flight. A plan in Planning while its code is being written — or in CodeReview after it shipped — makes the board describe a world that does not exist, and a stalled plan becomes indistinguishable from a healthy one. Kyle has raised this repeatedly. Measured 2026-07-30: of 190 open plans, 143 sat in Planning; 16 of those had checklist items already checked and 2 were fully checked; 5 more carried a branch or PR while still pre-Development; 5 had a PR and had never been closed.

**How to apply:**
- Do the `Planning → Review → Ready → Development` walk as one batch before the first edit. Set `assignedAgent` + `reviewAgent` + `fastTrack` FIRST — `fastTrack` skips dashboard-approval gates but not the agent-required gate, and a direct `Planning → Development` hop is rejected as "not an allowed transition". The ceremony is four calls; pay it up front rather than skipping it.
- Move to `CodeReview` in the same breath as `gh pr create` — not after CodeRabbit replies.
- Move to `Completed` immediately on merge+deploy. Don't batch it with the next task.
- Declare on the way in and clear on the way out, in the same breath as the status move: the declaration is the only thing that attributes your turns, and the status move is the moment you already have the plan number in hand.
- **If a plan cannot close because it is blocked on something only Kyle can do, say so explicitly in your report and name the item.** A silently-parked plan is invisible — nothing chases it and it looks abandoned. Blocked is a fine state; blocked and unsaid is not.

The operative gates live inline in the `fast-track-plan` skill at steps 4, 6 and 8. Do not rely on recalling this memory at the moment of action — see [[feedback_subagents_are_authorized]] for the same lesson learned the hard way about review.

Related: [[feedback_plans_default_planning]], [[feedback_review_vs_done]].
