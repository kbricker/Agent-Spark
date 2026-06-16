---
name: A plan is done when the user can use the feature, not when the format change is on disk
description: A plan's definition of done is "the user can do the thing the plan promised." If the on-disk shape is correct but the user can't mint / edit / assign from the editor, the plan is not done — no matter how clean the tests are.
type: feedback
scope: global
---

If the plan is "expose X to the user," then the plan isn't done until there's a user-reachable path to create / edit / assign X from the editor. Disk-level correctness + passing tests are necessary but not sufficient. Don't file the missing UI as a "follow-up" — file it as a shipped-incomplete and close it before picking up the next plan.

**Why:** Plan #248 (material-as-asset) was framed as "bring in and expose materials for the user." I shipped it with correct `.mat.json` disk format, sanitizers, stable-stringify round-trip, five material kinds, and green e2e — but no editor affordance to CREATE a new `.mat.json`. The only path was "copy a fixture file by hand." I then filed "Create Material asset-browser action" as parked under `##Follow-ups against #248` with the reasoning "non-blocking UX polish." That framing was wrong. Kyle called it out during #177 smoke test (2026-04-19): "the entire goal of the ticket 248 was to bring in and expose materials for the user." A user who can't create the thing the plan was supposed to deliver has NOT been given the feature.

**How to apply:**
- When writing a plan description, include at least one validation item phrased as "user can [verb] the thing" — not just "[thing] round-trips through serialize" or "renderer handles [thing]." For #248 this would have been "user creates a new material via an editor action + assigns it to a GameObject in under 5 clicks."
- During plan review, check: if Kyle sat down with the merged PR, could he do the thing the plan promised using only the editor UI? If no, the plan scope is wrong.
- During merge gate: if a user-visible workflow is marked "follow-up," ask whether that follow-up is actually the plan's core deliverable. If yes, delay merge or add it to the current PR.
- Do NOT hide behind "polish" framing for user-reachable surfaces. Polish is things like keyboard shortcuts, tooltips, loading spinners. Creating a primary asset type the plan was named after is not polish — it's the payload.
- Make the success criterion verifiable *up front*, not retrospective. Turn a vague task into a concrete check before you start: "add validation" → "write tests for the invalid inputs, then make them pass"; "fix the bug" → "write a test that reproduces it, then make it pass." For multi-step work, name the check for each step ("step → verify: [the observable that proves it]"). A sharp, testable criterion lets you loop to done on your own; "make it work" forces a clarification round-trip mid-flight. This is the same standard as the user-visible-done rule above, applied per step rather than only at the finish line.
