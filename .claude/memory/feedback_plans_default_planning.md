---
name: Plans default to Planning, not Backlog
description: Two checks before every hive_plan_create — should this be a fork of an existing plan instead, and is the status Planning (never Backlog, which is Kyle's manual "get this out of my face" bucket)
type: feedback
scope: global
---

## Before you create: should this be a fork, or not a new plan at all?

`hive_plan_create` is a tool you can reach for at any moment, so this check has to live somewhere always loaded rather than in a skill you might not invoke.

**The test — did this scope ever belong to an existing plan?**

- **Yes → `hive_plan_fork`.** Fork stamps lineage on both ends and auto-appends a linked deferral on the parent. A hand-rolled create gives you two plans with no relationship, and the connection then lives only in prose someone remembered to write.
- **No, we merely found it while working there → `hive_plan_create`**, plus a provenance note on both plans.
- **It's just the next phase of work already in an existing plan's scope → neither. Keep working that plan.**

That third branch is the one that gets missed. Kyle, 2026-08-03: *"no agent should make a new ticket so blithly... its super annoying how you bloat tickets with scope that makes little sense, and create new tickets when they are not needed."*

**Worked example of getting it wrong (2026-08-03).** Plan #754 said in its own scope: *"if it works, packaging the Hive channel as a plugin gets us onto supported `--channels`."* When Kyle authorised that build, a new plan #773 was created for it. But the scope was already #754's — the answer was fork, or simply carry on. Kyle had to notice the two plans were the same work and ask *"so these are the same ticket?"* before it was caught. It was reparented to 754.1.

The tell that produced the error: the split was drawn on **research vs build**, and on *"this needed Kyle's go-ahead, so it should be its own ticket."* Neither is a scope boundary. Needing authorization to proceed is not the same as the work being separate work — get the go-ahead and keep working the plan you have.

Fuller reasoning, and the fork-vs-create ordering rules, live in the `shaping-log` skill (§ Scope splits) and `fast-track-plan` step 1. This memory exists because those are on-demand skills and this decision happens at tool-call time.

## Status: Planning, never Backlog

When filing a new Hive plan (including parking-lot platform-improvement tickets that won't be worked on immediately), the default status is **Planning**, not Backlog.

**Why:** Kyle uses Backlog as a deliberate manual gesture — he moves plans there himself when he wants them out of the active view. Defaulting to Backlog is "hiding my own work from him," which defeats the purpose of filing the ticket in the first place. Learned on 2026-04-14 when I filed plans #183 (auto-watch on hive_send_message) and #184 (orphan auto-memory cleanup) in Backlog because Kyle had said "let's batch these as platform improvements later" — I interpreted that as "hide them from active view," but Kyle's reaction was "183 is what? you should never really file in backlog, I move stuff there manually from time to time to get it out of my face."

**How to apply:**
- New plans → always `Planning` status, even parking-lot tickets. They stay visible in Kyle's active view until he decides to hide them.
- If Kyle says "file this for later" or "batch it" or "not now," that's still Planning. The batching is a decision he'll make later; my job is to make the plan visible so it can be batched.
- Backlog is reserved for Kyle's own hand movement. I never file there and I don't move plans there without an explicit instruction that uses the word "backlog."
- Cancelled is still fine for genuinely abandoned/rerouted plans (like #182 when we moved the component-leaf rule out of the global template).
