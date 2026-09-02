---
name: Use the canonical primitive; don't manufacture an abstraction for DRY
description: Tempted to wrap repetition in a new helper for DRY? Use the canonical primitive already there, compose inline instead
type: feedback
scope: global
---

Two failure modes, one root — reaching for a new abstraction when the codebase already gives you what you need:

1. **Don't reinvent a primitive the codebase already has.** When you need to gate on a concept, find the canonical primitive the code already uses for it and compose inline at the call site. Don't hand-roll a parallel definition of the same concept.
2. **Don't manufacture a named abstraction just to satisfy DRY.** A new `IsX` that bundles a canonical primitive with extra conditions earns its name only when the bundled form is itself a distinct domain concept — not merely to consolidate 2–3 call sites. Inline composites with tiny shared prefixes are fine; the abstraction threshold is higher than DRY purity suggests.

**Why:** this surfaced on VaEx (plan #293, 2026-04-21), but the tension is general — VaEx is just where competing features and requirements first drove it hard, and any mature project with lots of overlapping requirements hits the same thing. The two concrete rejections:
- A hand-rolled `IsCapturable = HqLevel == 0 && !Controlled && !Capturing`, when the game already decides capturability with the canonical `ParentRegion.State == RegionState.Explored` in `OnSquadArrive`. Kyle: *"we already have a way to know if the settlement is capturable, this code should not be devising a new way."*
- A reviewer nit proposing a helper `IsPreCaptureUiEligible = IsCapturable && State != Capturing` to DRY three call sites — declined, because it names a UI concern, not a domain concept, and three inline composites read clearer than a new lookup.

**How to apply:**
- Before adding a `public bool IsX` (or equivalent) that compounds existing state, search for the canonical version the codebase already uses. Reuse it; add any extra local suppression inline at the call site rather than pre-bundling it.
- When a reviewer suggests consolidating 2–3 similar composites into a helper, decline by default.
- Reserve a new named helper for: 5+ call sites, a genuinely complex predicate (multiple calls / non-trivial logic), or a concept that names a distinct piece of domain semantics.

Related: [[feedback_no_shortcuts]] — the same minimalism, from the over-building side ("right" is not "elaborate").
