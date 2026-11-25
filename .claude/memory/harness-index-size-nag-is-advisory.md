---
name: harness-index-size-nag-is-advisory
description: "'Compact MEMORY.md' nag, or at the 25,000 cap? Nag is harness noise; at the cap never drop a line and keep its file"
source: core/harness-index-size-nag-is-advisory@97
metadata:
  type: feedback
---

After every write to `.claude/memory/MEMORY.md`, Claude Code (2.1.261, measured by vaexdev 2026-09-05) measures the file against its 200-line / 25 KB read limit and, from 70% of it, appends a PostToolUse reminder: *"The memory index at MEMORY.md is 21.3KB, approaching the 24.4KB read limit. Compact it to under 17.1KB now: keep one line per entry, move detail into topic files, and merge or drop stale entries."* The numbers are the same 25,000-byte limit shown in KiB (24.4 KiB) and its 70% line (17.1 KiB). Several fleet indexes sit between 17.5 KB and 25,000 bytes by design — their delivered blocks alone exceed 17.5 KB — so for those agents the reminder fires on every index edit, forever.

**Do not act on it.** The fleet limit is 25,000 bytes and 200 lines (plan 778.1). Hive refuses a class write that would leave the class's index over its budget and larger than it was, and delivery does not place a block that would push an index past the cap. The delivered blocks come from the classes: dropping or merging their lines by hand shrinks nothing Hive holds, stops the block receiving class changes, and loses rules the agent is meant to carry. A local section that has genuinely grown stale is pruned deliberately, on its own merits, never to satisfy this reminder.

**Why:** the reminder reads as an instruction ("Compact it … now") and names concrete actions ("merge or drop stale entries"); an agent that obeys it deletes index lines that the fleet put there. vaexdev traced it to the harness's documented behaviour (code.claude.com/docs/en/memory, "How it works") after first reading it as a fleet hook with a wrong threshold — nothing canonical carries a 17 KB number.

**How to apply:** treat the reminder as noise while the index is under 25,000 bytes. At the cap with a new memory to add, never drop an index line and keep its file: a local file with no index line is in no tier, because `hive_recall` searches only the corpus and the "In retrieval" block comes from the classes, so a name added to it by hand never reaches retrieval and stops the block receiving class changes (vaexdev, eight files, 2026-10-23 and 2026-10-27, plan 834.8). A lookup-shaped local fact stays a local memory, which the memory hook offers to the knowledge inbox for the corpus, and its line stays until the delivery that carries the corpus pointer lands, so the fact is reachable throughout. A rule never enters retrieval: it displaces a local line that is genuinely stale, or, when none is, goes to the inbox the same way, and overwatch makes the room in the classes. At the cap, nothing is parked: no file without a line, no name on a delivered block. If Kyle ever decides the fleet should live under the 70% line instead, that is a corpus decision (move more always-loaded files into the retrieved tier), taken in the classes by overwatch — not an edit any instance makes to its own index.

Related: [[check-what-overrides-the-file]].
