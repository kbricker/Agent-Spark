---
name: Fix workflow problems when you hit them, or ticket them
description: Fix a workflow or process defect the moment you hit it, or file a ticket to circle back — breaking context is worth it
type: feedback
scope: global
---

When a workflow, process, or config defect surfaces while you are doing something else, **fix it in the moment, or file a ticket so it gets circled back to.** Do not note it in passing and carry on.

Kyle, 2026-08-03: *"your job is to always fix workflow things when we encounter them or at least ticket so we can circle back, it breaks context when we stop and fix, but its worth it."*

**Why:** he has explicitly accepted the cost. Stopping mid-task to fix a process defect breaks the thread you were on, and that is a real price — but it is smaller than the same failure recurring until he notices and corrects it himself. The failure mode this replaces is the plausible-sounding *"I'll mention it and keep momentum"*, which reliably means it never gets fixed.

**How to apply:**

- Fix it inline when the fix is small and you are confident. Ticket it when the fix is large, risky, or needs a decision you cannot make.
- "Ticket it" means an actual plan, not a line in a shaping log or a note in chat. If it is only written where nobody will look, it was not ticketed.
- This is not licence to widen scope. Fixing the workflow defect you tripped over is in bounds; the adjacent tidying you noticed while there is not — see [[feedback_check_for_an_existing_ticket_before_growing_scope]] and the `manage-scope-creep` skill.
- Before writing a new rule, **find the existing one.** Most process defects are a rule that already exists and did not fire, not a rule that is missing. Adding a second copy makes the corpus harder to search and does not fix the miss.
- **When a rule exists but did not fire, the fix is the moment, not the wording.** Three separate diagnoses landed on this in 2026: the step 5.5 review gate was being read at step 8, the plan status gates lived in a summary section instead of at first-edit, and the fork-vs-create test sat in two on-demand skills while `hive_plan_create` is callable at any time. Each was fixed by moving the check to where the decision actually happens — a skill's own step for skill-driven work, an always-loaded memory for anything reachable by a bare tool call.

Related: [[feedback_check_what_overrides_the_file]], [[feedback_plans_default_planning]].
