---
name: Ephemeral agent repoPath must be local Windows path
description: When spawning ephemeral agents via hive_spawn_agent, repoPath must be a Windows path like C:\Projects\wfa2, NOT a Linux/container path
type: feedback
scope: global
---

When calling `hive_spawn_agent`, the `repoPath` parameter must be a **local Windows path** on Kyle's machine, NOT a Linux/container path.

**Why:** The RemoteAgent (WPF app) runs on Kyle's Windows machine and executes `git worktree add` from this path. A Linux/Unix path causes "directory name is invalid" error — the agent shows "spawning" but immediately fails.

**How to apply:** Every time you call `hive_spawn_agent`, use the Windows path for the target repo:
- Hive repo: `C:\Projects\wfa2`
- Verlet repo: `C:\Projects\Verlet`
- Never use `/home/claude/repos/...` or any Unix-style path — these ALWAYS fail.

**Also:** The target branch must exist on the remote before spawning. The worktree `git checkout` fails with "invalid reference" if the branch hasn't been pushed. Always `git checkout -b <branch> && git push -u origin <branch>` before calling `hive_spawn_agent`.
