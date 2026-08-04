---
name: Don't auto-assign agents on plans worked interactively
description: Setting assignedAgent on a plan can trigger that agent to start working — never set assignedAgent when Kyle is doing the work directly
type: feedback
scope: global
---

Don't set assignedAgent on plans when Kyle is doing the work directly in the interactive session. Setting assignedAgent can trigger that agent to pick up the plan and start working on it autonomously, causing duplicate/conflicting work.

**Why:** A persistent dev agent (the legacy D1, since renamed to vaexdev2) was set as assignedAgent on Plan #84 from plan creation defaults and it started working on the same null-check cleanup Kyle and VaExDev were already doing interactively.

**How to apply:** When creating plans for work being done in the interactive session, leave assignedAgent empty. Only set assignedAgent when intentionally dispatching work to a remote agent.
