---
name: Never force push from an agent's dedicated clone
description: Never force-push a branch from an agent-owned clone others commit to — cherry-pick or rebase instead
type: feedback
scope: global
---

NEVER force push from an agent's dedicated clone to overwrite a shared branch. An agent clone's history is always potentially stale: it does not include work committed from the main workspace, from another agent's clone, or through merged PRs.

**Why:** a force push from the VaEx4 clone overwrote `kyle/tower-perks-final-bits`, wiping every prefab change Kyle had made in Unity, the data reimports, and several commits made from the main clone. The work had to be redone and the Unity prefab configuration was lost outright. The clone looked correct locally — that is the whole trap.

**How to apply.** When commits made in an agent's clone need to reach a shared branch:

1. Cherry-pick the specific commits onto that branch in the project's **main** clone, or
2. Rebase the agent clone onto the latest remote first, resolve conflicts, then push normally.
3. Never `--force`, and never `--force-with-lease` either — the lease only protects against a remote you have not fetched, not against the local staleness that causes this.

**This gets sharper, not softer, as instances multiply.** With two agents on one project (plan 782.2) every shared branch has at least three possible writers — Kyle in the main clone and one agent in each of theirs. Historical clone assignments in older memories (`vaexdev2` in VaEx3, `vaexdev3` in VaEx4) date from the dormant remote-agent records and are not current; read the live assignment rule rather than assuming a clone from an old note.

Related: [[feedback_agent_branch]]
