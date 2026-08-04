---
name: No new abstractions over canonical primitives
description: When the codebase already has a canonical primitive for a concept, use it directly — do not invent a new named compound property just to hide a short inline composition.
type: feedback
scope: global
---

When you need to gate on a concept, find the canonical primitive the game already uses and compose inline at each call site. Do not invent a new named property that bundles the canonical primitive with extra conditions unless the bundled form itself names a distinct game concept.

**Why:** Kyle twice rejected this pattern in one session (2026-04-21 on plan #293). First: my hand-rolled `IsCapturable = HqLevel == 0 && !Controlled && !Capturing` — he pointed me at the canonical `ParentRegion.State == RegionState.Explored` that the game already uses in `OnSquadArrive` to decide when capture starts ("we already have a way to know if the settlement is capturable, this code should not be devising a new way"). Second: CodeRabbit nit suggesting a helper `IsPreCaptureUiEligible = IsCapturable && State != Capturing` to consolidate three call sites — Kyle approved declining because the helper names a UI concern, not a game concept, and three inline composites read clearer than a new lookup.

**How to apply:**
- Before adding a new `public bool IsX` property that compounds existing state, look for the canonical version the game already uses.
- `IsCapturable` currently maps to `ParentRegion.State == RegionState.Explored`. That's the single shared primitive.
- Call sites that need additional local suppression (e.g. "not currently being captured") add the extra check inline at the call site. Don't pre-bundle it.
- If CodeRabbit or another reviewer suggests consolidating 2–3 similar composites into a helper, decline by default — three inline composites with tiny shared prefixes are fine. The abstraction threshold is higher than DRY purity suggests.
- Reserve new named helpers for (a) 5+ call sites, (b) genuinely complex predicates (multiple method calls or non-trivial logic), or (c) concepts that name a distinct piece of game semantics.
