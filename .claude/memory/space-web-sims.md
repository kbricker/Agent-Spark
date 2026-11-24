---
name: space-web-sims
description: "docs/space-web-sims.md in the spark workspace is a PARKED future project — never commit it to the Agent-Spark repo (public)"
source: spark/space-web-sims@22
metadata:
  type: project
---

`docs/space-web-sims.md` in the spark workspace (written 2026-07-01) is a different, parked project — Kyle 2026-08-06: *"we will circle back to it at some point, lets not publish that into a public repo for now."*

**Why:** the Agent-Spark workspace repo is public; the doc is unpublished project material.

**How to apply:** leave it untracked. Never stage `docs/` when committing spark config (the [[dont-assume-staged-scope]] rule and the commit-config skill's no-blanket-add rule both cover this — this memory records that the exclusion is deliberate, not drift). When Kyle circles back, it likely becomes its own repo/Hive app.
