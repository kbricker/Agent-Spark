---
name: Plans enumerate the state lifecycle of every stateful surface
description: Any plan touching stateful surfaces (pooled objects, caches, mode controllers, serialized/numeric inputs) must enumerate init → reset → teardown → reuse paths plus value-domain constraints before dev starts
type: feedback
scope: global
---

Before development starts, a plan that introduces or modifies a stateful surface must carry a **state-lifecycle table**: for each stateful thing (pooled object, cache, mode/selection controller, persisted field, serialized/Inspector input), name how it initializes, every path that must reset it, how it tears down, and what happens on reuse. New numeric inputs also get their value-domain constraints stated (empty-collection division, truncation, negative/out-of-range values).

**Why:** The single largest persisting cluster in the #624 review-catch mining (approved by Kyle 2026-07-22): ~180 findings across all six months — pooled objects reused with stale state, mode handoffs leaving velocity/cache/reveals behind, new fields missing from ClearState/reset paths, unvalidated Inspector ranges, divide-by-zero on empty collections. These are ripeness criterion 3 failures (gaps not named): review keeps catching them because planning never enumerated the lifecycle.

**How to apply:** During plan shaping (fast-track planning step), add a checklist item or description section listing each touched stateful surface and its init / reset-paths (including pool reuse and mode handoff) / teardown / value-domain constraints. If the table is trivial ("no stateful surfaces"), say so explicitly — the absence claim is the check.
