---
name: feedback_record_as_you_shape
description: Capture plan-shaping exchanges — questions, answers, decisions, deferrals — into the plan's shaping log via hive_plan_log_add at the moment they happen; ticket splits go through hive_plan_fork
type: feedback
scope: global
---

Record plan shaping AS IT HAPPENS via `hive_plan_log_add` (platform in #620/#621, adoption in #629): a question when it's raised, the answer when it's resolved (linked via `questionId`), every scope decision when it's made, every scope split as a deferral with disposition `PREREQUISITE | FOLLOW_UP | PRECLUDED` — with `linkedPlanId` when the target plan already exists; when it doesn't, log the deferral unlinked and let `hive_plan_fork` complete the link: the fork auto-appends a linked deferral on the parent from its reason field. Append a manual linking entry only when the target plan was created outside fork — always as a new entry, never an edit. Ticket splits go through `hive_plan_fork`, never hand-rolled `hive_plan_create` — fork stamps lineage on both ends. Entries are append-only; corrections are new entries, never edits.

**Why:** The shaping trajectory is mineable data for the task-ripeness initiative (#623). Shaping that happens only in chat evaporates with the session, and after-the-fact summaries flatten the actual decision sequence — which questions were open, what got traded away, when scope split and why. The #624 mining could only recover what was durably recorded; capture-at-the-moment is what makes the ripeness loop possible.

**How to apply:** During any plan shaping conversation (creating, refining, or re-scoping a plan), call `hive_plan_log_add` in the same turn the exchange happens — don't batch entries for the end of the session. If you catch a mistake in an earlier entry, append a correcting entry rather than trying to mutate history. The log is readable back via `hive_plan_log`; review agents consult it before flagging scope issues.

Capture doesn't stop when dev starts (first-audit refinements, Kyle 2026-07-23 — "this whole system is about traceability"):
- A scope deferral discovered DURING review — e.g. a skipped finding pushing work to another plan — gets a linked deferral entry on the shaping log, same as one discovered during shaping.
- When a review-driven change **alters what the plan text promises** (a contract change), the finding records the catch AND a decision entry records the contract change — a later reader sees plan text that no longer matches shipped behavior, and the shaping log is where they look for why. In-scope implementation fixes stay findings-only; no double-logging.
