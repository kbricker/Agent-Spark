---
name: Always ensure agents are on the correct branch
description: Before any agent does work, first instruct it to checkout the correct branch — step 1 for all agents
type: feedback
scope: global
---

ALWAYS instruct agents to checkout the correct git branch before doing any work — this is step 1 for every agent assignment.

**Why:** A review agent (the legacy R1, since cut by plan #280) reviewed Plan #34 against the wrong branch (master instead of RobertK/BuildingDamage-rebased) and produced entirely invalid findings. Kyle called this out as a fundamental step that should never be skipped.

**How to apply:** When sending work to any persistent agent (e.g. vaexdev, vaexdev2, forge) or an ephemeral agent operating in a long-lived clone, the first instruction must be `git fetch origin && git checkout <branch> && git pull origin <branch>` in their workspace. Never assume agents are on the right branch. (A fresh per-plan ephemeral clone is created already on its branch — see [[feedback_spawn_repopath]] — so this bites most on persistent agents and long-lived clones.)
