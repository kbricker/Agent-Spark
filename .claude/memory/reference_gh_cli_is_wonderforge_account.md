---
name: The gh CLI only holds the kyle-wf WonderForge account
description: Using gh on a kbricker personal repo (Spark)? It's authed as kyle-wf (WonderForge) and can't create PRs there
type: reference
scope: global
---

The `gh` CLI on this machine is logged in as **kyle-wf** (the WonderForge account) only. Git pushes to Spark's personal repos work fine (SSH uses Kyle's personal key), but **gh API operations — PR create/merge — fail with "must be a collaborator"** on kbricker personal repos (TendWright, Orbital).

**How to apply:** before the first PR on a new personal repo, either Kyle runs `gh auth login` to add the kbricker account (then `gh auth switch` / `GH_TOKEN` per repo), or adds kyle-wf as a collaborator on the repo. Discovered 2026-07-15 on TendWright plan #604. If gh gains a kbricker account later, update this memory. (Spark holds the personal-repo git-identity details locally.)
