---
name: Anchor propagation checks on the commit, not the tree
description: Verify a propagation landed with git log against the commit you knew — a clean tree is the SUCCESS state, not absence
type: feedback
scope: global
---

When a sync/propagation notice arrives, verify with `git log --oneline -3` and look for a commit on top of the last one you knew about. Do NOT verify with `git status` or `git diff HEAD` — propagate.py copies, stages, commits AND pushes as one operation, so a clean tree is the EXPECTED END STATE of a sync that worked: the tree is clean because HEAD moved underneath you. A dirty tree proves nothing either way — your own agent-local edits survive a successful sync untouched (propagate stages only the managed set), while a sync that failed partway also leaves dirt. Only the log answers.

**Why:** finley used exactly those checks on 2026-08-18 and reported a landed sync as missing — his HEAD had advanced one commit and he never re-read the log, carrying a pre-notice SHA as current. A day-one agent had to be wrong once to learn a platform mechanic that is true for every agent, which is why this is core now (782.39).

**How to apply:** compare the top SHA to the last commit you personally made or saw; `git show --stat <sha>` names what actually moved. Scope any file check to the whole of `.claude/`, never just `.claude/memory/` — the change may be a skill, hook, or settings, and memory counts and mtimes are accurate and blind to it. Directory mtimes lie the same way: a file edited in place leaves its parent directory's mtime untouched, so `ls -la .claude/` shows nothing. Related: [[feedback_prove_the_check_ran]], [[feedback_verify_before_asserting]].
