---
name: manage-scope-creep
description: Intervene when a plan is spiraling because dev or review is proposing new unrelated work beyond the original scope. Bug fixes to the diff under review are NOT scope creep — they're the review loop working. Use when signals fire, not as routine review triage.
scope: global
---

# Manage Scope Creep

Scope creep is proposals for **new unrelated work** ("while you're here, let's refactor X", "we should also add Y"). Bug fixes to the code already in the diff are not creep — they're review doing its job. Don't conflate the two.

## Signals to intervene

- Review surfacing items unrelated to the plan's original symptom
- Dev editing files not in the Fix design
- Plan running 2× its estimate
- Reviewer saying "while you're here" / "we should also" / "it would be cleaner if"
- Kyle expressing impatience

## The one hard rule

Regressions the plan's own diff caused are always in scope and must be fixed before merge.

## Cut workflow

1. **Freeze scope.** Message dev + review with the in-scope list: "do not add new items to this plan; describe findings and I'll file separately."
2. **Audit the checklist.** Remove items that are new unrelated work (keep bug fixes to the diff, keep regressions).
3. **File each removed item as its own Planning plan.** Never Backlog. Bundle only if several share a tight scope boundary.
4. **Message Kyle** with the cut summary and the follow-up plan IDs.
5. **Drive the shrunk plan to merge.**

## Surgical changes at the diff level

Scope discipline also applies *inside* a single change, not just across a plan. When editing existing code:

- Touch only what the task requires. Every changed line should trace directly to the stated goal.
- Don't "improve" adjacent code, comments, or formatting that you happen to be near, and don't refactor things that aren't broken.
- Match the existing local style even if you'd write it differently — consistency beats your preference.
- Pre-existing dead code: mention it, don't delete it (deleting it is unrelated work — file it separately if it matters). Do remove imports/variables/helpers that *your own* change just orphaned.

This is the same "no unrelated work" rule as plan-level scope, one altitude down. A diff that quietly reformats a file or rewrites an untouched function is creep even when no checklist item was added.

## Gotchas

- Review agents surface everything; triage is the orchestrator's job, not theirs.
- Small plans wrapping up are not spiraling — don't invoke.
- CodeRabbit refactor suggestions are not mandatory; sift them the same way.
- Never defer regressions the plan itself introduced.
