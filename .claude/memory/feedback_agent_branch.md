---
name: Always ensure agents are on the correct branch
description: Before any agent does work, first instruct it to checkout the correct branch — step 1 for all agents
type: feedback
scope: role:orchestrator
---

ALWAYS instruct agents to checkout the correct git branch before doing any work — this is step 1 for every agent assignment.

**Why:** A review agent (the legacy R1, since cut by plan #280) reviewed Plan #34 against the wrong branch (master instead of RobertK/BuildingDamage-rebased) and produced entirely invalid findings. Kyle called this out as a fundamental step that should never be skipped.

**How to apply:** When dispatching work to a named agent that owns a long-lived clone (vaexdev, vaexdev2, forge, hivedev01), the first instruction must be `git fetch origin && git checkout <branch> && git pull origin <branch>` in their workspace. Never assume — a long-lived clone sits wherever its last task left it.

(The same hazard applies to subagents fanned out into a clone YOU own, but that is a subagent rule and lives in core, not here — every agent spawns subagents, including the ones that never dispatch.) Once an agent IS on a branch others also commit to, [[feedback_never_force_push_agent]] governs what you may do to it.
