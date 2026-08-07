---
name: Check local project memory first
description: Memory lives in .claude/memory/ inside the project, not the default central ~/.claude/ path — always check there first
type: feedback
scope: global
---

Memory files live in `.claude/memory/` inside YOUR workspace (`<your workspace>\.claude\memory\`), NOT in the harness's default central path (`~/.claude/projects/<cwd-slug>/memory/`). The `autoMemoryDirectory` setting — an ABSOLUTE path to your own workspace's memory dir in the checked-in `.claude/settings.json`, per plan #778 — points the harness there; a relative path is silently ignored (CLI 2.1.222) and would reopen the central-store trap.

**Why:** On first conversation in the new overwatch repo, I checked the central path, got "file does not exist", and assumed I had no memories — then wasted time reading from the old wfagent folder. The files were right here the whole time.

**How to apply:** At conversation start, read `MEMORY.md` from `.claude/memory/MEMORY.md` relative to the project root. Don't trust the system-provided central path as the only location.
