---
name: CodeRabbit auto-triggers reviews on PR push — don't manually request after dev commits
description: CR automatically runs a full review on PR creation and on every commit pushed to an open PR. Manually posting `@coderabbitai full review` after a dev push is redundant and wasteful. Only use the manual trigger for no-new-commit re-evaluations.
type: reference
scope: global
---

**CodeRabbit reviews are push-triggered by default.** Every new commit pushed to an open PR kicks off an automatic full review. PR creation also kicks off a review.

## What this means for the rabbit loop

The `handle-coderabbit-feedback` skill previously had me doing this each iteration:
1. Dev pushes fixes
2. Post `@coderabbitai resolve`
3. Post `@coderabbitai full review`
4. Wait for review

Step 3 was redundant. The push in step 1 already triggered a review. The manual `full review` created a second, duplicate run against the same HEAD. Waste of CR credits and made the review log harder to reason about.

## The correct flow

1. Dev pushes fixes → **CR auto-reviews** in the background
2. Wait for the auto-triggered review to publish (watch the channel / `gh pr view --comments`)
3. Read the verdict, sift findings, loop

No manual `full review` needed. **No routine `@coderabbitai resolve` either** — CR marks its own comments addressed on the next pass (the `(edited)` inline-comment events); only post resolve when stale threads genuinely linger after a clean review and the PR is about to merge. Every `@coderabbitai` command costs quota against the adaptive rate limit (Kyle 2026-07-11, plan #581: "learn to not be so chatty with CR").

## When to still use `@coderabbitai full review`

- **No new commit but you want CR to re-evaluate.** E.g., you posted reply comments you want CR to process, or an external state change (CI result, webhook) happened that CR should re-consider.
- **Stale-base diagnosis:** if an auto-triggered review's "Commits: reviewing between X and Y" section doesn't match the current HEAD on origin — usually because your resolve/re-trigger fired before a push fully propagated — you can manually re-trigger once you've verified the push is visible.

In both cases, confirm the commit you want reviewed is on origin BEFORE posting the trigger, otherwise you repeat the stale-base problem.

## Ordering gotcha

If you post `@coderabbitai resolve` or any CR command in the exact moment dev is pushing, the CR action may run against the pre-push HEAD. Always verify via `git fetch` + `git log origin/{branch}` that the expected commit is visible before firing CR commands that depend on the latest state.

## Source

Kyle confirmed this 2026-04-15 after I had spent several CR passes on #187 running manual `full review` triggers after every dev push, creating duplicate reviews. One of those duplicate runs happened to fire against a stale base and produced a confusing "pass 5" that echoed pass-4 findings already landed in a newer commit.
