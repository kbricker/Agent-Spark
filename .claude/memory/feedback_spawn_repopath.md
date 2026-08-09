---
name: Ephemeral agent repoPath must be local Windows path
description: When spawning ephemeral agents via hive_spawn_agent, repoPath must be a Windows path like C:\Projects\wfa2, NOT a Linux/container path
type: feedback
scope: global
---

When calling `hive_spawn_agent`, the `repoPath` parameter must be a **local Windows path** on Kyle's machine, NOT a Linux/container path.

**Why:** RemoteAgent (the WPF app on Kyle's machine) runs `git remote get-url origin` **with `repoPath` as the working directory** to resolve the clone URL. A Unix path is not a directory there, so git never starts — the agent shows "spawning" and immediately fails with "directory name is invalid".

**How to apply:** Every time you call `hive_spawn_agent`, use the Windows path for the target repo:
- Hive repo: `C:\Projects\wfa2`
- Verlet repo: `C:\Projects\Verlet`
- Never use `/home/claude/repos/...` or any Unix-style path — these ALWAYS fail.

**Also:** The target branch must exist **on the remote** before spawning. The spawn runs `git clone --branch <branch> --single-branch --depth 1`, which fails outright if the branch was never pushed. Always `git checkout -b <branch> && git push -u origin <branch>` first.

`repoPath` is only the URL lookup — the agent never works in it. Its checkout is a fresh per-plan clone at `C:\projects\agents\plans\plan<N>\<repo-basename>`, shared by every agent on that plan.

*Corrected 2026-08-08: this file said RemoteAgent "executes `git worktree add`" from `repoPath`. Plan #154 (`plan154-clone-lifecycle`, PR #47, April 2026) replaced worktrees with per-plan fresh clones and no worktree code remains. The Windows-path rule was right; the mechanism given for it was not.*
