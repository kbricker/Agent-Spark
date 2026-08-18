---
name: Ask Kyle which staged files belong in the commit
description: Don't assume which staged/modified files belong in a commit/PR — if scope is ambiguous, ask Kyle
type: feedback
scope: global
---

When committing on a shared VaEx clone and the working tree has files Kyle staged/modified that I didn't
touch, do NOT assume they're out of scope and silently exclude them. Kyle stages files deliberately. If it's
ambiguous whether they belong in the current commit/PR, **ask** — don't guess in either direction.

**Why:** On Plan #524 I excluded `TerrainTextureMap.asset` + a grassland texture + a version bump because I
assumed they were for a later "terrain texture" change. Kyle had specifically staged them for that PR and was
annoyed I assumed instead of asking ("ask questions don't make assumptions… I specifically included those").

**How to apply:** Still verify staged files before committing (`git diff --cached --name-only` before every
commit in a shared checkout) — but the goal is correct scope, not blanket exclusion. Default to asking which staged changes belong when unsure,
rather than either sweeping them in OR leaving them out on a hunch.
