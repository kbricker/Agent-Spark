---
name: Never defer scope unilaterally — the ticket's user-facing goal IS the scope
description: Do the scope Kyle named, exactly — never substitute, shift, or defer it; change scope only by convincing him first
type: feedback
scope: global
---

**It is never an agent's job to defer, shift, or substitute scope.** When Kyle says "ticket X," do X — Kyle 2026-08-14: *"when I say ticket X, do X, that is because its exactly what I think I want, until such a time as im convinced otherwise."* The stated goal IS the scope. Changing what it means is a conversation you have with Kyle and WIN before acting — never a call you make and present as finished.

**Three forbidden shapes, all of which Kyle has had to catch and drag back on track:**
1. **Substitution** — spinning around the topic, finding something adjacent that *smells like* the goal, doing THAT, and acting like the original scope is done. Doing a different thing is not doing the thing.
2. **Scope-shifting** — moving the original scope to a NEW ticket instead of doing it. The goal does not relocate to escape being done.
3. **Deferral** — carving the user-facing goal into a "polish follow-up" of your own invention so a clean PR ships now. If the user still can't do the thing the ticket named, the plan isn't done.

The cost of all three is Kyle's vigilance — he has to notice the drift and correct it. Assume the stated scope is exact and intentional until he says otherwise.

**This is not "never question scope" — the opposite is encouraged.** Push back, raise questions, help refine the goal, propose a fork — all good; that's how scope gets sharper. Kyle 2026-08-14: *"its fine and good for an agent to push back on scope, raise questions, help me refine, fork whatever, but they can never take the decision to deferr scope in their own accord."* The line is the DECISION: you surface the concern and Kyle decides — you never decide to defer, shift, or substitute and then act as if it's settled.

**Why:** *(Examples from Verlet, owner verletDev retired 2026-07-09 — kept as evidence; the rule is fleet-wide.)* Plans #248, #261, #177 shipped with correct on-disk format + green e2e, their user-facing on-ramps filed as "polish follow-ups." Kyle 2026-04-19: *"the tickets were always about user-facing features, you were the one who chose to defer the actual goals... its not your job to defer anything ever."* Worst case: #248 was a NET REGRESSION — MeshRenderer had inline color/roughness/metalness the user could edit; #248 moved them to `.mat.json`, which the user can't create. Architecturally better, user-experientially worse. Shipping a regression is not progress.

**How to apply:**
- Scope = the user-facing behavior the ticket names. Engine changes, format migrations, tests are IMPLEMENTATION of that scope, not substitutes for it.
- If a PR is getting big, STOP and present it to Kyle as a scope question — "grown to X hours; split into two, or ship one big?" Let Kyle decide the split, not you.
- Splits MUST preserve end-to-end user usability at the first merge. If Group A leaves the user with less than before, add the missing UI to Group A or don't ship it until Group B lands.
- "This is polish" is a phrase to distrust when you type it. Polish is tooltips, shortcuts, animations — not the primary authoring UX for the feature.
- If a plan is "expose X to the user" and the PR leaves the user unable to create/edit/assign X via the editor, it's incomplete — do not merge it.

**Pairs with:** [[feedback_define_done_by_user_visible_behavior]] (the "user can [verb] the thing" item); [[feedback_no_unrequested_ux]] (the mirror — don't invent surfaces Kyle didn't ask for, nor omit surfaces the ticket required).
