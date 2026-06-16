---
name: Never leave shims when moving code
description: When refactoring code to a new location, always delete the old location and update every caller in the same change — never leave a forwarder/pass-through stub behind. Shims cause spaghetti.
type: feedback
scope: global
---

Never leave a "shim" — a thin pass-through wrapper in the old location that just forwards to the new home — when moving code during a refactor. Always do a **clean move**: delete the old function/module entirely and update every caller in the same change.

**Why:** Kyle called this out 2026-04-15 during plan #207 design discussion. Shims feel like "less churn, less risk" but they accumulate. Future readers see two locations for the same logic, can't tell which one is canonical, and end up referencing the shim because it's the first thing autocomplete surfaces. Eventually the shim grows its own subtle behavior and the two paths diverge. This is how the codebase rots into spaghetti. Kyle's words: "that's bad form and leads to spaghetti."

**How to apply:**
- When moving code between modules (function relocation, module split, file rename, responsibility reassignment), delete the old location in the same PR that creates the new one.
- Update every caller site, even if it's dozens of files. The grep-and-fix pass is the work.
- If the call-site churn is too large for one PR, split the move itself into smaller pieces — but NEVER leave a forwarder stub "for now."
- Applies to function moves, module splits, method renames, responsibility reorgs — anywhere the temptation is "leave the old name working temporarily."
- Also applies when drafting plan descriptions for dev agents: say "clean move, no stubs, update all callers" explicitly, not "move X to Y" (which agents may interpret as leave-a-shim).
- Words to avoid in design discussions and ticket descriptions: "shim", "pass-through", "forwarder", "thin wrapper for compat", "leave a stub for now". These phrases signal the exact anti-pattern this rule prevents.
