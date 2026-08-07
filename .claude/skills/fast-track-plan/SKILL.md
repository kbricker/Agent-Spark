---
name: fast-track-plan
description: The DEFAULT orchestration workflow. Overwatch plays dev + review inline on the main thread and fans out to Agent/Task subagents for parallelizable work. Walks plan status through the gated state machine, merges and deploys. Use on almost every plan. Use `run-plan-workflow` only as the escape hatch for genuinely large / risky / long-running-test work.
scope: global
---

# Fast-track Plan Workflow (default path)

This is the default orchestration workflow. Overwatch plays dev + review inline and fans out to Agent/Task subagents as-needed. Ephemeral dev/review/test agents via `run-plan-workflow` are the **escape hatch** for work this skill can't handle cleanly — not the default entry point.

Per Kyle 2026-04-19: fast-track is the main track for all four virtual orchestrators (overwatch, vaexdev, spark, 3dproppipeline). The old pattern — spawning three ephemerals on every plan — was overkill for the common case, broke cache sharing, and burned startup cost on most plans that didn't need it. See `feedback_fast_track_is_default` for the rule.

## When to use this skill

- A new plan has been filed and you're about to execute. This is the default starting point. Do not ask for fast-track authorization — Kyle's standing rule is fast-track by default.
- A follow-up or polish pass on something already shipped.
- A bug fix.
- A refactor that fits in your main thread's context budget.
- A cross-workspace config change (skills, memory, CLAUDE.md across orchestrators).

## When to escape to `run-plan-workflow` instead

- The plan is genuinely large — many files, many sub-areas, hours of sequential work — and would blow the main thread's context budget.
- The plan needs long-running isolated Playwright testing where the test agent needs hours of browser state that can't share context with you.
- The plan has multi-agent coordination that requires real independent Claude sessions (not subagents that return summaries).
- The work is architecturally risky enough that Kyle wants a second Claude session to review it independently, not just your own self-review.

If unsure, stay with fast-track and fan out for the heavy parts. Escalating to ephemerals is reversible — you can always kill the ephemerals and continue inline. Starting with ephemerals when fast-track would do is the costlier mistake.

## Core procedure

### 1. Create the plan (if not already filed)

Use `hive_plan_create` with `fastTrack: true` by default. Full description, concrete Fix/Task/Validation checklist, Symptom + Fix design + Out-of-scope sections. Plans are load-bearing artifacts — future-you needs to be able to read the plan six months from now and understand what changed and why. See `feedback_plans_default_planning` — Planning status, never Backlog.

**Module selection:** valid modules are `Dashboard, Remote, Plans, Sessions, Bugs, Activity, Infra`. Orchestration plans → `Sessions`. There is no "Hive" module.

**Planning pre-conditions (from #624 review-catch mining, Kyle-approved 2026-07-22):** before moving past Planning, the plan description or checklist must answer three things — explicitly stating "none touched" counts as the answer:
1. **State lifecycle** — for each stateful surface touched (pooled object, cache, mode controller, serialized/numeric input): init / every reset path (incl. pool reuse, mode handoff) / teardown / value-domain constraints. See `feedback_plan_state_lifecycle`.
2. **Async in-flight** — for each async flow: what if the world changed mid-flight, and what if it runs twice/overlaps? See `feedback_plan_async_inflight`.
3. **Touched-surface audit** — when generalizing/modifying an existing surface: the enumerated (greppable) list of consumers and sibling/mirrored implementations, each marked in-scope or out. See `feedback_solve_the_actual_problem` item 7.

**Record as you shape (plan #629 — see `feedback_record_as_you_shape`):** the shaping trajectory is mineable data for the task-ripeness initiative. Capture into the plan's shaping log via `hive_plan_log_add` **at the moment of the exchange**, not as an after-the-fact summary:

- A question raised during planning → log `{type: "question"}` when it's asked, not when it's resolved.
- Kyle's answer → log `{type: "answer", questionId}` linked to the question entry it resolves.
- Every scope decision → log `{type: "decision"}` with what was chosen and why, at the moment it's made.
- Every scope split → log `{type: "deferral", disposition: PREREQUISITE | FOLLOW_UP | PRECLUDED}` at decision time, with `linkedPlanId` if the target plan already exists. If it doesn't yet, log the deferral without the link — and note that `hive_plan_fork` then **auto-appends a linked deferral on the parent from its reason field**, which IS the link entry (verified live, plan #629 validation): don't add a manual duplicate. Only append a linking deferral yourself when the target plan came into existence outside fork — always as a new entry, never as an edit to the original.
- Entries are append-only and immutable — corrections are NEW entries, never edits.

**Ticket splits go through `hive_plan_fork`, never hand-rolled `hive_plan_create`.** Fork stamps lineage on both ends (the parent's fork revision and the child's fork-origin pointer); a hand-rolled create silently loses that lineage. Pair each fork with a deferral entry naming the disposition.

**Capture doesn't stop when dev starts.** A scope deferral discovered during review (e.g. a skipped finding pushing work to another plan) gets a linked deferral entry just like one discovered during shaping. And when a review-driven change alters what the plan text promises — a contract change — the review finding records the catch AND a decision entry records the contract change; in-scope implementation fixes stay findings-only. "Contract" means operator-visible promises (what the tool/feature promises its user), NOT internal architecture/threading divergence from plan text — that stays findings-only (Kyle 2026-07-24, #645 boundary case). For operator-visible contract changes, traceability wins: when plan text no longer matches shipped behavior, record the "why" on the shaping log; internal architecture/topology divergences remain findings-only in the review log.

### 2. Assign yourself as both agents

Required before the status can move past Planning:

```
hive_plan_update({id, assignedAgent: "overwatch", reviewAgent: "overwatch"})
```

`fastTrack: true` skips dashboard-approval gates, NOT agent-required gates. Both assignment fields must be set.

### 3. Decide: single-repo or multi-repo?

- **Single target repo** (wfa2 is the common case): standard branch + PR + merge flow, covered below.
- **Workspace-config-only** (editing `.claude/` in any orchestrator workspace): direct-commit to each workspace's default branch (`master` for all four). No PR flow, no CodeRabbit — these repos are local config stores, not code. Reference the plan number in each commit message.
- **Mixed** (e.g. wfa2 + workspace changes): wfa2 gets the PR flow; workspace repos get direct commits. Reference the same plan number across all.

### 4. Do the work

> **STATUS GATE — move the ticket to Development BEFORE the first edit.** Not after, not at the end. The walk is `Planning → Review → Ready → Development`:
> ```
> hive_plan_update({id, fastTrack: true, assignedAgent: "<you>", reviewAgent: "<you>", gitBranch, baseBranch})
> hive_plan_update({id, status: "Review"})
> hive_plan_update({id, status: "Ready"})       // shaping is done — see below
> hive_plan_update({id, status: "Development"}) // first edit is imminent
> ```
> Assignments must land first — `fastTrack` skips dashboard-approval gates but **not** the agent-required gate, and `Planning → Development` in one hop is rejected as "not an allowed transition".
>
> **`Review` and `Ready` are real states, not transitions to pass through** — see the table at step 8 for what each asserts. `Review` is **planning review**: the plan is baked, and you smell-check it for gaps before any work starts. `Ready` means it passed and is **ready for development — a stopping point in the ticket's lifecycle**, where plans legitimately rest.
>
> Kyle, 2026-08-03: *"ready state means the research and planning has been completed, but we rarely use it properly... its a stopping point in the lifecycle of a ticket. we dont use the workflow well at all today."*
>
> So the intended rhythm is **shape → planning-review → Ready → stop**, with starting the build as a separate later act. Almost every plan begins as a rough goal that needs shaping (see `feedback_plans_default_planning`), which makes Planning→Review→Ready the most informative stretch of the board: it separates "still being figured out" from "gap-checked and buildable." Set each when it is true, not when you happen to reach this step.
>
> Batch all four calls together **only** when the plan arrived already shaped, has genuinely been gap-checked, and you are starting work immediately. That is the rare case, not the default — and this gate previously instructed the batch unconditionally, which is why no plan ever rests in Ready today.
>
> This gate is here, not in step 8, on purpose. Step 8 lists the whole state machine including "before starting work" — but by the time you read step 8 you have already done the work, so that line arrives too late to act on. Measured 2026-07-30: 16 plans sat in Planning with checklist items already checked, 2 of them fully checked; 5 more had a branch or PR while still pre-Development.

- Start from fresh default branch: `git checkout <default> && git pull origin <default>`
- For single-target-repo plans, create a feature branch: `git checkout -b plan{id}/short-slug`
- For config-repo plans, commit to default branch directly
- Edit per the plan's Fix design
- Build if server-side (`"$USERPROFILE/.dotnet/dotnet.exe" build ...`)
- For UI changes, verify in a dev server / loaded dashboard before committing

**Fan out here when it helps.** See the "Fan-out pattern" section below.

### 5. Check for pre-existing uncommitted drift

Before every commit, run `git status` and `git diff` to see what's dirty. Pre-existing uncommitted state is common across orchestrator workspaces — do NOT sweep it into your commit. Use explicit `git add <path>` on only the files you touched. If the plan includes a version bump and the csproj is already dirty-ahead-of-main, fold the existing bump into your commit so git main stays monotonically ahead of what's deployed. See the gotcha on 2026-04-13, plan #178.

### 5.5 Internal adversarial review — mandatory before the first CR push

Before the first push of any fast-track PR branch — the push that opens it to CodeRabbit, and regardless of whether you'll wait for CR — run an internal adversarial review on the complete outgoing diff (plan #650, Kyle 2026-07-24). Stage everything you intend to ship first (explicit `git add <path>` per step 5), then give the subagent `git diff <default>...HEAD` plus `git diff --cached`, and confirm via `git status` that no unstaged or untracked file you meant to include is missing from what it reviewed. No size exemption — trivial diffs still get the pass. Inline self-review alone does not hit the "rigor of a review ephemeral" bar — wfa2 PR #104 shipped a Major to CR (dedup filter silently dropping human review events, finding #112) that this pass is specifically built to catch.

- **Use several lenses in parallel, not one generalist.** Spawn 2-4 subagents with distinct briefs — e.g. correctness, contracts with consumers of the shared surface, and whatever format/serialization the change touches (prefab/YAML, migrations, schema). Field data from VaEx 682.18: the correctness and contract agents independently found the same Major from different directions, which is a strong confidence signal, and the format agent found the round's only Critical — one that neither of the others would have thought to look for. A single generalist reviewer is the cheap version of this step and it under-reads.
  - **Expect overlap between lenses, and read it as signal rather than waste.** Measured on 682.18: ~26 raised items collapsed to 13 logged findings, and the largest slice of that gap — 5 defects — was the *same* defect found independently by two lenses via different routes. That convergence is what lets you stop second-guessing whether a finding is real. Do not cut the lens count to reduce redundancy, and do not read a low logged-to-raised ratio as the reviewers being noisy. On that run there was zero style noise and zero invalid claims to reject; the rest of the gap was correctly-identified non-defects and two write-ups of one bug at different altitudes. Caveat on the sample: it was a UI/prefab-heavy diff, and a pure-logic diff may give reviewers more to have opinions about.
- Brief each subagent to REFUTE the diff: hunt scope-exceeding behavior changes (does any condition apply more broadly than the stated intent?), edge cases, contract breaks with consumers of the touched surface, and state/async gaps. Give it the plan's Fix design as the stated intent and the full diff. Three brief rules that keep signal high. Require every finding to come with a **concrete failure scenario**. Anything that can't be backed by one goes in a clearly-labelled **observations section rather than being silently dropped** — the substantiation bar is deliberately strong, and without this escape valve a real-but-hard-to-prove concern gets discarded instead of surfaced; on 682.18 a TMP font/material atlas issue reached the orchestrator that way and turned out to matter. And tell them to **verify claims made in commit messages and comments rather than take them at face value**. On 682.18 that last rule caught a commit claiming "Navigation set to None" where the serialized value was `4` (`Explicit`); `None` is `0`. The reviewer only caught it by going and reading the enum.
- Fix its valid findings before pushing; consciously skip invalid ones. Then **re-stage the fixed paths** (`git add` — fixes land in the working tree, and an unstaged fix would leave the rerun reviewing the pre-fix index) and re-run the pass on the post-fix diff (continuing the same subagent via SendMessage is fine — it has context); loop restage → rerun until it reports no new valid findings. Log survivors (fixed AND skipped) to the findings store at review settle — batching with the CR findings in one `/log-review-findings` call is fine.
- **The loop is not a formality — it is where much of the value is.** Read this as a hard requirement, not a tidy-up. On VaEx 682.18 the pass ran three rounds and every round found something. Rounds 2 and 3 found defects introduced **entirely by the fixes for round 1**: a fix that was a silent no-op *and* added a keyboard-navigation dead end, state parked in `Awake` instead of `OnEnable` so a panel rode into the next round, a new demo-HUD mirror that could resurrect a panel over the combat HUD, and a freshly-added gate that checked location but not round state — reopening the exact path round 1 had closed. Stopping after one round would have shipped three of them. A fix that does nothing while reading as done in the commit log is a nastier outcome than the original bug, because everything downstream treats it as handled.
- Why this pays: the subagent shares your prompt cache (cheap, fast), its catches cost zero CR review-run quota, and every pre-push catch saves a full CR round-trip (push → review → fix → push → re-review).
- Config-repo direct commits (no PR flow) don't require this step, but use judgment — a workspace skill/hook change that alters orchestrator behavior deserves the same pass.

### 6. Commit, push, (PR if applicable), merge

> **STOP — gate on step 5.5.** If you are about to run `gh pr create` (or the first `git push` of the branch) and have **not** completed the step 5.5 adversarial subagent loop to a clean round, go back and do it now. Not "run it after and fix what it finds" — before.
>
> This gate is duplicated here on purpose. Step 5.5 is several sections up and is not in your working context at the moment you assemble the PR; step 6 is. Two orchestrators have now skipped 5.5 without ever consciously deciding to — the session-config line saying "don't call the Agent tool unless asked" was in context at `gh pr create` and the rule to ignore it was not (see `feedback_subagents_are_authorized`). Prose elsewhere in the file does not survive that moment. This line does.
>
> Self-check, three questions: did a subagent read the full outgoing diff? did the final round come back with nothing new? are the survivors logged? If any answer is no, you are not at step 6 yet.

- Commit message: `Plan #{id}: {short summary}` followed by a short rationale. Reference fix item IDs when helpful.
- For single-target PR flow: push the branch, `gh pr create` with detailed body + test plan, wait for CodeRabbit (default is to wait — only skip when Kyle says "don't wait for rabbit"), merge with `gh pr merge {n} --merge --delete-branch`. Never `--squash`.
- For config-repo direct flow: commit directly to default branch, `git push`, done.

> **STATUS GATE — the moment the PR exists, move the ticket:** `hive_plan_update({id, status: "CodeReview", prUrl, gitBranch})`. Do it in the same breath as `gh pr create`, not after CR replies. A plan sitting in Development with a live PR is the second most common stall we measured.

### 7. Deploy (if applicable)

- If the plan touches `AgentStudio2/` / `McpBridge/src/` / `RemoteAgent/`: invoke `/deploy-hive` as a sub-step.
- If the plan only touches orchestrator workspace config (`.claude/`): no deploy. The local `git pull` in each workspace (or you're already in it) picks up the change.
- If it touches wfa2 hooks/scripts used by orchestrators: message affected orchestrators to `git pull` in `C:/Projects/wfa2`.

### 8. Close the ticket — and reference for the whole state machine

> **STATUS GATE — after the merge and any deploy, move it to Completed.** `hive_plan_update({id, status: "Completed"})`. A merged, deployed plan left in CodeReview reads as in-flight on Kyle's dashboard and is indistinguishable from work that stalled.
>
> **If it cannot close, say so out loud — do not just leave it.** The usual reason is a validation item only Kyle can perform (a UI check, a device test, a round-trip he has to trigger). That is legitimate, but a silently-parked plan is invisible: nothing chases it and it looks identical to an abandoned one. Name the specific item and what you need from him in your report, every time you hand back. Live example at time of writing: #738 and #739 were both merged and deployed yet sat in CodeReview on one unchecked Kyle-only item.
>
> **Never close on a partially-checked list.** Every fix/task/validation item gets checked, or the plan is not Completed — see step 10. If an item turns out not to apply, correct its text or delete it deliberately; do not leave it dangling and close anyway.

**This section is the reference for the full machine. The operative gates are inline at steps 4, 6 and here** — do not rely on reaching this section to remember them.

**Sequential, one step at a time, no skipping:** `Planning → Review → Ready → Development → CodeReview → Completed`.

What each state asserts, since two of them are routinely burned as syntax:

| State | Means |
|---|---|
| `Planning` | Being shaped. The default, and where most plans legitimately spend their early life. |
| `Review` | **Planning review.** The plan is baked; smell-check it for gaps before any work starts. This is a review of the *plan*, not of code — `CodeReview` is the code one. |
| `Ready` | **Passed review; ready for development.** A deliberate stopping point in the lifecycle — plans rest here. |
| `Development` | Someone is editing code right now. |
| `CodeReview` | PR is open. |
| `Completed` | Merged, deployed, every item checked. |

Kyle, 2026-08-03: *"review is PLANNING REVIEW, the intent there is to smell check a baked plan to ensure there are no gaps, then its 'ready' meaning ready for development, its a stopping point in the lifecycle of a ticket. we dont use the workflow well at all today."*

**`Ready` being a stopping point is the part the workflow currently loses.** The intended rhythm is shape → planning-review → Ready → **stop**; picking the work up and starting to build is a separate, later act. That gives the board a queue of shaped, gap-checked plans that anyone can pull from. Running all four transitions in one batch collapses that queue to nothing — every plan is either unshaped or already being built, and the two states that carry the most planning information never hold a plan long enough to be read.

```
hive_plan_update({id, status: "Review"})       // after assignments set
hive_plan_update({id, status: "Ready"})        // when shaping is done — often its own moment
hive_plan_update({id, status: "Development"})  // before starting work
hive_plan_update({id, status: "CodeReview", prUrl, gitBranch})   // after commit
hive_plan_update({id, status: "Completed"})
```

For config-repo plans with no PR, use a descriptive `prUrl` (e.g. direct commit SHA link) or leave null and note it in the commit message.

### 9. Log review findings to the platform store

If the plan ran any review that produced findings — internal adversarial subagents, your own self-review, or CodeRabbit catches worth keeping — **invoke `/log-review-findings`** before completing the plan (plan #632; supersedes the old file-based `reports/internal-review-log/` convention). That skill is the canonical procedure: one `hive_review_finding_add` entry per finding that survived verification, including skipped ones, generalized `pattern`, honest `reviewer`, `criterion` when it's clear. The always-loaded rule is `feedback_log_review_findings`: a review is not finished until its findings are in the store. A review pass with zero surviving findings logs nothing.

### 10. Check off every checklist item

Use `hive_plan_checklist` with `checkedBy: "overwatch"` on every fix + task + validation item. Leave nothing unchecked on a Completed plan. The checklist is the audit trail.

### 11. Report back to Kyle

One or two sentences. What shipped, where to look, follow-ups. Mention any side findings and offer to file separate tickets.

## Fan-out pattern (Agent/Task subagents)

Fast-track is inline by default, but you can and should spawn Agent/Task subagents for parallelizable work. The subagent model shares the prompt cache with you and returns a summary — so it's strictly cheaper and faster than ephemerals for independent sub-work.

### When fan-out helps

- **Independent parallel work.** Same cognitive shape across N targets — e.g. "propagate this memory to three orchestrators", "audit four files for the same pattern", "research five candidate libraries simultaneously". Fire all N in a single message (multiple Agent tool calls in parallel) so they actually run concurrently.
- **Large-context research.** The exploration would pollute the main thread with noise. Delegate to a subagent that returns a tight summary — you keep your context clean.
- **Multi-file audit.** Subagent reads the files, reports the matches, you keep moving.
- **Long-running searches.** Let the subagent grep/glob while you write the next section.

### When to NOT fan out

- **Sequential dependencies.** A → B → C where B can't start until A is done. Subagents can't coordinate mid-run — do it inline.
- **Shared-state edits.** Two subagents editing the same file or overlapping regions will collide. The orchestrator edits shared files itself.
- **Creative / design judgment.** If the step requires synthesis you'd do poorly if you only saw a subagent's summary — do it yourself. "Never delegate understanding" applies: don't write "based on your findings, decide X" in a subagent prompt. Design decisions stay in the main thread.
- **Small work.** If the inline version would take three tool calls, spawning a subagent is pure overhead. Fan-out has a floor.

### Cache-sharing mental model

Subagents spawned during active main-thread work read from the warm prompt cache (~5-minute TTL). This is a real cost/speed win: Agent subagents on this process get cache hits the ephemeral pipeline never does. Fan out parallel sub-work aggressively — the cache is there, use it.

Ephemerals via `run-plan-workflow` are separate Claude Code processes. Zero cache sharing. Spawn cost is real (clone, init, first-message context build). Only pay that cost when the escape-hatch criteria genuinely apply.

### Subagent prompt discipline

Brief each subagent as if it's a colleague who just walked in:
- State the goal and why
- Give context (paths, line numbers, what matters, what to ignore)
- Say what the output format should be and how long
- Tell it explicitly whether to write code or just research
- Never write "based on your findings, fix X" — you do synthesis, it does lookup

### Anti-patterns

- **Spawning a subagent to avoid reading a file yourself.** Use Read.
- **Hedging** — running two subagents on the same question "to compare answers". Pick one approach.
- **Fan-out for sequential work** — see above.
- **Using fan-out as a context escape.** If the plan is genuinely too big for your main thread, that's the `run-plan-workflow` escape-hatch signal. Don't try to chain subagent summaries together as a substitute for a real ephemeral pipeline.
- **Leaving subagent results un-verified.** A subagent's report describes what it intended to do, not necessarily what it did. Before acting on a subagent's claim, verify — especially for file writes.

## Gotchas

- **Status transitions are sequential.** `Planning → Completed` in one call fails. Walk through every state.
- **fastTrack skips dashboard-only gates, not agent-required gates.** You still need `assignedAgent` + `reviewAgent` set.
- **Module must be valid.** `Sessions` for orchestration; "Hive" is not a module.
- **Don't pre-bump a version with a dirty working tree.** Check `git diff` on the csproj first.
- **You are still the reviewer.** Self-review your diff with the same rigor a review ephemeral would — edge cases, regressions, things you'd flag if someone else wrote it. Self-review does NOT replace step 5.5 — the adversarial subagent pass before the first CR push is mandatory.
- **CodeRabbit may run late.** If you merge before CR finishes, the review is harmless against a closed PR — but if it surfaces real findings, open a small follow-up PR rather than ignoring.
- **Pre-existing drift in workspace repos is common.** Always commit by explicit path — never `git add -A`.

## Do not

- Do not default to `run-plan-workflow`. That's the old default and has been replaced. Only use it when the escape-hatch criteria apply.
- Do not skip the checklist on plans you close. The checklist is the receipt.
- Do not fake a Completed status when the work isn't done. `fastTrack` is not a shortcut to skip real review — it's a different-shaped workflow with the same rigor.
- Do not skip deploy on server-side changes. "It's in main" is not "it's live".
- Do not fan out work that has sequential dependencies or shared-state edits. See the anti-patterns section.
- Do not delegate synthesis or design decisions to subagents. You do the thinking; subagents do the lookup/execution.

## Persistent agents and wake/sleep

Fast-track runs inline on the orchestrator's main thread and via Agent/Task subagents — it does **not** dispatch to persistent named agents in its own flow. Per plan #280, remote-class persistent agents (today that is **forge** — vaexdev3/vaexserverdev were retired 2026-08-07 per Kyle, deactivated and hidden, to be rebuilt properly when task volume warrants) boot Offline (`AutoSpinDown: true`) and require an explicit `hive_agent_wake` to come up. **Virtual orchestrators (vaexdev2, spark, ...) are NOT wake targets** — the server refuses a cold-start wake on them (plan 782.10; a wake on an already-running virtual returns a harmless no-op); they come up via their workspace launch script, and you reach a running one with `hive_send_message`.

When fast-track delegates to a sub-skill that does touch a persistent agent, the wake/sleep wrap is that sub-skill's responsibility, not yours. Today only one sub-skill dispatches to a remote-class agent: **`/deploy-hive`** wakes forge as its step 0 and sleeps it as its final step. (`/run-plan-workflow` spawns ephemerals via `hive_spawn_agent` — no wake/sleep involved.)

You should not pre-wake a persistent agent inside fast-track on the assumption it'll be needed — wake/sleep has a measurable cost (process spin-up, clone re-attach), so leave it to the sub-skill that actually dispatches. If you find yourself reaching for `hive_agent_wake` at the fast-track layer, that's usually a signal the work belongs in `/run-plan-workflow` instead.

## Related skills

- `run-plan-workflow` — the ephemeral dev/review/test pipeline. Escape hatch for work too large or too isolated for fast-track. Read that skill's own "When to use" before invoking — it's stricter now.
- `deploy-hive` — the Hive platform deploy procedure. Invoke as a sub-step for any plan touching `AgentStudio2/`, `McpBridge/src/`, or `RemoteAgent/`.
- `handle-coderabbit-feedback` — the CodeRabbit cleanup loop. Run this directly (you are the dev) when CR comes back with findings on a fast-track PR.
- `manage-scope-creep` — invoke at the first spiral signal (more items being added than resolved, CR loop not converging, scope drifting from the Fix design).
