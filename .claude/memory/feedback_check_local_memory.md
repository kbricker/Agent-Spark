---
name: Check local project memory first
description: Memory lives in .claude/memory/ inside the project, not the default central ~/.claude/ path — always check there first
type: feedback
scope: global
---

Memory files live in `.claude/memory/` inside the project directory (`C:\projects\overwatch\.claude\memory\`), NOT in the default central path (`C:\Users\kyleb\.claude\projects\...\memory\`). The `autoMemoryDirectory` in `settings.local.json` overrides the default.

**Why:** On first conversation in the new overwatch repo, I checked the central path, got "file does not exist", and assumed I had no memories — then wasted time reading from the old wfagent folder. The files were right here the whole time.

**How to apply:** At conversation start, read `MEMORY.md` from `.claude/memory/MEMORY.md` relative to the project root. Don't trust the system-provided central path as the only location.
