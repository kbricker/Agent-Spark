---
name: no-commits-in-agents-working-tree
description: Never commit in a repo checkout an agent is actively working in — check current branch first
metadata:
  type: feedback
scope: global
---

While spark was mid-plan on TendWright, I committed a CLAUDE.md edit in `C:\Projects\TendWright` assuming it was on `main` — it landed on spark's feature branch (`plan618/bench-toolkit`) instead, and the push failed on missing upstream (2026-07-21).

**Why:** Repos like TendWright are a single checkout shared with the working agent. When the agent is mid-plan, the tree sits on their feature branch; any commit I make lands there, tangling my change into their work and risking state confusion.

**How to apply:** Before committing in any repo an agent works in, run `git branch --show-current`. If it's a plan/feature branch (or the agent is working per Hive status), don't commit — either message the agent to include the change, or wait for the branch to merge. Related: [[feedback_fast_track_is_default]]
