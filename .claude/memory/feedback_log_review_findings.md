---
name: A review is not finished until its findings are in the store
description: A review just settled? Not finished until surviving AND skipped findings are in the store via hive_review_finding_add
type: feedback
scope: global
---

A review is NOT finished until its surviving findings are logged to the fleet-wide
review-findings store (`hive_review_finding_add`, plan #632). This includes skipped
findings (reason in summary) — a deliberately-declined catch is signal. Zero-finding
reviews log nothing.

**Why:** The #624 mining showed internal review catches were near-invisible (26/1590
over six months) because they lived only in session transcripts and evaporated. The
whole task-ripeness loop — mining catches back into planning pre-conditions — starves
without this data. Kyle 2026-07-23: "I don't want this ever forgotten."

**How to apply:** Invoke the `log-review-findings` skill the moment a review's verdict
settles, before the plan moves on. Keep `pattern` generalized (it's the clustering
signal). When a review ran in a subagent, the findings come back in its report and the
agent that spawned it logs them — a subagent's summary is not the store, and nothing
else will carry them across. Verify with `hive_review_finding_list` before closing the plan.
