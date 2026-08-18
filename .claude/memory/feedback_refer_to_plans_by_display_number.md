---
name: A parented plan's display number is its name
description: Once a plan has a parent, call it by display number (664.1), not bare id (654); the bare id stays the API argument
type: feedback
scope: global
---

Once a plan is parented, **its display number is its name.** Say and write `664.1`, not `654`. Kyle 2026-07-28: *"once a ticket is actually a subticket, you should use that number 664.1 I would have found, and its the point of subtickets."*

Applies to prose everywhere an agent writes: chat, plan names and descriptions, shaping-log entries, commit messages, and branch names created from that point on. **The underlying `id` remains the machine argument** — `hive_plan_get(id: 654)`, `/api/plans/654`, `hive_plan_log_add(planId: 654)`. Tools take the id; humans get the display number. Quoting the id alongside it (`664.1 · #654`) is fine and often helpful; leading with the bare id is not.

**Why:** the dotted number carries the relationship and the bare id carries nothing — that is the entire point of sub-tickets. It is also the only identifier the dashboard renders, so a plan referred to by its id is a plan nobody can find by looking. This is not hypothetical: #654 was discussed, branched and logged as "654" for days while every screen showed `664.1`, and Kyle could not locate it when he needed it. The string "654" appeared nowhere in the UI.

**Re-parenting, and how much to care.** Display numbers change when a plan is grouped under a parent after the fact — #654 lived a full day standalone before #664 existed, and its number changed retroactively with no migration. When you re-parent, **make a quick pass and fix the obvious references**: the plan's own name and description, and any sibling plan that points at it. Do not chase every historical mention. Pushed branch names, existing commit messages and old log entries stay as they are — they are immutable, and rewriting history to chase a renumber costs more than it returns. Kyle 2026-07-28: *"hygene dictates we should make a pass and fix that, but I dont want to get crazy on that, its more important that going forward you speak consistantly with the subticket display number."*

Going forward beats cleaning up backwards. See [[feedback_plan_preconditions]] and [[feedback_record_as_you_shape]].
