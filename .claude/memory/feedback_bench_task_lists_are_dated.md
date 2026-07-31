---
name: feedback_bench_task_lists_are_dated
description: "TendWright bench task lists are dated files — docs/bench-tasks-YYYY-MM-DD.md, one per session, never one rolling document"
metadata:
  node_type: memory
  type: feedback
---

TendWright's bench task lists live in **`docs/bench-tasks-<YYYY-MM-DD>.md`** — one dated file per bench session. Kyle renamed the rolling `docs/bench-tasks.md` to `docs/bench-tasks-2026-07-31.md` himself on 2026-07-31 and said *"I added the date to the bench tasks file for today, that should be the pattern going forward"*.

**Why:** a bench list is a record of what was true and what was asked on a given day, not a live document. A single rolling file quietly rewrites its own history — items get edited in place, and a week later there is no way to see what the list actually said when Kyle walked out to the bench. Dated files make each session's list an immutable artifact, and the sequence of them is the record of what the bench work has actually been.

**How to apply:** when starting a new bench list, create a new dated file. Do not reopen or edit an earlier day's file to add today's items — carry forward whatever is still open into the new one and let the old file stand as it was. The same append-only instinct that governs shaping logs.

Related: [[project_tendwright]].
