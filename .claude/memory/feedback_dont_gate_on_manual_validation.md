---
name: Don't gate closure on validations only Kyle can run, or on things that can't happen
description: Never gate closure on a validation only Kyle can run by hand, or on a scenario that can't happen — ship non-breaking work, let real use test it, open a new ticket if it lands wrong.
type: feedback
scope: global
---

Two kinds of validation item are a tax on Kyle rather than evidence, and neither
should hold a ticket open:

- **Expensive-manual, on a non-breaking change.** If proving it needs Kyle at a
  keyboard doing real work (an in-editor check, a device test, a play session),
  and the change cannot break anything already working — **close the ticket.**
  Let other testers and real use surface problems, and open a NEW ticket
  referencing the original if something doesn't land right.
- **Near-impossible or precluded by our own workflow.** A scenario that should
  never occur is not a test, it's a wait for a violation. Don't write it at all.

**Why:** Kyle 2026-08-08: *"generally the problem with many validations is they
are a lot of time to construct for me, and they might also be wildly low
probability / near impossible things. the former, I would rather move on if the
change was non-breaking and let others test, we can always open another ticket
if something does not land right. on the latter, its a waste of my time."*
Two live examples the same week: #810 carried four in-editor Unity checks
(place a building, upgrade it, destroy it, regenerate the map) that were
delegated to other testers as post-release feedback; 782.13 waited on a
CodeRabbit event from a branch matching no plan — which `one-ticket-one-branch`
means should never exist, so the item was waiting on a workflow violation.

**How to apply:**
- **Write fewer, cheaper validations.** Prefer checks an AGENT can run in
  seconds — curl the endpoint, grep the state, diff against a baseline, read the
  log line. The cost this rule objects to is *Kyle's* time, not yours: an
  agent-runnable check is still mandatory and still gets run.
- **Before writing a validation, ask whether the scenario can actually occur.**
  If our own conventions prevent it, the safety net still ships — you just don't
  gate on witnessing it fail.
- **Dropping one is a deliberate act, never a quiet tick.** Delete the item,
  record in the shaping log that it was removed *unrun* and why, and preserve
  its test script there so a future tester can execute it. Never check an item
  you did not run — see [[feedback_review_vs_done]].
- **Say what is unproven in the handback.** "Merged and deployed; the in-editor
  checks are delegated" is honest. Silence reads as validated.

**This does NOT license deferring scope.** [[feedback_never_defer_scope]] and
[[feedback_define_done_by_user_visible_behavior]] govern the *payload* — the
work must be complete and the user must be able to do the thing the plan
promised. This rule governs the *proof* of work already finished. Keep writing
the "user can [verb] the thing" item: it is how a plan's scope stays honest at
authoring time. What changes is that a finished, non-breaking change does not
sit open waiting for Kyle to personally execute it.
