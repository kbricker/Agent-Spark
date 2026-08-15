---
name: Kyle reads and directs — never hands-on
description: Kyle reads and directs, never hands-on — CodeRabbit reviews PRs, agents edit tickets; don't build him hands-on affordances
type: feedback
scope: global
---

Kyle's role across plans and PRs is **read, approve, and direct** — never operate the machinery himself. Reviewing and editing are done by tools and agents; Kyle steers and gives the final go.

**PRs — CodeRabbit reviews, Kyle merges.** Kyle does not read PR diffs line-by-line. CodeRabbit is the reviewer; Kyle's only gate is the final merge approval once CodeRabbit (and, on non-fast-track plans, the review agent) is clean and findings are addressed. When reporting PR status, describe what CodeRabbit flagged and what was fixed — never "waiting for your review." Kyle 2026-04-17: *"I dont review PRs thats code rabbit."* The full review flow still applies (the never-skip-review rule, for agents that compose the pr-workflow role) — it's just CodeRabbit + review agent + Kyle's merge-click, not Kyle reading the diff.

**Tickets — agents edit, Kyle directs.** Kyle never edits plan tickets by hand; he reads them and tells an agent what to change. Plan-management surfaces (checklist edit, item text/type, module) are **agent-facing tools**. "We should be able to X" in a Studio/Plans ticket means *the agents* should be able to X — not that a human control is owed. Kyle 2026-07-28: *"I dont want that, I never edit tickets, its all for agents, I just read them and tell you to change etc, so as long as agents can edit items now, we are gtg."*

**The design implication:** do not scope a dashboard-UI affordance for human plan-editing on the assumption Kyle needs the same hands-on path — that's the [[feedback_no_unrequested_ux]] trap wearing a completeness costume. This does NOT weaken [[feedback_define_done_by_user_visible_behavior]] — it identifies who the *user* is: for plan surfaces the user is an agent, so "done" means an agent can do it; for VaEx/Verlet product work the user is a human and that memory applies unchanged. When an unbuilt item turns out to be scope Kyle doesn't want, delete it and log a `deferral` with disposition `PRECLUDED` quoting him — don't check it.
