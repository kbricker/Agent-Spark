---
name: feedback-coderabbit-ratelimit-batch-pushes
description: "CodeRabbit's adaptive rate limit counts every push's incremental review — batch commits during fast iteration loops, and skip @coderabbitai commands (resolve/full review) unless genuinely needed"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4ddf3e59-e074-479c-8242-cdb770b0532b
scope: global
---

During the plan #519 tuning loop (2026-07-11), CodeRabbit hit its Fair Usage rate limit from THIS session alone: six pushes to one PR (each triggering an incremental review) plus two follow-up polish PRs ≈ 8 review runs in a few hours. Kyle: "nothing else but you for hours" — no other agents were pushing.

**Why:** CodeRabbit's adaptive limit counts review RUNS, not PRs, and every push to an open PR triggers an incremental run. A rapid fix→push→Kyle-tests→fix cycle burns quota fast, and the limit then blocks unrelated tiny PRs.

**How to apply:** when iterating quickly with Kyle testing in-editor (commit → he checks → next fix), accumulate the fixes locally and push in batches (e.g. after 2-3 fixes, or when he needs to pull), rather than push-per-fix. Kyle pulls from the shared clone's working tree anyway during these loops — the push is only needed for the PR record. See [[feedback_coderabbit_webhook]].

Extended after PR #351 hit the limit again (2026-07-11, Kyle: "learn to not be so chatty with CR"). Two more rules:

1. **Don't post `@coderabbitai resolve` routinely.** CR marks its own comments addressed on the next review pass anyway (the "(edited)" inline-comment events). Only post resolve when stale threads actually linger AND the PR is about to merge. Never post `@coderabbitai full review` when a push will auto-trigger one.
2. **If more work is landing on the same PR soon, fold CR-finding fixes into the next work commit** instead of pushing them alone — on #351 the CR-fix push and the prefab-work push 20 minutes later each burned a review run when one would have covered both. On a long-lived ticket branch there's no urgency to get a clean re-review between slices.
