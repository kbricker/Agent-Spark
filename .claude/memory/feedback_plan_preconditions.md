---
name: Plans answer the #624 pre-conditions before dev — state lifecycle and async
description: Before dev, a plan names every touched stateful surface's lifecycle and every async flow's staleness + single-flight guards — or states none touched
type: feedback
scope: global
---

Before development starts, a plan that touches stateful surfaces or async flows must answer these pre-conditions explicitly. Stating "none touched" counts as the answer. Both were the two largest persisting clusters in the #624 review-catch mining (Kyle-approved 2026-07-22) — review keeps catching what planning never asked (ripeness criterion 3).

**1. State lifecycle (~180 findings).** For each stateful surface (pooled object, cache, mode/selection controller, persisted field, serialized/Inspector input): name how it initializes, every path that must reset it (including pool reuse and mode handoff), how it tears down, and what happens on reuse. New numeric inputs also state their value-domain constraints (empty-collection division, truncation, negative/out-of-range). The failures: pooled objects reused with stale state, mode handoffs leaving velocity/cache behind, new fields missing from reset paths, unvalidated ranges, divide-by-zero.

**2. Async in-flight (~110 findings).** For each async flow (fetch/save/mint/flush, timer callback, reconnect loop, event handler doing I/O), answer:
   - **What if the world changed mid-flight?** (scene/selection/target switched, entity evicted, newer save issued) — name the staleness guard: re-check the target on completion, sequence/version the writes, or cancel on context change.
   - **What if it runs twice or overlaps?** — name the single-flight story: guard flag, semaphore, debounce, idempotence, or "overlap is safe because…". The failures: fire-and-forget writes, late results clobbering newer state, unsequenced optimistic saves where a slower older write wins.

**How to apply:** In the plan description or checklist, one line per touched surface / async flow with its answer. The third #624 pre-condition — the enumerated touched-surface/consumer audit — lives in [[feedback_solve_the_actual_problem]] (item 7).
