---
name: fast-track-plan
description: The DEFAULT orchestration workflow. Overwatch plays dev + review inline on the main thread and fans out to Agent/Task subagents for parallelizable work. Walks plan status through the gated state machine, merges and deploys. Use on almost every plan. Use `run-plan-workflow` only as the escape hatch for genuinely large / risky / long-running-test work.
scope: global
---

# Fast-track Plan Workflow (default path)

This is the default orchestration workflow. Overwatch plays dev + review inline and fans out to Agent/Task subagents as-needed. Ephemeral dev/review/test agents via `run-plan-workflow` are the **escape hatch** for work this skill can't handle cleanly — not the default entry point.

Per Kyle 2026-04-19: fast-track is the main track for all three virtual orchestrators (overwatch, verletDev, vaexdev). The old pattern — spawning three ephemerals on every plan — was overkill for the common case, broke cache sharing, and burned startup cost on most plans that didn't need it. See `feedback_fast_track_is_default` for the rule.

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

### 2. Assign yourself as both agents

Required before the status can move past Planning:

```
hive_plan_update({id, assignedAgent: "overwatch", reviewAgent: "overwatch"})
```

`fastTrack: true` skips dashboard-approval gates, NOT agent-required gates. Both assignment fields must be set.

### 3. Decide: single-repo or multi-repo?

- **Single target repo** (wfa2 is the common case): standard branch + PR + merge flow, covered below.
- **Workspace-config-only** (editing `.claude/` in overwatch and/or verletDev and/or vaexdev): direct-commit to each workspace's default branch (`master` for overwatch + vaexdev, `main` for verletDev). No PR flow, no CodeRabbit — these repos are local config stores, not code. Reference the plan number in each commit message.
- **Mixed** (e.g. wfa2 + workspace changes): wfa2 gets the PR flow; workspace repos get direct commits. Reference the same plan number across all.

### 4. Do the work

- Start from fresh default branch: `git checkout <default> && git pull origin <default>`
- For single-target-repo plans, create a feature branch: `git checkout -b plan{id}/short-slug`
- For config-repo plans, commit to default branch directly
- Edit per the plan's Fix design
- Build if server-side (`"$USERPROFILE/.dotnet/dotnet.exe" build ...`)
- For UI changes, verify in a dev server / loaded dashboard before committing

**Fan out here when it helps.** See the "Fan-out pattern" section below.

### 5. Check for pre-existing uncommitted drift

Before every commit, run `git status` and `git diff` to see what's dirty. Pre-existing uncommitted state is common across orchestrator workspaces — do NOT sweep it into your commit. Use explicit `git add <path>` on only the files you touched. If the plan includes a version bump and the csproj is already dirty-ahead-of-main, fold the existing bump into your commit so git main stays monotonically ahead of what's deployed. See the gotcha on 2026-04-13, plan #178.

### 6. Commit, push, (PR if applicable), merge

- Commit message: `Plan #{id}: {short summary}` followed by a short rationale. Reference fix item IDs when helpful.
- For single-target PR flow: push the branch, `gh pr create` with detailed body + test plan, wait for CodeRabbit (default is to wait — only skip when Kyle says "don't wait for rabbit"), merge with `gh pr merge {n} --merge --delete-branch`. Never `--squash`.
- For config-repo direct flow: commit directly to default branch, `git push`, done.

### 7. Deploy (if applicable)

- If the plan touches `AgentStudio2/` / `McpBridge/src/` / `RemoteAgent/`: invoke `/deploy-hive` as a sub-step.
- If the plan only touches orchestrator workspace config (`.claude/`): no deploy. The local `git pull` in each workspace (or you're already in it) picks up the change.
- If it touches wfa2 hooks/scripts used by orchestrators: message affected orchestrators to `git pull` in `C:/Projects/wfa2`.

### 8. Walk plan status through the gated machine

**Sequential, one step at a time, no skipping:** `Planning → Review → Ready → Development → CodeReview → Completed`.

```
hive_plan_update({id, status: "Review"})       // after assignments set
hive_plan_update({id, status: "Ready"})
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
- **You are still the reviewer.** Self-review your diff with the same rigor a review ephemeral would — edge cases, regressions, things you'd flag if someone else wrote it.
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

Fast-track runs inline on the orchestrator's main thread and via Agent/Task subagents — it does **not** dispatch to persistent named agents (vaexdev2, vaexdev3, vaexserverdev, forge) in its own flow. Per plan #280 those agents now boot Offline (`AutoSpinDown: true`) and require an explicit `hive_agent_wake` to come up.

When fast-track delegates to a sub-skill that does touch a persistent agent, the wake/sleep wrap is that sub-skill's responsibility, not yours:

- **`/deploy-hive`** wakes forge as its step 0 and sleeps it as its final step.
- **`/run-plan-workflow`** wakes the assigned dev agent (vaexdev2 / vaexdev3 / vaexserverdev / forge) before dispatch and sleeps it after the work is committed.

You should not pre-wake a persistent agent inside fast-track on the assumption it'll be needed — wake/sleep has a measurable cost (process spin-up, clone re-attach), so leave it to the sub-skill that actually dispatches. If you find yourself reaching for `hive_agent_wake` at the fast-track layer, that's usually a signal the work belongs in `/run-plan-workflow` instead.

## Related skills

- `run-plan-workflow` — the ephemeral dev/review/test pipeline. Escape hatch for work too large or too isolated for fast-track. Read that skill's own "When to use" before invoking — it's stricter now.
- `deploy-hive` — the Hive platform deploy procedure. Invoke as a sub-step for any plan touching `AgentStudio2/`, `McpBridge/src/`, or `RemoteAgent/`.
- `handle-coderabbit-feedback` — the CodeRabbit cleanup loop. Run this directly (you are the dev) when CR comes back with findings on a fast-track PR.
- `manage-scope-creep` — invoke at the first spiral signal (more items being added than resolved, CR loop not converging, scope drifting from the Fix design).
