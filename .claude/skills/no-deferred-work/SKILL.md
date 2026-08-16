---
name: no-deferred-work
description: Procedural gate that MUST be invoked any time you are about to defer scoped work, leave a "follow-up needed" note, file a TODO comment, or carve a piece of a plan out into "we'll come back to it later." 100% rule — work that was scoped into a plan never moves to "later" or to another ticket without an explicit Kyle conversation and his direction to do so. You may argue for a reorg, a fork, or a prerequisite; you may not decide to defer. Applies to every agent AND to every subagent it spawns during plan execution.
scope: global
---

# No Deferred Work Without Express Auth

This skill is a **hard procedural gate** on deferral. Run through it in order before you defer, postpone, push-out, or "follow-up-plan" any piece of scoped work. Do not skip steps. Do not silently bypass this skill because "it's a small detail" or "the test agent will catch it later" — those are exactly the deferrals that turn into invisible platform failures three weeks later.

## Why this skill exists

**The #280 incident (2026-05-02 → discovered 2026-05-22). Historical — the agent names below are NOT today's roster.** Plan #280 renamed the then-current persistent dev roster (D1→vaexdev2, D2→vaexdev3, dev-backend→vaexserverdev) and shipped the wake/sleep lifecycle. Those three were retired on 2026-08-07, and **the `vaexdev2` key was later reused for an unrelated agent** — today's vaexdev2 is a virtual orchestrator created 2026-08-04, not the renamed D1. Read this section for the failure shape only; do not take any identity claim in it as current. The plan was marked Completed with all 23 checklist items green. But the renamed home folders were left with only old D1/D2/dev-backend CLAUDE.md content carried over by the rename, and were never given `.mcp.json` or `.claude/settings.json`. The deferral was noted in `deploy-persistent-agent-config` SKILL.md as *"templates for the renamed roster have not been authored yet — flagged in the README as a follow-up plan"* — and that was the only signal back to Kyle.

Three weeks later, when vaexdev tried to dispatch real plan work to vaexdev2 and vaexdev3, both agents booted with **zero Hive MCP servers registered**. Effectively un-orchestrable. The "follow-up plan" was never filed, never planned, never executed. The deferral was invisible from the dashboard, the plan was Completed on paper, and the failure surfaced as a confusing "the agents woke but didn't work" symptom that took targeted diagnosis to root-cause.

Kyle's response (2026-05-22): *"ok that was an error to leave this work undone with no indication to me haha … file the hive plan, and create a skill for this, it should be 100% of the time that work is completed, never deferred without discussion and explicit direction to move tasks to other tickets"*.

This skill is the gate that closes that loop.

## When to invoke this skill

**Every single time you are about to push work out of the current scope.** Specifically:

- Any moment you're about to add a "follow-up plan needed" line to a plan description, commit message, PR description, or skill README
- Any moment you're about to write a `// TODO`, `# TODO`, or equivalent in source code that names work the current task should have done
- Any moment you're about to file a NEW plan to capture work that was implicitly or explicitly in the current plan's scope
- Any moment you're about to drop a checklist item with "we'll do this later" reasoning rather than because the item was wrong
- Any moment you're about to merge a PR whose stated goal includes a behavior the merged code doesn't deliver yet
- Any moment you're about to mark a plan Completed knowing a piece of its stated scope is unfinished
- Any moment a subagent's report says "I'll leave the X integration for a future PR" or "the test coverage for Y is a follow-up"
- Any moment a review agent flags something and you're about to respond with "valid finding, but out of scope — file a follow-up"
- Any moment a CodeRabbit finding gets dismissed as "not in this PR's scope"

If you're not sure whether what you're about to do counts as deferral, invoke this skill anyway. Cost of running it: 60 seconds. Cost of missing it: the #280 incident.

## What counts as "deferring scoped work"

**COUNTS:**
- Pushing a checklist item to "a future plan" without Kyle naming the split
- Closing/merging a plan with known incomplete pieces of its goal — even small ones
- Leaving infrastructure prerequisites unprovisioned with a note like "templates not authored yet, follow-up"
- Writing code that depends on configuration / data / templates that don't exist yet, on the assumption they'll be added later
- Letting a review finding stand as "valid but out of scope" without checking with Kyle
- Renaming/moving/deleting something and leaving behind a stale reference with the intention to fix it later
- Implementing the engine half of a feature and filing the UI half as a follow-up plan
- Filing the structural change and deferring the data migration to "next plan"
- Any "ship now, polish later" framing of a piece of scope

**DOES NOT COUNT:**
- Truly out-of-scope discoveries — e.g., a dev agent finds a pre-existing bug unrelated to the plan's stated goal. That's a legitimate new bug report, not deferral. (But default to suspicion: ask yourself whether the "unrelated bug" is actually something the current plan should have surfaced or caused.)
- Kyle-authorized splits — if Kyle has explicitly said "let's do that in a follow-up plan, file it now," that's authorization. Document it with a back-reference to the conversation.
- Capturing genuinely new ideas surfaced during work — fine to note them on a separate plan/spec, as long as you don't claim the current plan is "done" if it actually requires them.

## The gate — run through every step, in order

### Step 1: STOP

Do not push the deferral note. Do not file the follow-up plan. Do not mark the current plan Completed. Do not write the TODO comment. Hands off the surface until you've completed the rest of this skill.

### Step 2: Verify it's actually deferral

Re-read the current plan's goal statement and full scope. Ask:

- Was the piece I'm about to defer *implicit* in the plan's stated goal?
  - "Rename this agent" implies: the renamed agent works at least as well as the old one. Provisioning MCP into the renamed home folder was implicit scope. The rename is not done without it.
- Will the user (or any dependent system) be *able to do the thing the plan promised* once this PR merges?
  - If no, the deferred piece is not "follow-up" — it's incomplete current scope.
- If a teammate read the plan name in isolation, would they expect this piece to be done?
  - If yes, deferral changes the meaning of "Completed."

If the answer to any of these is "yes, this is in-scope," continue to Step 3. If you're genuinely confident it's out-of-scope, document why in one sentence before proceeding to Step 3 anyway — the gate still applies, you're just predicting Kyle will approve.

### Step 3: Compile the deferral proposal

Produce the following as a single chat message to Kyle, in this exact shape:

**Proposed deferral:** what specifically you're proposing to push out

**Current plan:** plan ID + name (or the immediate work context if no plan)

**Why I want to defer:** the actual reason. Common honest reasons:
- Scope creep — the piece is genuinely larger than I realized and would dominate the PR
- Dependency — the piece needs something else to land first
- Time — the piece would push the plan past a soft deadline
- Uncertainty — I don't know how to do the piece yet and need design time
- Out of scope — I believe the piece was not part of the plan's stated goal (rare; default to suspicion of this answer)

**What breaks if we defer:**
- User-facing impact: what can the user not do until the deferred piece lands?
- Platform impact: what other agents / systems are subtly broken by the deferral?
- Discoverability of the gap: how would Kyle notice if I deferred and never came back to it? (If the answer is "he wouldn't unless I tell him" — that is the #280 trap; flag it loudly.)

**Proposed disposition:**
1. **File new plan** — what plan ID/name, when does it get prioritized
2. **Split out a PREREQUISITE** — the piece still gets done, and gets done FIRST; the current ticket blocks on it rather than shipping without it. Distinct from option 1, where the work moves to later. Use this when the honest problem is ordering, not scope.
3. **Reorganise the ticket** — the scope is right but sits on the wrong ticket, or wants forking so the parts can land separately. Nothing is dropped or postponed; the boundaries move.
4. **Add to current plan as a Validation item** — push the gate to post-deploy
5. **Drop entirely** — the piece was not actually in scope (rare)
6. **Land it now** — back out of the deferral and finish the work

**Your recommendation:** pick one. Don't hedge.

**Arguing your case is expected; deciding is not.** Kyle 2026-08-16: *"they can argue about it with me, try to convince me to reorg, fork, do a prereq whatever, but they cannot decide to defer on their own."* Make the strongest honest case you have — that is what this proposal is for. The gate is on the decision, not on the disagreement.

### Step 4: Wait for Kyle's explicit direction

"Explicit direction" means Kyle typed one of:

- "yes file the follow-up plan as P{N}"
- "ok defer, I'll track it"
- "land it now, don't defer"
- "drop it, that's out of scope"
- equivalent explicit answer that names the disposition

**NOT authorization:**
- Silence
- "hmm"
- "sure I guess"
- An earlier session's approval for a DIFFERENT deferral
- "the plan implies it" — no plan implies it until Kyle says so explicitly
- A review agent or CodeRabbit "this could be a follow-up" — those are suggestions, not authorizations

If Kyle says "land it now," respect the decision. Do not re-propose the deferral in the same session.

### Step 5: Execute the disposition Kyle picked

- **Filed a new plan:** create it IMMEDIATELY (not "later"), with explicit problem statement, design, full checklist, and a link back to the originating plan. Set it to Planning status. Note its number in the originating plan's description so the deferral is dashboard-visible. **Use `hive_plan_fork`, not `hive_plan_create`** — a split hand-rolled as a create loses the lineage stamp on both ends, and this is a split by definition. Pair it with a shaping-log deferral entry carrying the disposition.
- **Split out a prerequisite:** fork it the same way, but the current plan does NOT proceed to Completed — it blocks. Say so on the originating plan (`disposition: PREREQUISITE` in the deferral entry) so the dashboard shows a blocked ticket rather than a finished one with a loose end.
- **Reorganised:** move the scope to the ticket that should own it and update BOTH descriptions in the same pass. Nothing is postponed here, so nothing should read as postponed — a reorg that leaves the original ticket still claiming the work is just a deferral with better paperwork.
- **Added a Validation item:** edit the current plan's checklist via `hive_plan_add_checklist_item` BEFORE marking the current plan Completed. The validation item must name what behavior must hold for the deferred work to be considered done.
- **Landed it now:** back out of the deferral, do the work, drop a "Replaced proposed deferral, landed inline" line in the commit/PR.
- **Dropped it:** record the reasoning in the plan description or commit so future-you can find it.

### Step 6: Verify the deferral is dashboard-visible

Before claiming the current plan is Completed:

- If you filed a follow-up plan, does the originating plan's description link to it by number?
- If you added a Validation item, did it actually save? (Re-fetch the plan and look for it.)
- If the deferral landed in another plan's scope, is that plan's description updated to reflect the new scope?

A deferral that lives only in a skill README, a commit message, or a buried code comment is **invisible to Kyle**. The dashboard is the source of truth — make the deferral surface there.

## Subagents spawned during plan execution

**A subagent does not load this skill.** It sees only the brief you write, so this gate reaches it only if you put it there. Every subagent brief that could hit a scope decision MUST carry something like: *"If you want to defer, drop, or push out any piece of the scoped work — stop and report a proposal instead. Do not decide it yourself, and do not leave a TODO."* The section below is written as instructions TO a subagent so it can be quoted straight in.

If you are a subagent working a piece of a plan and you hit a "let's defer this piece" moment:

1. **Do not defer.** Do not silently drop the work. Do not write a TODO comment intending to address it later. Do not file a follow-up plan on your own initiative.
2. **Stop and return.** Your final output is the report — give it the Step 3 proposal shape. Include: the plan ID, the checklist item you're working on, and the specific piece you want to defer + why.
3. **The agent that spawned you relays to Kyle and comes back with explicit direction.** Do NOT assume the deferral is approved — if Kyle says land it now, the work gets done.
4. **Default to landing it inline** if there is any ambiguity about whether you are authorized to defer. An extra hour in the current change is cheaper than an invisible platform gap.

**A subagent's deferral is the easiest one to miss, which is why this section exists.** It never reaches Kyle on its own: it arrives as one line inside a summary the spawning agent skims, and "I left X as a follow-up" reads like diligence rather than a decision that needed authorization. If you are the spawning agent, treat any deferral language in a subagent's report as an unanswered question addressed to Kyle — not as a note you may accept on his behalf.

## Escape hatches

**There are none.** No "tiny detail" exemption. No "the review agent will catch it" exemption. No "it's just a follow-up" exemption. No "we agreed in a different session" exemption.

If you find yourself wanting to skip this skill because "surely this one is fine," that's precisely the moment the skill exists for. Run it.

## What this skill implies for plan-completion discipline

Before marking any plan Completed (`hive_plan_update status: Completed`):

- Re-read the plan's stated goal. Can the user / next agent / dependent system do the thing the goal named?
- If no: the plan is not Completed. Either land the remaining work or invoke this skill on the gap.
- Are there any "follow-up" notes anywhere — in commit messages, PR descriptions, skill READMEs, code comments — that name work this plan implicitly required?
- If yes: invoke this skill on each one before marking the plan done.

A plan in Completed status is a claim that its goal is delivered. This skill is what keeps that claim true.

## Pairs with

- `feedback_never_defer_scope.md` — the principle this skill enforces procedurally
- `feedback_define_done_by_user_visible_behavior.md` — the "user can do the thing" validation lens
- `feedback_no_shortcuts.md` — build it right the first time
- `feedback_solve_the_actual_problem.md` — trace all affected paths, not just the obvious one
