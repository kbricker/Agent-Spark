---
name: Kyle does not edit tickets — agents do
description: Plan/ticket surfaces are agent-facing. Kyle reads plans and directs changes verbally; never scope dashboard UI for human plan editing.
type: feedback
scope: global
---

Kyle never edits plan tickets by hand. He reads them and tells an agent what to change. Plan-management surfaces (checklist edit, item text, item type, module assignment) are **agent-facing tools** — "we should be able to X" in a plan ticket means *the agents* should be able to X, not that a human control is owed.

**Why:** On 2026-07-28, closing plan 723.2 (#718), I held the plan open because it had an unbuilt item for a dashboard inline-edit control and the `no-deferred-work` gate treats unbuilt scope as a blocker. Asked directly, Kyle: *"I dont want that, I never edit tickets, its all for agents, I just read them and tell you to change etc, so as long as agents can edit items now, we are gtg"*. The API + MCP surface was the whole deliverable; the UI half was never really in scope.

**How to apply:**
- When shaping a plan for a plan/ticket-management capability, deliver the API + MCP surface. Do **not** add a dashboard-UI checklist item on the assumption a human needs the same affordance — that's the `feedback_no_unrequested_ux` trap wearing a completeness costume.
- Read "we should be able to…" in a Studio/Plans ticket as *the fleet* should be able to, unless Kyle names a human workflow explicitly.
- This does **not** weaken `feedback_define_done_by_user_visible_behavior` — it identifies who the user is. For plan surfaces the user is an agent, so "done" means an agent can do it. For VaEx/Verlet product work the user is a human and that memory applies unchanged.
- Same shape as [[feedback_kyle_does_not_review_prs]]: Kyle's role is read-and-direct, not hands-on. He approves and steers; agents operate the machinery.
- When an unbuilt item turns out to be scope Kyle doesn't want, delete the item and log a `deferral` with disposition `PRECLUDED` quoting him — don't check it, which would assert work nobody did.
