---
name: Closing out interactive Hive plans
description: State-machine transition path required to move an interactive plan from Planning to Completed in Hive
type: reference
scope: global
---

Interactive plans (fast-track, no agents assigned upfront) cannot jump Planning → Completed directly. The Hive state machine enforces a specific path even with `fastTrack: true`. To close one out:

1. Set `reviewAgent: "vaexdev"` and status `Review` (Hive rejects Review without a review agent).
2. Status `Ready`.
3. Set `assignedAgent: "vaexdev"` and status `Development` (Hive rejects Development without a dev agent).
4. Status `CodeReview`.
5. Status `Completed`.

Assigning `vaexdev` as both agents is safe on a finished plan — the `feedback_no_assign_agent.md` rule is about not triggering agent work on plans being actively developed, which doesn't apply once everything has landed and validated.

If any step rejects, sequence back and try the next allowed transition. Backlog → Completed is NOT allowed.
