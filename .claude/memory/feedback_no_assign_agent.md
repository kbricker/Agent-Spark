---
name: Don't auto-assign agents on plans worked interactively
description: Never set assignedAgent when Kyle is doing the work directly — it can trigger that agent to start working the plan
type: feedback
scope: global
---

Don't set assignedAgent on plans when Kyle is doing the work directly in the interactive session. Setting assignedAgent can trigger that agent to pick up the plan and start working on it autonomously, causing duplicate/conflicting work.

**Why:** A persistent dev agent (the legacy D1, since renamed to vaexdev2) was set as assignedAgent on Plan #84 from plan creation defaults and it started working on the same null-check cleanup Kyle and VaExDev were already doing interactively. Assignment briefly had a second surprising edge — it silently wrote the agent's activePlanId, so every idle-but-assigned agent LOOKED mid-plan and billed its turns to a plan it never worked; plan #791 removed that sync (activePlanId is self-declared via hive_set_status only), so the trigger edge above is the one that remains.

**How to apply:** When creating plans for work being done in the interactive session, leave assignedAgent empty. Only set assignedAgent when intentionally dispatching work to a remote agent.
