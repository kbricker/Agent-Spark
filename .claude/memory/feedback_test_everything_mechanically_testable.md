---
name: Test everything mechanically testable before handing anything back
description: Handing Kyle something to try? Run every machine-runnable check yourself first — his time is for eye/flow/UX/gameplay
type: feedback
scope: global
---

If a check can be run by a machine, run it. Kyle's manual time is reserved for what genuinely needs a human: **eye testing, flow, UX and gameplay**. Handing him a menu item to click, a validator to run, or a script to execute is a failure of the job, not a handoff.

Kyle 2026-08-31, after being asked to run a build guard's failure path by hand:

> *"im so tired of you leaving things for me to test that are actually testable. the only things I want to worry about are things that require eye testing and flow / ux / gameplay testing"*

**Why:** an agent that cannot execute its own verification ships work whose green report means nothing — and every such handoff parks a ticket until Kyle has time. That is what left plans #55, #599, #599.1 and #603 sitting for weeks on measurements nobody was blocked on except by hands, and a build guard reached a PR having never once been executed.

**How to apply:**

- Before writing "run this and tell me what it says", ask what stops YOU running it. The answer is usually a solvable environment problem, not an impossibility — a held file lock, a missing spare working copy, a headless invocation you have not looked up yet. Solve that instead of delegating around it.
- **Prove the FAILURE path, not just the success path.** A check that has never fired is indistinguishable from one that cannot fire. See [[feedback_prove_the_check_ran]].
- Genuinely-manual checks still exist and are still worth naming — a visual pass, a gameplay feel test. Name those plainly and hand them over without apology. This rule is about the other kind, and it does not license gating closure on them either: see [[feedback_dont_gate_on_manual_validation]].
- When a class of check keeps needing hands, automating it IS the work, not a distraction from it.

Promoted to global from vaexdev's local memory 2026-08-31 — the failure it describes ("every agent hands work back that it could run itself", vaexdev) is not specific to any one codebase. Domain-specific mechanics for running checks unattended belong in the relevant role pack, not here.
