---
name: Verify before asserting
description: Always verify claims against actual state before telling Kyle something is true — never assume
type: feedback
scope: global
---

Do not assert something is true without verifying it first. Especially for destructive or irreversible actions (like restoring files), double-check the actual state before proceeding.

**Why:** Told Kyle a scene change was included in a squash merge without checking `git log` for that file. Then confidently suggested `git checkout --` to "clean" a line-ending diff, which actually wiped out uncommitted work. The assumption cost him time re-doing Unity scene setup.

**How to apply:** Before claiming something is committed, merged, or safe to discard — run the command to verify. `git log -- <file>`, `git show <commit> -- <file>`, etc. Don't eyeball a diff and assume. Especially never suggest discarding local changes without confirming they're already persisted somewhere.
