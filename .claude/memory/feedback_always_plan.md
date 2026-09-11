---
name: Always plan before building
description: Plan at the gate — about to PR, merge, push shared, propagate, deploy, or told plan / ship? Then plan first. Before that gate there is no ticket
type: feedback
scope: global
---

Plan when the work is about to become shared — you are opening a PR, merging, pushing to a branch others consume, propagating, or deploying — or when the asker says plan, ship, PR, or merge. Research first, write the formal plan (`hive_plan_create`) with the affected paths and edge cases enumerated, align with Kyle when scope is non-trivial, and build against it. The plan is the quality gate; the reviewer is not there to catch what a shallow spec missed.

Before that gate there is no ticket. A test / sample / quick / try ask is delivered as the thing itself; look / check is answered, not built. If the thing is then promoted to ship, write the plan at that point — its description says what already exists and what was decided getting there, which is the shaping record for the quick phase — and review the built thing against the plan's enumeration. Where the enumeration finds a path the quick build missed, that is rework, not a polish loop. This is not the 2026-03-26 failure below: that was no formal plan at all, a quick description handed straight to a reviewer.

**Why:** two corrections from Kyle, in opposite directions, and both hold.
- 2026-03-26: jumping straight to code on the Hive Channel feature, then a clear quality regression when formal plan mode was swapped for a quick description handed to a review agent — fragile, half-baked implementations that seemed to work, broke quickly, and cost a day of rework. Shipped work needs the formal plan.
- 2026-09-11 (plan 1027): "sample FBX in the Test folder... shove it into the test scene" became fifteen minutes, three headless Unity passes and a plan walked to Review before a file was written. "Endlessly grinding on simple problems." The corpus pushed every request into the shipped-work flow because nothing said when this rule does not apply.

**How to apply:**
1. Ask what you are about to do, not only what the words were: if the next action makes the work shared, plan first. Quick-ask words say the asker does not expect that step — they are the hint; the action is the gate.
2. When it applies: research, formal plan with a concrete checklist and enumerated paths, Kyle's alignment for non-trivial scope, then build, checking items off.
3. Work that lands on an existing plan is that plan's — set its status and attribution, one call. That is not ceremony.
4. A true one-line obvious fix still skips planning. Informal discussion with Kyle is discovery — it becomes a plan when it becomes ship work.
