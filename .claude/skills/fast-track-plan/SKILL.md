---
name: fast-track-plan
description: The orchestration workflow, used on every plan. You play dev + review inline on the main thread and fan out to Agent/Task subagents for parallelizable work. Walks plan status through the gated state machine, runs the mandatory internal adversarial review, merges and deploys. There is no second pipeline — work too large for one context gets decomposed across subagents.
scope: global
---

# Fast-track Plan Workflow (default path)

This is the orchestration workflow. You play dev + review inline and fan out to Agent/Task subagents as needed. **There is no second path** — the separate-process pipeline that used to serve as an escape hatch was retired on 2026-08-16.

Per Kyle 2026-04-19: fast-track is the main track for every orchestrator. The pattern it replaced — spawning three separate agent processes on every plan — was overkill for the common case, broke cache sharing, and burned startup cost on most plans that didn't need it. See `feedback_fast_track_is_default` for the rule.

## When to use this skill

- A new plan has been filed and you're about to execute. This is the default starting point. Do not ask for fast-track authorization — Kyle's standing rule is fast-track by default.
- A follow-up or polish pass on something already shipped.
- A bug fix.
- A refactor that fits in your main thread's context budget.
- A cross-workspace config change (skills, memory, CLAUDE.md across orchestrators).

## When the plan is too big for one context

There is no other pipeline to escalate to, so the answer is always decomposition rather than delegation to a different mechanism:

- **Genuinely large — many files, many sub-areas.** Split it across subagents by sub-area and synthesise their reports yourself. You keep the design decisions; they do the lookup and the mechanical work.
- **Long-running browser or test work.** Give it to a subagent so the transcript stays out of your context, and ask for observed values rather than a verdict.
- **Architecturally risky.** That is what the step 5.5 adversarial pass is for, run with more lenses and more rounds — not a reason to reach for a different workflow.
- **Genuinely needs a second independent session** — Kyle asking for a review that is not yours, or work belonging to a project you do not own. That is a handoff to another *named* agent taking a ticket of its own, and it is Kyle's call, not yours: agents are bound to projects (Hive, VaEx, infra), so "who could do this" is a much shorter list than the roster and getting it wrong hands work to an agent with neither the repo nor the remit. Note this is a real handoff — it is NOT the same as the dispatch fast-track avoids in "Persistent agents and wake/sleep" below, which is about waking an agent mid-plan to do a piece of YOUR ticket.
  - Whichever agent takes it, the first thing you tell it is to check out the right branch; a long-lived clone sits wherever its last task left it.

If the work still doesn't fit, the plan is too big and wants forking — take that to Kyle rather than deciding it (`no-deferred-work`).

## Core procedure

### 1. Create the plan (if not already filed)

Use `hive_plan_create` with `fastTrack: true` by default. Full description, concrete Fix/Task/Validation checklist, Symptom + Fix design + Out-of-scope sections. Plans are load-bearing artifacts — future-you needs to be able to read the plan six months from now and understand what changed and why. See `feedback_plans_default_planning` — Planning status, never Backlog.

**Module selection:** valid modules are `Dashboard, Remote, Plans, Sessions, Bugs, Activity, Infra`. Orchestration plans → `Sessions`. There is no "Hive" module.

**Planning pre-conditions (from #624 review-catch mining, Kyle-approved 2026-07-22):** before moving past Planning, the plan description or checklist must answer three things — explicitly stating "none touched" counts as the answer:
1. **State lifecycle** — for each stateful surface touched (pooled object, cache, mode controller, serialized/numeric input): init / every reset path (incl. pool reuse, mode handoff) / teardown / value-domain constraints. See `feedback_plan_preconditions`.
2. **Async in-flight** — for each async flow: what if the world changed mid-flight, and what if it runs twice/overlaps? See `feedback_plan_preconditions`.
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
- **Workspace-config-only** (editing `.claude/` in any orchestrator workspace): direct-commit to each workspace's default branch (`master` for every one of them today — verify rather than assume; read `composition.json` for who exists). No PR flow, no CodeRabbit — these repos are local config stores, not code. Reference the plan number in each commit message.
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

Before the first push of any fast-track PR branch — the push that opens it to CodeRabbit, and regardless of whether you'll wait for CR — run an internal adversarial review on the complete outgoing diff (plan #650, Kyle 2026-07-24). Stage everything you intend to ship first (explicit `git add <path>` per step 5), then give the subagent `git diff <default>...HEAD` plus `git diff --cached`, and confirm via `git status` that no unstaged or untracked file you meant to include is missing from what it reviewed. No size exemption — trivial diffs still get the pass. Inline self-review alone does not hit the "rigor of a dedicated reviewer" bar — wfa2 PR #104 shipped a Major to CR (dedup filter silently dropping human review events, finding #112) that this pass is specifically built to catch.

- **Use several lenses in parallel, not one generalist.** Spawn 2-4 subagents with distinct briefs — e.g. correctness, contracts with consumers of the shared surface, and whatever format/serialization the change touches (prefab/YAML, migrations, schema). Field data from VaEx 682.18: the correctness and contract agents independently found the same Major from different directions, which is a strong confidence signal, and the format agent found the round's only Critical — one that neither of the others would have thought to look for. A single generalist reviewer is the cheap version of this step and it under-reads.
  - **Expect overlap between lenses, and read it as signal rather than waste.** Measured on 682.18: ~26 raised items collapsed to 13 logged findings, and the largest slice of that gap — 5 defects — was the *same* defect found independently by two lenses via different routes. That convergence is what lets you stop second-guessing whether a finding is real. Do not cut the lens count to reduce redundancy, and do not read a low logged-to-raised ratio as the reviewers being noisy. On that run there was zero style noise and zero invalid claims to reject; the rest of the gap was correctly-identified non-defects and two write-ups of one bug at different altitudes. Caveat on the sample: it was a UI/prefab-heavy diff, and a pure-logic diff may give reviewers more to have opinions about.
- **Five lenses worth naming explicitly, each mined from a real CodeRabbit finding on a protocol-shaped artifact** (evidence pass on 664.1, salvaged 2026-08-10). Be precise about why they earn their place: **not** because they beat the mandatory internal pass — five of the six cited PRs merged *before* that pass existed (it landed in wfa2 PR #105) — but because when they were first applied they blocked their own introducing diff, 1 critical + 13 major + 6 minor, including three defects in that plan's own use of them. (Counts are findings-store ids 170–189, queried; 664.1's own prose says 12 major and is wrong — which is itself the lesson, since verifying a claim beats copying it.) These are not a replacement for the parallel-lens structure above — they are the classes this review demonstrably misses when nobody names them:
  - **crash-consistency / interruption** — what if we crash, are killed, or are interrupted between step A and step B? Does a partial sequence replay, double-apply, or lose data? (wfa2 PR #106 read-before-move let a crash replay the handoff; wfa2 PR #106 plain `mv` could silently clobber an existing journal entry; wfa2 PR #97 seed resume inferred progress from a total count and dropped entries.)
  - **spec self-contradiction** — does the artifact contradict itself, its own stated API limits, or the memory/skill carrying the same rule elsewhere? (wfa2 PR #97 skill said "one call per review" against a 50-item API cap; wfa2 PR #98 `linkedPlanId` guidance contradicted the append-only rule two lines below it, in *both* the skill and the canonical memory; wfa2 PR #103 a closing sentence restated the unscoped rule the same amendment had just scoped.)
  - **terminal-case omission** — does every wait, loop, and await name its failure exit? (wfa2 PR #101 guidance said wait for `agent_idle`, but a crashed agent never emits it — an orchestrator following the memory verbatim waits forever.)
  - **provenance-as-operand** — is a citation, example, or plan number hard-coded somewhere it will later be read as the operand? Deadly in reusable templates. (wfa2 PR #98 hard-coded plan `#629` in the reusable dev *and* review CLAUDE.md templates; every future assignment would have consulted the wrong plan's shaping log.) Note the two namespaces this bullet is about: a bare `#N` in fleet prose is ambiguous between a plan id and a PR number, so write `wfa2 PR #106` or the plan's dotted display number.
  - **scope-exceedance** — does any condition apply more broadly than the stated intent? (wfa2 PR #104 a submitted-only filter meant for CodeRabbit dedup was applied to *all* reviewers, silently dropping human review events.)
- Brief each subagent to REFUTE the diff: hunt scope-exceeding behavior changes (does any condition apply more broadly than the stated intent?), edge cases, contract breaks with consumers of the touched surface, and state/async gaps. Give it the plan's Fix design as the stated intent and the full diff. Three brief rules that keep signal high. Require every finding to come with a **concrete failure scenario**. Anything that can't be backed by one goes in a clearly-labelled **observations section rather than being silently dropped** — the substantiation bar is deliberately strong, and without this escape valve a real-but-hard-to-prove concern gets discarded instead of surfaced; on 682.18 a TMP font/material atlas issue reached the orchestrator that way and turned out to matter. And tell them to **verify claims made in commit messages and comments rather than take them at face value**. On 682.18 that last rule caught a commit claiming "Navigation set to None" where the serialized value was `4` (`Explicit`); `None` is `0`. The reviewer only caught it by going and reading the enum.
- Fix its valid findings before pushing; consciously skip invalid ones. Then **re-stage the fixed paths** (`git add` — fixes land in the working tree, and an unstaged fix would leave the rerun reviewing the pre-fix index) and re-run the pass on the post-fix diff (continuing the same subagent via SendMessage is fine — it has context); loop restage → rerun until it reports no new valid findings. Log survivors (fixed AND skipped) to the findings store at review settle — batching with the CR findings in one `/log-review-findings` call is fine.
- **The loop is not a formality — it is where much of the value is.** Read this as a hard requirement, not a tidy-up. On VaEx 682.18 the pass ran three rounds and every round found something. Rounds 2 and 3 found defects introduced **entirely by the fixes for round 1**: a fix that was a silent no-op *and* added a keyboard-navigation dead end, state parked in `Awake` instead of `OnEnable` so a panel rode into the next round, a new demo-HUD mirror that could resurrect a panel over the combat HUD, and a freshly-added gate that checked location but not round state — reopening the exact path round 1 had closed. Stopping after one round would have shipped three of them. A fix that does nothing while reading as done in the commit log is a nastier outcome than the original bug, because everything downstream treats it as handled.
- Why this pays: the subagent shares your prompt cache (cheap, fast), its catches cost zero CR review-run quota, and every pre-push catch saves a full CR round-trip (push → review → fix → push → re-review).
- **Config-repo direct commits still get this pass.** Having no PR is a property of the *transport* — CodeRabbit is not wired to these repos — and not a review exemption. A skill, hook or memory that programs agent behaviour is code executed by an LLM rather than a CPU, and it reaches the whole fleet.
  - **This flow needs its own trigger and its own diff expression**, because the ones at the top of 5.5 assume a PR-opening push and silently produce nothing here. Trigger: **before `git push`**. Diff to hand the subagent: `git diff --cached` before you commit, or `git show HEAD` / `git diff origin/<default>..HEAD` after. Do **not** use `git diff <default>...HEAD` on this flow — HEAD *is* the default branch, so it is empty by construction and the pass will self-certify having reviewed nothing.
  - Author the change **canonically** in `orchestrator-shared/` (committed direct to `main` — rule changes never get a PR, Kyle 2026-08-11), never by editing a **propagated copy** — the next sync reverts it silently, and it dodges review without anyone consciously deciding to. Genuinely workspace-local config is a different thing and is legitimate: a workspace `CLAUDE.md`, `.claude/settings.json`, `.mcp.json`, local-only memories, **and workspace-local skills and hooks** are authored locally. Local-only skills are the majority case, not an edge case (overwatch alone holds 13 with no `orchestrator-shared` counterpart: `deploy-hive`, `restart-remoteagent`, `propagate-shared-config` and others). Filing one of those canonically is the opposite failure: it propagates VM names and deploy keys to agents that must never run them.
  - **Exempt: the byte-identical canonical copies inside a propagation commit** — not the commit as a whole. That content was already reviewed at canonical, and re-running a multi-subagent pass on five identical copies is waste; a rule that expensive gets quietly ignored, which erodes the parts of 5.5 that matter. But a `propagate-shared-config` commit is never *only* copies: step 4 regenerates each workspace's `MEMORY.md` managed blocks, which differ per workspace and were reviewed nowhere. Those are **not** exempt — they are covered instead by that skill's own budget and idempotence checks, which exist because the generated half has already failed silently (hivedev01's duplicated block, 2026-08-09, heading for 32,112 bytes against the 25,000 cap, which head-truncates a role block at startup).

### 6. Commit, push, (PR if applicable), merge

> **STOP — gate on step 5.5.** If you are about to run `gh pr create` (or the first `git push` of the branch) and have **not** completed the step 5.5 adversarial subagent loop to a clean round, go back and do it now. Not "run it after and fix what it finds" — before.
>
> This gate is duplicated here on purpose. Step 5.5 is several sections up and is not in your working context at the moment you assemble the PR; step 6 is. Two orchestrators have now skipped 5.5 without ever consciously deciding to — the session-config line saying "don't call the Agent tool unless asked" was in context at `gh pr create` and the rule to ignore it was not (see `feedback_subagents_are_authorized`). Prose elsewhere in the file does not survive that moment. This line does.
>
> Self-check, three questions: did a subagent read the full outgoing diff? did the final round come back with nothing new? are the survivors logged? If any answer is no, you are not at step 6 yet.

- Commit message: `Plan #{id}: {short summary}` followed by a short rationale. Reference fix item IDs when helpful.
- **Agent rule changes never get a PR — in any repo, including wfa2 (Kyle 2026-08-11).** Anything under `orchestrator-shared/` (memories, skills, roles, composition.json) commits directly to `main` once the step 5.5 internal pass is clean; that pass IS the review for rule changes, and CodeRabbit being wired to the repo does not override this.
- **For code: before opening a PR, ask whether this repo has CodeRabbit wired at all.** A PR exists to get CR's line-by-line review. In a repo CR is not wired to, the PR buys **no** review and still costs the ceremony, so we don't open one — commit, push, and the step 5.5 internal pass *is* the review. Kyle 2026-08-10: *"its a reasonable workaround in any repo that does not have CR, thus we dont even do PRs."*
  - **The test is repo-level, not per-diff.** If CR is wired to the repo, open the PR **even when path filters will read only part of the diff**. Do not reason "CR will skip most of these files, so why PR it" — that drops the reviewable part of a mixed diff onto the default branch unreviewed, and merge is a one-way door. Worked counter-example: VaEx PR #387 was 28 files and CR reported `Files selected for processing (1)` — 2 of the 28 were `.cs`, and CR read only one of them. Note what that shows: opening the PR got *some* code reviewed where skipping it would have got none, **and** a `.cs` file was still silently dropped. So opening the PR is necessary, not sufficient — always compare `Files selected for processing (N)` against the PR's real file count, which the retrieved note `reference_coderabbit_path_filters_skip_silently` (hive_recall it) calls the only reliable signal. The pure-asset case in VaEx has its own rule with its own extension list in `feedback_content_branches_no_pr` (vaex-dev role); it is a **purity** test — pure assets push only, code+assets mixed still gets a PR — and it does not generalise past that.
  - **How to actually answer it**, because "is CR wired here?" is knowledge you may not have — and the agents on CR-less repos are exactly the ones whose role bundle never told them so. Probe at the **repo** level: `gh pr list --state all --limit 5`, then check whether CodeRabbit has commented on any of them. Present on a recent PR → wired. **Absent is only an answer if there were several real PRs to check** — a repo with one or two PRs, or whose PRs all predate a possible CR install, gives you *doubt*, not a verdict. Do not let the probe manufacture false certainty; fall through to the default below.
  - **When in doubt, open the PR.** A wasted run is recoverable; an unreviewed merge is not.
  - **If you opened a PR and CodeRabbit never comments, that does NOT authorise merging.** The next bullet's "wait for CodeRabbit" default assumes CR exists, and silence has three causes that look identical on one PR: not wired, **auto-paused**, and rate-limited. Auto-pause is the trap — the retrieved note `reference_coderabbit_rate_limits` (hive_recall it) records that pushes then trigger *nothing*, it names no time, it never clears on its own, and one comment (`@coderabbitai resume`) recovers it. So after a reasonable wait (CR normally replies in minutes; observed waits run to 15–33 minutes), go back to the **repo-level** probe: if other recent PRs do have CR comments, yours is paused or limited — `@coderabbitai resume` for a pause, and for an expired rate-limit window `@coderabbitai review` or a push (an expired limit re-runs nothing by itself); do not conclude "not wired" and do not merge. If the repo genuinely has no CR, say so plainly and take it to Kyle. `feedback_never_skip_review` (pr-workflow role) still governs any PR that exists: CR review, findings addressed, Kyle approves. This escape bounds the *wait*, never the *review*.
  - Note also that the question is whether to open a PR, **not** whether to "skip CR" — CR auto-runs on PR creation and every push, so once a PR exists the run is already spent.
- For single-target PR flow: push the branch, `gh pr create` with detailed body + test plan, wait for CodeRabbit (default is to wait — only skip when Kyle says "don't wait for rabbit"), merge with `gh pr merge {n} --merge --delete-branch`. Never `--squash`.
- For config-repo direct flow (the work was done **directly on the default branch**): commit, `git push`, done.
- For no-PR branch flow — keyed on a **deliberate decision not to open a PR**, for one of exactly these three reasons: the repo has no CR, *or* it is a pure-asset content branch under `feedback_content_branches_no_pr` (vaex-dev role), *or* Kyle said not to PR it. Broader than "repo has no CR", because VaEx content branches are the fleet's most common no-PR branch and VaEx *does* have CR — key it to that alone and the most frequent case matches no flow at all. **But the key is the decision, not the state.** If you meant to open a PR and `gh pr create` failed — missing template, no upstream, auth hiccup — you are not in this flow, however much "no PR exists" describes your situation. Fix the failure and open the PR; do not let a mechanical error route a reviewable diff onto the default branch. **Land it in the same session** — `git merge --no-ff` into the default branch and push. A pushed branch with no PR and no merge is **not** a deliverable and there is nothing downstream to remind anyone it exists. 664.1's branch was pushed deliberately with no PR, sat unmerged for 16 days with its plan stuck, and was ultimately cancelled and the branch deleted. If you genuinely intend to park a branch rather than land it, say so explicitly to Kyle rather than letting silence decide.

> **STATUS GATE — the moment the PR exists, move the ticket:** `hive_plan_update({id, status: "CodeReview", prUrl, gitBranch})`. Do it in the same breath as `gh pr create`, not after CR replies. A plan sitting in Development with a live PR is the second most common stall we measured.
>
> **On a no-PR deliverable there is no such moment**, and that is exactly how these plans stall. Move the ticket on the **merge** instead of on a PR that will never exist. Which field to set depends on what shipped, and one case has no clean answer yet:
>
> - **Non-code** (research, spec, docs, ops): set `deliverableType` — `spec` | `doc` | `ops`. Plan #614 made this the supported way to complete with no `prUrl`.
> - **Code merged without a PR:** point `prUrl` at the **merge commit**. That is an honest record of where the work landed, not the fabricated placeholder #614 exists to eliminate, and it is already what TendWright does. Do **not** reach for `ops` to unstick a code plan — `deliverableType` splits into PR-backed code and non-code, has no value meaning "code merged without a PR", and `DeliverableTypes.IsPrLess` fails closed by design, so guessing makes the board lie about what shipped. The missing value is a real gap, open with Kyle and logged on #614; if you hit it, say so rather than picking whichever value gets you moving.

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

Fast-track is inline by default, but you can and should spawn Agent/Task subagents for parallelizable work. The subagent model shares the prompt cache with you and returns a summary — so it's strictly cheaper and faster than dispatching to a separate agent for independent sub-work.

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

Subagents spawned during active main-thread work read from the warm prompt cache (~5-minute TTL). That is a real cost and speed win, and it is the reason fan-out is cheap here: dispatching to a separate agent process instead means zero cache sharing plus a real startup cost (clone, init, first-message context build). Fan out parallel sub-work aggressively — the cache is there, use it.

### Subagent prompt discipline

**Name the branch in every brief.** A subagent inherits whatever your clone has checked out, or gets a fresh worktree that your checkout never reaches — either way it can land commits off the plan branch, and no handoff message exists for anyone to notice. This is restated here rather than left to memory because this is the moment it applies. Carry the `no-new-deps` and `no-deferred-work` gates into the brief for the same reason: a subagent loads neither skill.

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
- **Chaining subagent summaries into a substitute for understanding.** Fan-out is for work whose *results* you can verify, not for holding a design you never formed. If the plan is too big for your main thread even decomposed, it wants forking — see "When the plan is too big for one context".
- **Leaving subagent results un-verified.** A subagent's report describes what it intended to do, not necessarily what it did. Before acting on a subagent's claim, verify — especially for file writes.

## Gotchas

- **Status transitions are sequential.** `Planning → Completed` in one call fails. Walk through every state.
- **fastTrack skips dashboard-only gates, not agent-required gates.** You still need `assignedAgent` + `reviewAgent` set.
- **Module must be valid.** `Sessions` for orchestration; "Hive" is not a module.
- **Don't pre-bump a version with a dirty working tree.** Check `git diff` on the csproj first.
- **You are still the reviewer.** Self-review your diff with the same rigor a dedicated reviewer would — edge cases, regressions, things you'd flag if someone else wrote it. Self-review does NOT replace step 5.5 — the adversarial subagent pass before the first CR push is mandatory.
- **CodeRabbit may run late.** If you merge before CR finishes, the review is harmless against a closed PR — but if it surfaces real findings, open a small follow-up PR rather than ignoring.
- **Pre-existing drift in workspace repos is common.** Always commit by explicit path — never `git add -A`.

## Do not

- Do not skip the checklist on plans you close. The checklist is the receipt.
- Do not fake a Completed status when the work isn't done. `fastTrack` is not a shortcut to skip real review — it's a different-shaped workflow with the same rigor.
- Do not skip deploy on server-side changes. "It's in main" is not "it's live".
- Do not fan out work that has sequential dependencies or shared-state edits. See the anti-patterns section.
- Do not delegate synthesis or design decisions to subagents. You do the thinking; subagents do the lookup/execution.

## Persistent agents and wake/sleep

Fast-track runs inline on the orchestrator's main thread and via Agent/Task subagents — it does **not** dispatch to persistent named agents in its own flow. Per plan #280, remote-class persistent agents (today that is **forge** — vaexdev3/vaexserverdev were retired 2026-08-07 per Kyle, deactivated and hidden, to be rebuilt properly when task volume warrants) boot Offline (`AutoSpinDown: true`) and require an explicit `hive_agent_wake` to come up. **Virtual orchestrators (vaexdev2, spark, ...) are NOT wake targets** — the server refuses a cold-start wake on them (plan 782.10; a wake on an already-running virtual returns a harmless no-op); they come up via their workspace launch script, and you reach a running one with `hive_send_message`.

When fast-track delegates to a sub-skill that does touch a persistent agent, the wake/sleep wrap is that sub-skill's responsibility, not yours. Today only one sub-skill dispatches to a remote-class agent: **`/deploy-hive`** wakes forge as its step 0 and sleeps it as its final step.

You should not pre-wake a persistent agent inside fast-track on the assumption it'll be needed — wake/sleep has a measurable cost (process spin-up, clone re-attach), so leave it to the sub-skill that actually dispatches. If you find yourself reaching for `hive_agent_wake` at the fast-track layer, that is the signal the work is really a separate ticket for that agent — take it to Kyle. And if a handoff is agreed, a remote-class agent must be WOKEN before it can receive anything: messaging an Offline agent is a reply that never arrives.

## Related skills

- `deploy-hive` — the Hive platform deploy procedure. Invoke as a sub-step for any plan touching `AgentStudio2/`, `McpBridge/src/`, or `RemoteAgent/`.
- `handle-coderabbit-feedback` — the CodeRabbit cleanup loop. Run this directly (you are the dev) when CR comes back with findings on a fast-track PR.
- `manage-scope-creep` — invoke at the first spiral signal (more items being added than resolved, CR loop not converging, scope drifting from the Fix design).
