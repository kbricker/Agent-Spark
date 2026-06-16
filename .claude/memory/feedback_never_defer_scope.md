---
name: Never defer scope unilaterally — the ticket's user-facing goal IS the scope
description: Verlet tickets are always about user-facing features. Do not invent "polish follow-up" buckets on your own to get a PR shipped. If the user can't do the thing, the plan isn't done.
type: feedback
scope: global
---

**The rule:** It is not my job to defer scope. Ever. If the ticket's stated purpose is "bring X to the user," then the scope is "user can do X via the editor UI without hand-editing files." Carving that up into "ship the engine now, follow up with UI later" is a scope shift I am not authorized to make — regardless of how clean the engine diff looks or how green the tests are.

**Why:** Plans #248 (material-as-asset), #261 (HDR environments), #177 (MeshRenderer.geometry) all got shipped with correct on-disk format + green e2e, with their user-facing on-ramps filed as "follow-ups" I named "polish." After three of those stacked up, Kyle said (2026-04-19): "the tickets were always about user-facing features, you were the one who chose to defer the actual goals. its madness, whats the point of 6 hours of engine work that does not actually expose the features we enabled, actually took stuff away, cant even set color! its not your job to defer anything ever." The worst case: #248 produced a NET REGRESSION — MeshRenderer used to have inline color / roughness / metalness the user could edit; after #248 those moved to `.mat.json` which the user can't create. Feature got architecturally better, user-experientially worse. Shipping a regression is not shipping progress.

**How to apply:**
- When drafting or reviewing a plan, the scope = the user-facing behavior the ticket names. Engine changes, format migrations, tests are IMPLEMENTATION of that scope, not substitutes for it.
- If I'm about to file a checklist item as a "follow-up" because the current PR is getting big, STOP. Present the size problem to Kyle as a scope question: "this plan has grown to X hours; should we split into two plans or ship this one big?" Let Kyle decide the split, not me.
- Splits MUST preserve end-to-end user usability at the first merge. If Group A leaves the user with less than they had before Group A started, Group A is broken — either add the missing UI to Group A or don't ship Group A until Group B lands too.
- "This is polish" is a phrase I should be suspicious of when I type it. Polish is tooltips, shortcuts, animations. The primary authoring UX for an asset type is NOT polish — it's the feature.
- If a plan is "expose X to the user" and the PR leaves the user unable to create/edit/assign X via the editor, the PR is incomplete, not just "v1." Do not merge it.

**Pairs with:**
- `feedback_define_done_by_user_visible_behavior.md` — the "user can [verb] the thing" validation item
- `feedback_no_unrequested_ux.md` — don't invent surfaces Kyle didn't ask for (the mirror image: don't omit surfaces the ticket required either)
