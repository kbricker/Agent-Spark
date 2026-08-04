---
name: Kyle does not review PRs — CodeRabbit does
description: Never ask Kyle to review a PR line-by-line; that's CodeRabbit's job. Kyle's role is merge approval, not code review.
type: feedback
scope: global
---

Kyle does not perform PR code review. CodeRabbit is the reviewer. Kyle's role is the final merge approval after CodeRabbit has reviewed and findings are addressed.

**Why:** On 2026-04-17, after opening PRs for Plan #229, I closed out with "CodeRabbit will review; Kyle can merge when ready" framed as if Kyle would also be reviewing. Kyle: "I dont review PRs thats code rabbit."

**How to apply:**
- After opening a PR, wait for CodeRabbit's walkthrough + actionable comments. Address the findings iteratively without bugging Kyle about line-level review.
- When reporting PR status to Kyle, describe what CodeRabbit flagged and what was fixed — not "waiting for your review."
- Kyle merges when the PR is CodeRabbit-clean (and review-agent-clean for non-fast-track plans). That's the only gate on his end.
- The existing `feedback_never_skip_review.md` still applies: never merge without the full review flow completing — but the flow is CodeRabbit + review agent + Kyle's merge-click, not Kyle reading the diff.
