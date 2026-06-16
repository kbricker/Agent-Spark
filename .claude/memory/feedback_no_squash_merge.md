---
name: Never squash-merge PRs
description: Always use a merge commit (not squash) when merging PRs in WonderForge/VaEx and related repos
type: feedback
scope: global
---

NEVER use `--squash` when merging a PR via `gh pr merge`. Default to merge commit (`--merge`) unless Kyle explicitly asks otherwise.

**Why:** Kyle's PRs often bundle multiple logically distinct commits (feature work + incremental fixes + CodeRabbit responses). Squash flattens all of that into a single commit on master, losing the per-change granularity that's useful for `git blame`, `git log`, bisecting, and understanding what landed when. Corrected 2026-04-19 after plan-266 PR #225 was squash-merged.

**How to apply:** When completing the CodeRabbit loop or any other PR merge, run `gh pr merge <n> --repo <repo> --merge --delete-branch`. Do not use `--squash`. If unsure about the merge style for a repo, ask before merging.
