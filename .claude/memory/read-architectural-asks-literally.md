---
name: read-architectural-asks-literally
description: "Kyle redirected scope with an architectural critique? Re-read his exact words — don't snap to the nearest familiar fix"
source: core/read-architectural-asks-literally@97
metadata:
  type: feedback
---

When Kyle redirects a plan's scope with an architectural critique, resist the urge to pattern-match to the nearest familiar solution. Parse his words literally, including negative space ("I don't think we need X" = X should not exist, not "X should be smaller").

**Why:** On plan #290 (2026-04-20), Kyle said: *"if we fix the uri, even if I have 2 servers running on different ports, the build of a game will run in that port"* and *"the port fix is bogus"*. The literal reading: no second preview server exists; preview runs at a path on the dev server's existing URL. I pattern-matched to "OS picks the second port" (the familiar EADDRINUSE fix) and shipped that. Kyle corrected: *"but I literally asked you to change the ticket so the build uses url with no port."* Filed plan #300 to actually do what he asked. Avoidable rework.

**How to apply:** When Kyle critiques a plan scope:
1. Re-read the critique *word by word*. What nouns are present? What nouns are absent? ("no port" means the port concept shouldn't exist, not "pick the port differently.")
2. Ask yourself: am I hearing him propose *a new architecture*, or am I rewriting his words into *a smaller version of the current architecture*? The first is usually what he means.
3. Before restructuring the plan description, paraphrase his critique back and check the paraphrase is faithful. If your version adds mechanisms he didn't mention (auto-pick, mutex, second anything), you're probably pattern-matching, not listening.
4. When uncertain between two readings of his direction, ASK instead of guessing — the cost of a clarifying question is tiny next to the cost of shipping the wrong architecture.
