---
name: The harness's "compact MEMORY.md" reminder is a 70% warning, not the fleet limit
description: 'Compact MEMORY.md to under 17.1KB' after an edit? Harness 70% warning; the fleet limit is 25,000 bytes — do not compact
type: feedback
scope: global
---

After every write to `.claude/memory/MEMORY.md`, Claude Code (2.1.261, measured by vaexdev 2026-09-05) measures the file against its 200-line / 25 KB read limit and, from 70% of it, appends a PostToolUse reminder: *"The memory index at MEMORY.md is 21.3KB, approaching the 24.4KB read limit. Compact it to under 17.1KB now: keep one line per entry, move detail into topic files, and merge or drop stale entries."* The numbers are the same 25,000-byte limit shown in KiB (24.4 KiB) and its 70% line (17.1 KiB). Every fleet index sits between 17.5 KB and 25,000 bytes by design — the managed blocks alone exceed 17.5 KB — so the reminder fires on every index edit, for every agent, forever.

**Do not act on it.** The fleet limit is 25,000 bytes and 200 lines (plan 778.1), `propcheck.py` fails a propagation that crosses it, and the managed sections are regenerated from canonical — dropping or merging their lines by hand is reverted by the next sync and, until then, loses rules the agent is meant to carry. A local section that has genuinely grown stale is pruned deliberately, on its own merits, never to satisfy this reminder.

**Why:** the reminder reads as an instruction ("Compact it … now") and names concrete actions ("merge or drop stale entries"); an agent that obeys it deletes index lines that the fleet put there. vaexdev traced it to the harness's documented behaviour (code.claude.com/docs/en/memory, "How it works") after first reading it as a fleet hook with a wrong threshold — nothing canonical carries a 17 KB number.

**How to apply:** treat the reminder as noise while the index is under 25,000 bytes. If Kyle ever decides the fleet should live under the 70% line instead, that is a corpus decision (move more always-loaded files into the retrieved tier), taken in canonical by overwatch — not an edit any instance makes to its own index.

Related: [[feedback_check_what_overrides_the_file]].
