---
name: Checklist checked = implemented, not reviewed
description: Review agents must not check off checklist items during review — checked means code is done, not validated
type: feedback
scope: global
---

Checklist items should only be checked when the code is actually implemented. During plan review, the reviewer validates that items are correct and complete — they do NOT check them off. A review agent once checked off all items during a review pass, which made it look like everything was done when nothing had been built.

**Why:** Kyle caught this on plan 69 — all items appeared complete after review but zero code had been written. Checking items = development complete, not review complete.

**How to apply:** When instructing review agents, explicitly state: "validate items and mark as checked" should NOT be in the review message. Instead say "review for completeness and verify against the codebase — do not check items off, that happens during development."
