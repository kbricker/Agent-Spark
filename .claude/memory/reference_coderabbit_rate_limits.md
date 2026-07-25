---
name: CodeRabbit rate limits are adaptive and pooled across the whole fleet as kyle-wf
description: CodeRabbit Pro rate limits are adaptive (fair-usage tiers), pooled per developer identity — the whole agent fleet counts as kyle-wf; how to check status without burning a review
type: reference
scope: global
---

CodeRabbit rate limits (researched 2026-07-14 after wfa2#95 got blocked):

- **Pro plan nominal: 5 PR reviews/hour per developer** (rolling window, not hourly reset), with the **Fair Usage policy overriding it** at sustained high volume — both per public docs. The specific tier ladder is **our observed/inferred behavior, not documented**: keyed to the last 7 days, roughly 0-29 reviews → 5/hr, 30-39 → 4/hr, 40-49 → 3/hr, 50-59 → 2/hr, 60+ → 1/hr one-at-a-time.
- **Every run counts**: automatic review on PR open, automatic incremental review on EVERY push to an open PR, and manual `@coderabbitai review` / `full review`. Runs that don't submit a formal review object (e.g. summary-comment-only incremental runs) appear to count too — observed behavior is stricter than the count of submitted reviews suggests (25 formal submissions/week measured, yet ~2/hr behavior).
- **Pooled per developer identity** (repo-specific observation, follows from limits being per-developer): every agent (overwatch, vaexdev, spark, codexhive...) authors commits/PRs as kyle-wf, so the entire fleet consumes ONE developer's allowance — that's why the org trips the fair-usage flag despite modest per-repo volume.
- **`@coderabbitai rate limit`** posted as a PR comment returns current status WITHOUT consuming a review. Use this before retrying, instead of blind full-review triggers.
- Rate-limit wait messages come in two phrasings (2026-07 format change): legacy "Please wait **N minutes and M seconds**", newer "Review limit reached" + "**Next review available in:** **N minutes**". The handle-coderabbit-feedback retry sub-procedure parses both.
- Unblock option: usage-based billing add-on, $0.25/file for over-limit reviews (Billing → usage tab). Waits observed: 15-33 min.
- CodeRabbit is NOT installed on the WonderForge/Gateway repo (PRs #1, #2 had zero bot activity) — don't wait for it there.
