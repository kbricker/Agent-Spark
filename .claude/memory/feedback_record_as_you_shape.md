---
name: Record shaping-log entries as they happen, never batched
description: hive_plan_log_add every entry as it happens (shaping AND dev/review) — the WHY record; entry types in shaping-log skill
type: feedback
scope: global
---

Record plan shaping **as it happens** via `hive_plan_log_add` — a question when it is raised, the answer when it is resolved (linked by `questionId`), every scope decision when it is made, every scope split as a deferral. Entries are append-only: a correction is a new entry pointing at what it supersedes, and even a retype is a new `reclassification` entry rather than an edit. Ticket splits go through `hive_plan_fork`, never a hand-rolled `hive_plan_create`. This does not stop when a plan leaves Planning — review-time deferrals and contract changes get logged too.

**Invoke the `shaping-log` skill** for the full discipline: the entry types and when each applies, what a good entry contains, the fork and deferral linking rules, contract-change vs findings-only during review, what stays in the repo instead, and how to verify coverage rather than assume it. The skill holds the type list; this file deliberately does not repeat it. It used to say "the five entry types", which went stale the moment #837 added more — an enumeration duplicated between a skill and a memory propagated into every workspace drifts silently, and the propagated copy is the one every agent loads.

**Why:** Kyle 2026-07-27 — *"the handling of tickets and shaping logs needs to be 100%, its the basis for our 'meta work' with the hive so agents can learn from things and become more autonomous."* These logs are not paperwork for a human to read later; they are the corpus every future agent mines to understand why the system is the way it is. Patchy logs mean each agent re-derives from scratch and re-proposes options that were already priced and rejected. Shaping that happens only in chat evaporates with the session, and an end-of-session summary flattens the decision sequence into its conclusion — the sequence is the part with information in it. Platform #620/#621, adoption #629, mining #623/#624, consumed by #641.

**How to apply:** Call `hive_plan_log_add` in the same turn the exchange happens; never batch to the end of a session. A sweep only happens if someone asks, and a discipline that depends on being asked is not a discipline. Before claiming a session is captured, read the log back and compare it against `git log` — every commit that changed a design should map to an entry.

This memory is a pointer, kept deliberately short. The skill is canonical: if the two disagree, the skill wins and this file is stale. See [[feedback_plan_preconditions]]; the earned-autonomy plan that consumes these logs is #641.
