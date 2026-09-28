---
name: Kyle reads and directs — never hands-on
description: About to build Kyle a button, or leave him a command to run? Don't — he reads and directs; agents edit tickets and do every bit of housekeeping
type: feedback
scope: global
---

Kyle's role across plans and PRs is **read, approve, and direct** — never operate the machinery himself. Reviewing and editing are done by tools and agents; Kyle steers and gives the final go.

**PRs — CodeRabbit reviews, Kyle merges.** Kyle does not read PR diffs line-by-line. CodeRabbit is the reviewer; Kyle's only gate is the final merge approval once CodeRabbit is clean and findings are addressed. When reporting PR status, describe what CodeRabbit flagged and what was fixed — never "waiting for your review." Kyle 2026-04-17: *"I dont review PRs thats code rabbit."* The full review flow still applies (the never-skip-review rule, for agents that compose the pr-workflow role) — it's just CodeRabbit + Kyle's merge-click, not Kyle reading the diff. (The separate review-agent pipeline retired with the ephemeral path, 782.22.)

**Tickets — agents edit, Kyle directs.** Kyle never edits plan tickets by hand; he reads them and tells an agent what to change. Plan-management surfaces (checklist edit, item text/type, module) are **agent-facing tools**. "We should be able to X" in a Studio/Plans ticket means *the agents* should be able to X — not that a human control is owed. Kyle 2026-07-28: *"I dont want that, I never edit tickets, its all for agents, I just read them and tell you to change etc, so as long as agents can edit items now, we are gtg."*

**Commands — agents run them; Kyle does no housekeeping.** Kyle 2026-09-28: *"I dont ever want to have to do manual tasks related to work I have asked you or any hive agent to do, especially housekeeping stuff like this."* Merged-branch and worktree cleanup, package restores, service restarts, config toggles — the agent's, always. When the auto-mode classifier holds an in-remit action, the command does not go on a list for his hands: the fix is the profile's auto-mode allow rule, and that edit is the one thing only Kyle can make — an agent editing its own auto-mode rules is an unconditional Auto-Mode Bypass deny, and re-issuing a denied command is classed the same way (overwatch, 2026-09-28: three denials on one cleanup). So hand him the finished rule text to paste once, say which file, and never retry the denied command.

**The design implication:** do not scope a dashboard-UI affordance for human plan-editing on the assumption Kyle needs the same hands-on path — that's the [[feedback_no_unrequested_ux]] trap wearing a completeness costume. This does NOT weaken [[feedback_define_done_by_user_visible_behavior]] — it identifies who the *user* is: for plan surfaces the user is an agent, so "done" means an agent can do it; for VaEx/Verlet product work the user is a human and that memory applies unchanged. When an unbuilt item turns out to be scope Kyle doesn't want, delete it and log a `deferral` with disposition `PRECLUDED` quoting him — don't check it.
