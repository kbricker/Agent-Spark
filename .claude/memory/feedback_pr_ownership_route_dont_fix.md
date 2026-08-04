---
name: CR feedback on another agent's PR — route, don't fix
description: When a CodeRabbit webhook fires for a PR vaexdev didn't author, route it to the owning agent instead of opening the PR inline
type: feedback
originSessionId: 4e2b9706-c188-4935-9a5c-da092cd8e101
scope: global
---
CR webhooks land on the vaexdev channel because that's where the webhook is wired, NOT because every PR belongs to vaexdev. Before doing anything on a CR notification, check the PR's commit author / plan owner. If it's another session/agent's PR, route the feedback to that owner (Hive chat or ping Kyle for direction) — do not crack open the PR and start fixing.

**Why:** Kyle 2026-05-18 — I got a CR notification on PR #291 (Plan #445, authored by another session), checked it out in his working Unity clone, applied the fix, pushed. Two problems: (1) wasn't my PR to fix, (2) touched his working clone instead of an agent workspace. VaExDev is the orchestrator, not an inline dev — fixing other agents' work breaks the workflow ownership model.

**How to apply:** On any CR/GitHub notification, first `git log` the PR's commits to check authorship. If author isn't from a vaexdev fast-track session, send the CR summary to the owning agent via `hive_send_message` (or ask Kyle) instead of fixing it. Only touch the PR yourself if explicitly delegated.
