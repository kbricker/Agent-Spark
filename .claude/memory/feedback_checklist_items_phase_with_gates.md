---
name: Phase checklist items against the status gates
description: Phase checklist items against the status gates — anything at-or-after merge is a VALIDATION item, because an unchecked TASK item blocks the move to CodeReview and deadlocks the plan.
type: feedback
scope: global
---

The Hive plan state machine refuses `→ CodeReview` while any **task**-type
checklist item is unchecked. So a task item describing work that can only happen
at or after merge — merging itself, propagation, notifying agents, deploying,
live round-trips, promotion proposals that depend on the merge landing — cannot
be satisfied when the gate checks it, and the plan deadlocks. The only ways out
are checking something that is not done, or checklist surgery mid-flight.

**Why:** the two item types answer different questions. A task item is the
"code is done" receipt the CodeReview gate reads. A validation item is checked
later, after merge and deploy, and does not block the transition.

**How to apply:** when authoring a checklist, phase every item against the
status gates. Task items cover only work completable while the plan sits in
Development. Anything at-or-after merge is a **validation** item. If you are
already deadlocked, correct the item's TYPE rather than checking it — a ticked
box means done, and ticking one to escape a gate is how a plan starts lying.

Observed twice on 2026-07-24 (plans #650, #652) with items like "PR through CR
and merge" and "propagate + notify", and again on 2026-08-08 when vaexdev2 was
forced to send a merge-gated promotion proposal early because the last unchecked
task item was blocking CodeReview. Promoted to core after that third instance:
every agent that authors a plan checklist meets this same gate.

Related: [[feedback_move_tickets_with_work]], [[feedback_review_vs_done]].
