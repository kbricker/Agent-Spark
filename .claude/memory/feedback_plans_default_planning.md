---
name: Plans default to Planning, not Backlog
description: Before every hive_plan_create — SEARCH for a plan that owns the problem, fork it; status = Planning, never Backlog
type: feedback
scope: global
---

**The name is the rule.** Kyle, 2026-08-03: *"it is why they are called plans and the starting state is planning."* They are **plans**, and they open in **Planning** — the artifact is named for the activity, and the default status is the phase where shaping happens. Both halves of this memory follow from that: file it as Planning, and refine it in place rather than filing a successor once it is shaped.

## Before you create: should this be a fork, or not a new plan at all?

`hive_plan_create` is a tool you can reach for at any moment, so this check has to live somewhere always loaded rather than in a skill you might not invoke.

**The test — did this scope ever belong to an existing plan?**

- **Yes → `hive_plan_fork`.** Fork stamps lineage on both ends and auto-appends a linked deferral on the parent. A hand-rolled create gives you two plans with no relationship, and the connection then lives only in prose someone remembered to write.
- **No, we merely found it while working there → `hive_plan_create`**, plus a provenance note on both plans.
- **It's just the next phase of work already in an existing plan's scope → neither. Keep working that plan.**

That third branch is the one that gets missed. Kyle, 2026-08-03: *"no agent should make a new ticket so blithly... its super annoying how you bloat tickets with scope that makes little sense, and create new tickets when they are not needed."*

**Worked example of getting it wrong (2026-08-03).** Plan #754 said in its own scope: *"if it works, packaging the Hive channel as a plugin gets us onto supported `--channels`."* When Kyle authorised that build, a new plan #773 was created for it. But the scope was already #754's — the answer was fork, or simply carry on. Kyle had to notice the two plans were the same work and ask *"so these are the same ticket?"* before it was caught. It was reparented to 754.1.

The tell that produced the error: the split was drawn on **research vs build**, and on *"this needed Kyle's go-ahead, so it should be its own ticket."* Neither is a scope boundary. Needing authorization to proceed is not the same as the work being separate work — get the go-ahead and keep working the plan you have.

**Why research-vs-build is the trap specifically.** Kyle, 2026-08-03: *"almost all our tickets start as research / rouch shaped goals that need refined into concise workable plans. its exceedingly rare for me to just blurt out a sentance of perfectly formed scope that can just be done."*

So the normal life of a ticket is **rough goal → research → shaped scope → build**, all in one plan. Refinement is the ticket's early phase, not a precursor to it. Treating the end of research as the end of the ticket splits at the point nearly every plan passes through, which is how you get two plans for one piece of work.

Practical consequence: when research on a plan concludes and the way forward is clear, the default is to **rewrite that plan's description and checklist in place** and carry on. A plan whose scope changed as it was shaped is working exactly as intended — it does not need a successor.

## How do you know an existing plan owns it? SEARCH — the test above assumes knowledge you do not have

This is the half that was missing until 2026-08-19, and its absence is why the rule kept being followed and duplicates kept happening anyway. Kyle: *"we have been forking things we find into new tickets, then later you or I notice it is close to or similar to something already ticketed, then we have to merge/consolidate."*

**Search on the QUESTION the work answers, not the words of your title.** Two duplicates found in one consolidation pass, and neither would have been caught by matching titles:

- **782.25 and 782.33 were SIBLINGS in the same epic.** Titles: "the roster settings file is never on an agent's resolution path" and "emit autoMemoryDirectory for every spawned agent". No shared keyword. Same question — *does the settings file we write actually reach the running agent?* — and 782.33's fix rested on an assumption 782.25 had already measured false. Browsing the epic would not have caught it; the titles genuinely describe different things.
- **544.1 and 782.31 had near-identical titles** — "Rename agent taxonomy: virtual -> interactive" and "Agent taxonomy: rename virtual -> agent" — six weeks apart, in different epics, both live and each proposing a different target name for the same enum. Nobody scanned the full corpus at create time, so a trivially findable duplicate survived until a consolidation pass.

**Mechanically:** `GET /api/plans?includeCompleted=true` and match against name + description. Note the default call **omits Completed and Cancelled** (246 open vs 922 total), and finished work is exactly what you want to find — a duplicate of a Completed plan means you should be reading its outcome, not rebuilding it. Search across ALL epics: both cases above crossed or ignored epic boundaries. `hive_recall` does not help here yet — its corpus is curated memory files, not plans (834.2).

**And the answer may be "add an item", not "fork".** The destination for a finding is usually a ticket whose subject already covers it — as a checklist item, or as a paragraph in its description. A new plan has to earn itself on a different owner, a different deliverable, or a gate the host ticket would be blocked behind. Kyle 2026-08-19: *"its annoying how many tickets we create, this epic will never end if we add tickets to it endlessly."*

Fuller reasoning, and the fork-vs-create ordering rules, live in the `shaping-log` skill (§ Scope splits) and `fast-track-plan` step 1. This memory exists because those are on-demand skills and this decision happens at tool-call time.

## Status: Planning, never Backlog

When filing a new Hive plan (including parking-lot platform-improvement tickets that won't be worked on immediately), the default status is **Planning**, not Backlog.

**Why:** Kyle uses Backlog as a deliberate manual gesture — he moves plans there himself when he wants them out of the active view. Defaulting to Backlog is "hiding my own work from him," which defeats the purpose of filing the ticket in the first place. Learned on 2026-04-14 when I filed plans #183 (auto-watch on hive_send_message) and #184 (orphan auto-memory cleanup) in Backlog because Kyle had said "let's batch these as platform improvements later" — I interpreted that as "hide them from active view," but Kyle's reaction was "183 is what? you should never really file in backlog, I move stuff there manually from time to time to get it out of my face."

**How to apply:**
- New plans → always `Planning` status, even parking-lot tickets. They stay visible in Kyle's active view until he decides to hide them.
- If Kyle says "file this for later" or "batch it" or "not now," that's still Planning. The batching is a decision he'll make later; my job is to make the plan visible so it can be batched.
- Backlog is reserved for Kyle's own hand movement. I never file there and I don't move plans there without an explicit instruction that uses the word "backlog."
- Cancelled is still fine for genuinely abandoned/rerouted plans (like #182 when we moved the component-leaf rule out of the global template).
