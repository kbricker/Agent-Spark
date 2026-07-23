---
name: feedback_record_as_you_shape
description: Capture plan-shaping exchanges — questions, answers, decisions, deferrals — into the plan's shaping log via hive_plan_log_add at the moment they happen; ticket splits go through hive_plan_fork
type: feedback
scope: global
---

Record plan shaping AS IT HAPPENS via `hive_plan_log_add` (platform in #620/#621, adoption in #629): a question when it's raised, the answer when it's resolved (linked via `questionId`), every scope decision when it's made, every scope split as a deferral with disposition `PREREQUISITE | FOLLOW_UP | PRECLUDED` — with `linkedPlanId` when the target plan already exists; when it doesn't, log the deferral unlinked, then append a follow-up deferral entry carrying `linkedPlanId` after the fork creates it (the link is a new entry, never an edit). Ticket splits go through `hive_plan_fork`, never hand-rolled `hive_plan_create` — fork stamps lineage on both ends. Entries are append-only; corrections are new entries, never edits.

**Why:** The shaping trajectory is mineable data for the task-ripeness initiative (#623). Shaping that happens only in chat evaporates with the session, and after-the-fact summaries flatten the actual decision sequence — which questions were open, what got traded away, when scope split and why. The #624 mining could only recover what was durably recorded; capture-at-the-moment is what makes the ripeness loop possible.

**How to apply:** During any plan shaping conversation (creating, refining, or re-scoping a plan), call `hive_plan_log_add` in the same turn the exchange happens — don't batch entries for the end of the session. If you catch a mistake in an earlier entry, append a correcting entry rather than trying to mutate history. The log is readable back via `hive_plan_log`; review agents consult it before flagging scope issues.
