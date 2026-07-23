---
name: reference_gh_cli_is_wonderforge_account
description: gh CLI is authenticated as kyle-wf (WonderForge) — it cannot create PRs on kbricker personal repos (Spark projects)
metadata: 
  node_type: memory
  type: reference
  originSessionId: 08c4549d-0dcb-4d3f-b861-a56f84597918
---

The `gh` CLI on this machine is logged in as **kyle-wf** (the WonderForge account) only. Git pushes to Spark's personal repos work fine (SSH uses Kyle's personal key), but **gh API operations — PR create/merge — fail with "must be a collaborator"** on kbricker personal repos (TendWright, Orbital).

**How to apply:** before the first PR on a new personal repo, either Kyle runs `gh auth login` to add the kbricker account (then `gh auth switch` / `GH_TOKEN` per repo), or adds kyle-wf as a collaborator on the repo. Discovered 2026-07-15 on TendWright plan #604. If gh gains a kbricker account later, update this memory.

Related: [[feedback_personal_repo_git_identity]], [[project_tendwright]].
