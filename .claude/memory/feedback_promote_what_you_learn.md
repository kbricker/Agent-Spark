---
name: A local memory write triggers a promotion proposal in the same turn
description: Send a PROMOTION PROPOSAL to overwatch in the same turn you write a local memory or learn something beyond your ticket. Never batch it. Local files are scratch pending classification — procedure in the promote-learning skill.
type: feedback
scope: global
---

The moment you write (or the harness auto-writes) a file into your local
`.claude/memory/`, or you learn something that would have saved you meaningful
time had you known it at session start and would still be true for an agent that
isn't you — send a `PROMOTION PROPOSAL` message to overwatch in the same turn.
Not at session end, not batched.

**Why:** Propagation is one-way; nothing merges local knowledge back (plan
782.12). A local memory that stays local is knowledge one agent has and its
sibling does not — byte-identity checks pass while the agents diverge in
reasoning, which is the silent version of the failure. Kyle 2026-08-04:
"anything novel that might pop up in a clone should get a new workflow where you
hear about it, analize, integrate, propagate."

**How to apply:** Invoke the `promote-learning` skill for the message format and
the full loop. Local files are scratch copies pending classification — the reply
names one of five outcomes: promoted → the canonical copy replaces yours;
kept local → only you need it, legitimate for principals, keep it; identity →
it moves into your CLAUDE.md; rejected → overwatch tells you why, and you delete
the local copy and its MEMORY.md index line so no residue survives; escalated →
Kyle decides, hold your copy until the ruling.
