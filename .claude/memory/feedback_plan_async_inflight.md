---
name: Plans answer the two async questions up front
description: Every async flow in a plan must answer "what if the world changed while this was in flight?" and "what if this runs twice / overlaps itself?" — single-flight, sequencing, and cancellation named before dev starts
type: feedback
scope: global
---

For every async flow a plan introduces or touches (fetch/save/mint/flush, timer callback, reconnect loop, event handler doing I/O), the plan answers two questions before development starts:

1. **What if the world changed while this was in flight?** (scene/selection/target switched, entity evicted, newer save issued) — name the staleness guard: re-check the target on completion, sequence/version the writes, or cancel on context change.
2. **What if this runs twice or overlaps itself?** — name the single-flight story: guard flag, semaphore, debounce, idempotence, or an explicit "overlap is safe because…".

**Why:** ~110 findings in the #624 review-catch mining (approved by Kyle 2026-07-22): fire-and-forget writes, late fetch results clobbering newer state, unsequenced optimistic saves where a slower older write wins, overlapping timers with no single-flight guard. Heaviest in Verlet editor code and wfa2 services; the shape persists into July. Ripeness criterion 3 — review keeps catching what planning never asked.

**How to apply:** In the plan description or checklist, one line per async flow with its answer to both questions. "No async flows touched" stated explicitly counts as the check.
