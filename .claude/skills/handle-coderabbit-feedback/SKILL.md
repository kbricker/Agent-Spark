---
name: handle-coderabbit-feedback
description: Autonomous CodeRabbit review-response loop on an open PR — fix → push (auto-triggers review) → read verdict → loop, with minimal @coderabbitai chatter (quota). Includes rate-limit retry + terminal-signal recognition.
---

# Handle CodeRabbit Feedback

Once Kyle has given functional approval on a PR ("functionally ready", "go ahead and merge", etc.), the orchestrator owns the CodeRabbit cleanup loop end-to-end. Kyle should not have to nudge each iteration.

## When to use this skill

Kyle says "handle rabbit", "work the rabbit loop", "the PR is functionally ready", "go ahead and merge after rabbit", or otherwise gives functional approval on a PR that still needs automated review cleanup. Also use as a sub-step of `/run-plan-workflow` Phase 1.75 or `/fast-track-plan` when CodeRabbit findings arrive.

## Important — CR auto-triggers on every push

**CodeRabbit automatically runs a review on PR creation and on every commit pushed to an open PR.** You do NOT need to manually `@coderabbitai full review` after a dev push — that just creates a redundant review run against the same HEAD.

Only use `@coderabbitai full review` when there is NO new commit but you want CR to re-evaluate the existing state (e.g., after posting reply comments you want CR to see, or after an external change that CR missed). The 99% case is "dev pushes a commit → CR auto-reviews it → you read the new review."

**Ordering gotcha:** if you post `@coderabbitai full review` in the same moment dev is pushing, CR may run against the old HEAD before the new commit lands. If the review's "reviewing between X and Y" commit hash doesn't match the latest HEAD, it's a stale run — wait for the auto-triggered run from the push to arrive, or explicitly re-trigger after confirming the push is visible on origin.

## The loop

Repeat until CodeRabbit comes back clean, then merge.

1. **Read the latest CR review.** CR publishes automatically after each push. Watch for the channel event. When the event arrives, read the message carefully — classify it against the signal table below before acting.
2. **Distinguish actionable from informational.** Focus on actionable findings and nits you decide to absorb. Apply `manage-scope-creep` sift to anything adjacent-but-outside the diff.
3. **Fix or push back.**
   - If findings are correct: dispatch the dev agent (already alive from `run-plan-workflow`) with a concrete briefing. Dev fixes, runs tests, commits, **pushes — that push automatically triggers CR pass N+1**. For fast-track plans, the orchestrator fixes directly.
   - **ONE PUSH PER REVIEW CYCLE. This is a hard rule, not a preference.** When a review arrives, fix EVERY finding in it, run the internal pass (step 3.5), fix what that finds too — then push ONCE. Never push per finding, per finding-cluster, or "while you think about the rest". Findings that arrive mid-triage join the same push.
     - Why it is stated this hard: the previous wording said "piggyback the fix-push *when possible*, only push standalone when the PR is merge-blocked" — which never fires on the common case (a PR whose only remaining work IS the CR fixes) and whose escape clause explicitly licensed a standalone push exactly when the loop is hottest. On wfa2#119 that guidance permitted three pushes in twenty minutes, consumed the entire fleet-wide hourly allowance on ONE PR, and stalled the merge behind a 30-minute cooldown. The cost is per-cycle; guidance that reasons per-push cannot see it.
     - The push cadence sets the review cadence. Every push is a review run, so pushing three times means asking for three reviews whether or not you wanted them.
   - If a finding is wrong or a bad-taste suggestion: explain why rather than dismissing silently — but **batch the pushbacks into ONE PR comment covering every declined finding**, not one reply per thread. Reply comments appear to consume runs too (wfa2#119 measured five runs against four pushes), and a reply-per-finding turns one disagreement into several.
   - If a finding is a genuine architectural disagreement you can't resolve: surface to Kyle.
4. **Run the internal adversarial pass on the FIX BATCH before pushing it** — not only on the original diff. `fast-track-plan` step 5.5 mandates this before the first push; it applies to every subsequent fix batch too, and this is the highest-leverage rule in this skill.
   - Fix commits are where review attention is lowest and stakes are often highest (they touch error paths, rollback, ordering). On wfa2#119, three fix batches were pushed without an internal pass and CR found defects in two of them, each costing a full round-trip; the one batch that DID get an internal pass first had two findings caught before they ever reached CR.
   - Internal passes cost **zero** CR quota, share the prompt cache, and return in minutes. A finding caught internally is a CR cycle you never spend.
   - Watch specifically for **the sibling you didn't fix**: wfa2#119 twice had a fix applied at the reported site while the identical defect sat untouched in a parallel code path a few lines away. When you fix a finding, grep for its shape elsewhere before pushing.
5. **Do NOT post `@coderabbitai resolve` routinely.** CR marks its own comments addressed on the next review pass (you'll see `(edited)` inline-comment events) — the command is redundant chatter that costs quota and triggers a reply. Only post it when stale threads genuinely linger after a clean review AND the PR is about to merge. (Per Kyle 2026-07-11, plan #581: "learn to not be so chatty with CR".)
6. **Wait for the auto-triggered next review from the push.** Do NOT also post `@coderabbitai full review` — duplicate review against the same HEAD. Just watch for the event.
7. **Loop back to step 1.** Every iteration should reduce the finding count. If it doesn't (fighting in circles), stop and ask Kyle.
8. **Exit condition: clean review** (see the signal table below). At that point, merge the PR.

## The review budget — count runs, not just findings

**Target: 3 CR runs per PR.** One on open, plus at most two fix cycles. That is the whole budget, because the nominal Pro allowance is 5 reviews/hour **pooled across the entire fleet** (every agent authors as `kyle-wf`), and adaptive fair-usage cuts it further — CodeRabbit told us on 2026-08-02 that our activity sits in the *95th percentile or higher* of all its users. One PR spending five runs is one PR spending everyone's hour.

- **Before any push to a PR that has already had 2+ reviews**, post `@coderabbitai rate limit` — it returns current status and **does not consume a run**. Check the budget before spending it.
- **Reaching run 4 is a signal, not a milestone.** It means the diff was not ready when it was first pushed. Stop, run the internal pass to convergence, and ship the remainder as one batch — do not keep trading pushes for reviews.
- **A green CodeRabbit check is not necessarily a review.** A rate-limited PR shows the check as `pass` with the description `Review rate limited`. Read the description, not the tick — merging on that is merging on a check that never ran.
- **What the check state actually means** matters at merge time: `mergeStateStatus: CLEAN` reflects branch protection, not whether CR reviewed the latest commit. Verify the newest commit was actually covered.

## Guard against auto-pause as well as rate limits

These are different mechanisms and they need different responses — see `reference_coderabbit_rate_limits`. A **rate limit** names a wait and clears itself. An **auto-pause** names no time, never clears on its own, and silently stops reviewing pushes altogether so a branch accumulates unreviewed commits. Batching fixes into fewer pushes is the single defence that works against both.

## CR event signal table

When a channel event arrives carrying a CR message, classify it by matching the body against these patterns. This table is the skill's contract with the wfa2 webhook handler — if the message wording changes meaningfully, update here AND the handler.

| Signal | Body pattern | Meaning | Next action |
|---|---|---|---|
| **Clean review** | `No actionable comments were generated in the recent review.` | CR reviewed, found nothing actionable | Exit loop — merge |
| **Clean review (alt)** | `Actionable comments posted: 0` | Same, older phrasing | Exit loop — merge |
| **Findings review** | `Actionable comments posted: N` with N≥1 | CR posted N actionable items | Read findings via `gh pr view <n> --comments --repo <owner>/<repo>`, fix, push |
| **Inline-only review** | Literal text `(Empty review body — findings are inline. Run 'gh pr view ...' to fetch them.)` | CR review body is empty; findings are inline comments only | Fetch with the suggested `gh` command, treat as findings review |
| **Inline comment** | Message starts with `CodeRabbit inline comment` (may include `(edited)` suffix before `on **<repo>#<pr>**`) | Single inline code finding (new or updated — edits often mean "addressed" markers) | Part of an inline-only review; already covered by the parent review event, but useful as a per-finding prompt |
| **Terminal ack** | Body ends with `Resolving.` / `Resolving all open comments now.` / `[resolve]` | CR is acknowledging a resolve command; no new review coming for this HEAD | Treat as end-of-loop for this iteration; if no clean-review signal yet, verify via `gh pr view --comments` before merging |
| **Rate limit** | Contains `Rate limit exceeded` (relay emits it with the verbatim wait line when CR provided one — either `Please wait **N minutes and M seconds**` or the newer `Next review available in:** **N minutes**`) | CR is rate-limited; has specified a wait duration | Trigger the rate-limit retry sub-procedure below |
| **In-progress** | `Currently processing new changes` | CR is actively reviewing | Wait for the next event — this is a progress ping, not terminal |
| **Paused** | `Reviews paused` | CR has stopped reviewing this PR | Escalate to Kyle — the auto-loop can't continue without CR |

**Note (relay contract, plan #646):** the webhook handler sanitizes and classifies before dispatch — you receive clean signal-only messages, never raw CodeRabbit markup. Specifically: `Currently processing new changes` is filtered outright; review events relay only on `action=submitted` (no more submitted+edited double posts); a CR review body collapses to its `Actionable comments posted: N` line; walkthrough/banner comments with no signal content are suppressed entirely; rate-limit and paused comments arrive as the clean one-liners in the table above. HTML comments and `<details>` blocks never reach you — patterns that referenced them are retired.

## Rate-limit retry sub-procedure

**First check whether a retry is needed at all.** If the PR is not merge-blocked on the clean review (long-lived ticket branch, more slices coming), skip the retry entirely — the next work push auto-triggers a cumulative review that covers the rate-limited diff for free. Only retry when the PR is actually waiting to merge.

When the Rate limit signal arrives, the message will contain a wait line in one of two phrasings (CR changed format ~2026-07; the relay passes either through verbatim):

```text
Please wait **N minutes and M seconds** before requesting another review.
**Next review available in:** **N minutes**
```

Steps:

1. **Parse the duration.** Try legacy regex `Please wait \*\*(\d+) minutes? and (\d+) seconds?\*\*` → `N*60 + M` seconds; else `Next review available in:\*\*\s*\*\*(\d+) minutes?` → `N*60` seconds. If neither matches, default to 15 minutes and note it.
2. **Track retry count.** Keep a mental counter for this PR's rate-limit hits (from TaskCreate metadata, a skill-local variable, or just conversation state). Cap at **3 attempts**. On the 4th rate-limit for the same PR, escalate to Kyle — something is structurally wrong (too many commits, quota exhausted for the hour, org config).
3. **Schedule a wake-up.** `ScheduleWakeup delaySeconds=<total_seconds + 30>, reason="CR rate-limited on PR #<n>, retry after wait"`. The +30s is slack to avoid racing the rate-limit window.
4. **On wake-up:** post `@coderabbitai review` on the PR (this one IS a manual trigger — there's no new commit, so CR won't auto-review; plain `review` is incremental and cheaper than `full review`, and it's the command CR's own limit message names). Wait for the next event.
5. **If the retry also rate-limits:** increment the counter and repeat from step 1.
6. **If the retry succeeds:** reset the counter and resume the normal loop.

**Why the +30s:** CR's limits are adaptive fair-usage (rolling window; reviews free up as earlier ones age out — see `reference_coderabbit_rate_limits`). The wait line states time until the next review becomes available. A few seconds of slack avoids the edge case where we retrigger just before the window frees and get rate-limited again.

## When to spawn a fix agent vs patch inline

- **Inline (orchestrator directly):** small finding, 1-3 line tweak, obvious fix, fast-track plan.
- **Dev agent (already persistent on this plan):** anything that requires repo context — renames, refactors, multi-file changes, or anything where you'd have to read surrounding code to get right. Applies only to `/run-plan-workflow` (persistent agents). Fast-track orchestrators patch inline.

Do not spawn a NEW agent just for the rabbit loop. The dev agent from `/run-plan-workflow` is still alive for this reason — it already knows the codebase state.

## Fix all findings now — do not defer

Do not leave "low priority" findings for a follow-up PR to save review cost. You're already in the PR, CodeRabbit is already reviewing it, the dev agent is already running. The marginal cost of fixing a nit now is near zero; the cost of re-opening this PR later is real.

## When to stop the loop and ask Kyle

- CodeRabbit's suggestion conflicts with the intended architecture of the plan.
- Two consecutive iterations produced the same finding count (you're not making progress).
- A finding requires a call Kyle hasn't weighed in on yet (security tradeoff, API shape, etc.).
- Rabbit is suggesting something that would break a contract with another system.
- Rate-limit hits exhausted (3 retries already used on this PR).
- Paused signal arrived and the auto-loop can't proceed.

## After the loop is clean

Merge the PR. Move the plan back to the appropriate deploy/validate step (or straight to Completed if the plan is already validated). Don't leave the PR hanging after a clean review.

## Do not

- **Do not push more than once per review cycle.** The single most expensive habit available to you. See step 3.
- **Do not push a fix batch that no reviewer has seen.** Internal pass first, every time — it is free.
- Do not nag Kyle between iterations. Own the loop.
- Do not merge on a partially-reviewed PR hoping the remaining findings "don't matter".
- Do not argue with CodeRabbit in comment threads beyond a single clarifying reply. If it's still wrong on the next pass, surface to Kyle.
- Do not add a polling fallback. Per Kyle 2026-04-19 on plan #277 — the CR loop must stay event-driven. If webhooks are unreliable, fix the event subscription + handler, don't work around it.
