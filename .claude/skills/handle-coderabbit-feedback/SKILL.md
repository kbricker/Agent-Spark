---
name: handle-coderabbit-feedback
description: Autonomous CodeRabbit review-response loop on an open PR — fix → push (auto-triggers review) → resolve old threads → read verdict → loop. Includes rate-limit retry + terminal-signal recognition.
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
   - If a finding is wrong or a bad-taste suggestion: leave a reply on the comment explaining why, don't dismiss silently. CR's next pass will see the reply.
   - If a finding is a genuine architectural disagreement you can't resolve: surface to Kyle.
4. **After the push, resolve stale threads.** Post `@coderabbitai resolve` on the PR. This clears old thread state so the next auto-review starts clean. This is the ONLY manual `@coderabbitai` command you normally need.
5. **Wait for the auto-triggered next review from the push.** Do NOT also post `@coderabbitai full review` — duplicate review against the same HEAD. Just watch for the event.
6. **Loop back to step 1.** Every iteration should reduce the finding count. If it doesn't (fighting in circles), stop and ask Kyle.
7. **Exit condition: clean review** (see the signal table below). At that point, merge the PR.

## CR event signal table

When a channel event arrives carrying a CR message, classify it by matching the body against these patterns. This table is the skill's contract with the wfa2 webhook handler — if the message wording changes meaningfully, update here AND the handler.

| Signal | Body pattern | Meaning | Next action |
|---|---|---|---|
| **Clean review** | `No actionable comments were generated in the recent review.` | CR reviewed, found nothing actionable | Exit loop — merge |
| **Clean review (alt)** | `Actionable comments posted: 0` | Same, older phrasing | Exit loop — merge |
| **Findings review** | `Actionable comments posted: N` with N≥1 | CR posted N actionable items | Read findings via `gh pr view <n> --comments --repo <owner>/<repo>`, fix, push |
| **Inline-only review** | Literal text `(Empty review body — findings are inline. Run 'gh pr view ...' to fetch them.)` | CR review body is empty; findings are inline comments only | Fetch with the suggested `gh` command, treat as findings review |
| **Inline comment** | Message starts with `CodeRabbit inline comment` (may include `(edited)` suffix before `on **<repo>#<pr>**`) | Single inline code finding (new or updated — edits often mean "addressed" markers) | Part of an inline-only review; already covered by the parent review event, but useful as a per-finding prompt |
| **Terminal ack** | Body ends with `Resolving.` / `Resolving all open comments now.` / `[resolve]` / `<!-- <review_comment_addressed> -->` | CR is acknowledging a resolve command; no new review coming for this HEAD | Treat as end-of-loop for this iteration; if no clean-review signal yet, verify via `gh pr view --comments` before merging |
| **Rate limit** | Contains `<!-- This is an auto-generated comment: rate limited by coderabbit.ai -->` AND `## Rate limit exceeded` | CR is rate-limited; has specified a wait duration | Trigger the rate-limit retry sub-procedure below |
| **In-progress** | `Currently processing new changes` | CR is actively reviewing | Wait for the next event — this is a progress ping, not terminal |
| **Paused** | `Reviews paused` or `[!NOTE] Reviews paused` | CR has stopped reviewing this PR | Escalate to Kyle — the auto-loop can't continue without CR |

**Note:** The webhook handler filters out the `Currently processing new changes` pattern before dispatch, so you won't see those events in your channel. Everything else reaches you.

## Rate-limit retry sub-procedure

When the Rate limit signal arrives, the message will contain text like:

```text
Please wait **N minutes and M seconds** before requesting another review.
```

Steps:

1. **Parse the duration.** Regex: `Please wait \*\*(\d+) minutes? and (\d+) seconds?\*\* before requesting another review`. Convert to total seconds: `N*60 + M`.
2. **Track retry count.** Keep a mental counter for this PR's rate-limit hits (from TaskCreate metadata, a skill-local variable, or just conversation state). Cap at **3 attempts**. On the 4th rate-limit for the same PR, escalate to Kyle — something is structurally wrong (too many commits, quota exhausted for the hour, org config).
3. **Schedule a wake-up.** `ScheduleWakeup delaySeconds=<total_seconds + 30>, reason="CR rate-limited on PR #<n>, retry after wait"`. The +30s is slack to avoid racing the rate-limit window.
4. **On wake-up:** post `@coderabbitai full review` on the PR (this one IS a manual trigger — there's no new commit, so CR won't auto-review). Wait for the next event.
5. **If the retry also rate-limits:** increment the counter and repeat from step 1.
6. **If the retry succeeds:** reset the counter and resume the normal loop.

**Why the +30s:** CR's rate-limit window is hourly (confirmed: per-user commit cap per hour). The message says "wait N minutes and M seconds" — that's the time until the hour-rollover for the oldest commit in the window. A few seconds of slack avoids the edge case where we retrigger 1 second before the window expires and get rate-limited again.

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

- Do not nag Kyle between iterations. Own the loop.
- Do not merge on a partially-reviewed PR hoping the remaining findings "don't matter".
- Do not argue with CodeRabbit in comment threads beyond a single clarifying reply. If it's still wrong on the next pass, surface to Kyle.
- Do not add a polling fallback. Per Kyle 2026-04-19 on plan #277 — the CR loop must stay event-driven. If webhooks are unreliable, fix the event subscription + handler, don't work around it.
