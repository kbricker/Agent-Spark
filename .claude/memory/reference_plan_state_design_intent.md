---
name: What the plan state machine was designed for
description: The plan states encode a multi-agent pipeline — planner shapes, adversarial reviewer air-gaps the plan and flags Ready, dev agent picks it up, adversarial review validates the work. Ready is the handoff point. Only the code-review half was ever built
type: reference
scope: global
---

The Hive plan state machine is not bookkeeping. It encodes an intended **multi-agent pipeline**, designed early on and never fully realised because agents were weaker at the time. Kyle, 2026-08-03:

> *"the goal has always been to have planning agents that can shape tickets in the context of a project, have an adversarial review agent with similar context air gap the plan and flag it ready or iterate on touch ups with the planner. then once ready, a ticket can be handed to a dev agent, work done, then we go into an adversarial review phase, get the work validated, then finally completed."*

Mapped onto the states:

| State | Who acts | What happens |
|---|---|---|
| `Planning` | **planning agent** | Shapes a rough goal into a concrete plan, in the context of the project |
| `Review` | **adversarial plan reviewer** | Air-gapped second agent with similar context smell-checks the plan for gaps. Either flags it Ready or iterates touch-ups with the planner |
| `Ready` | — | **Stopping point AND handoff point.** The plan is shaped and gap-checked; it now waits to be picked up |
| `Development` | **dev agent** | Picks the ticket up and builds it |
| `CodeReview` | **adversarial code reviewer** | CodeRabbit and/or internal review subagents validate the work |
| `Completed` | — | Validated, merged, deployed |

**Adversarial review appears twice** — once on the plan, once on the code. That symmetry is the core of the design.

## What is actually built

**The code-review half works.** CodeRabbit has been in the loop a long time, and internal adversarial review subagents (the mandatory step 5.5 pass) now run alongside it. Kyle: *"thats the main spot that is sort of working as designed."*

**The planning-review half was never built.** There is no planning agent distinct from the orchestrator, and no air-gapped adversarial reviewer for plans. So `Review` and `Ready` have had no one to be meaningful *for*, and degenerated into transitions to click through.

## Why the states became syntax — and the tension to be honest about

`fast-track-plan`, the default workflow since 2026-04-19, has the orchestrator **play planner, plan-reviewer and dev inline on one thread**. When a single agent holds every role, `Ready` cannot be a handoff — there is nobody to hand to. That is why its status gate ended up instructing all four transitions in one batch, and why plan states carry so little information today.

So this is a real tension, not a bug to blame on carelessness: **the state machine assumes role separation; the default workflow collapses it.** Both are legitimate. What is not legitimate is pretending the states mean something while batching through them.

**Fast-track was adopted deliberately, and for good reasons — do not read this memory as a case for reviving the old pipeline.** Kyle, 2026-08-03: *"we adopted fast track because the whole system was causing more problems then it solved early on, and farming things out to ephemeral agents who have to rebuild context is wasteful."* The multi-agent pipeline was tried and it lost on two counts: it created more coordination problems than it removed, and every ephemeral agent paid to rebuild context the orchestrator already had.

**The half that works avoids exactly that cost — and that is the reusable lesson.** Step 5.5's adversarial code review is not an ephemeral agent; it is an **in-session subagent**. It gets the air-gap that makes review valuable (fresh eyes, no attachment to the work, no memory of why a choice felt right) while taking a briefed prompt instead of reconstituting a workspace. That is why the code-review half survived contact and the ephemeral pipeline did not.

**So if the planning-review half is ever built, it should mirror step 5.5, not the old pipeline:** an adversarial subagent that reads the shaped plan and gap-checks it before it moves to Ready. Same proven shape, negligible context cost, and it does not reintroduce the coordination overhead that killed the original design. Anyone proposing to revive ephemeral planner and reviewer agents should read this paragraph first.

Practical consequences:

- **When roles are collapsed (fast-track, the common case):** the states still track reality — Development before the first edit, CodeReview at PR, Completed on merge — but `Ready` is a formality, and saying so is more honest than performing it.
- **When roles are separated (a plan shaped in one session and built in another, or work handed to a different agent):** `Ready` is load-bearing. Set it when the plan is gap-checked and stop there. That queue is the whole point.
- **The unbuilt half is a real opportunity, not a historical footnote.** Agents are considerably stronger than when this was designed. An air-gapped plan-review pass is the same shape as the step 5.5 adversarial code review that already demonstrably works — mining that symmetry is the obvious next move whenever Kyle wants to pick it up.

Related: [[feedback_plans_default_planning]] (the fork-vs-create test and why plans start rough), and the `fast-track-plan` skill's step 8 table for what each state asserts.
