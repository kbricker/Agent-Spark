---
name: log-review-findings
description: Log review catches to the fleet-wide Hive review-findings store (plan #632) whenever ANY review settles — internal adversarial subagents, self-review, CodeRabbit catches worth keeping, or an ephemeral review agent's verdict. Invoke at the moment a review's findings are final, before the plan moves on. This is how review catches stay durable and mineable instead of evaporating in session transcripts.
scope: global
---

# Log Review Findings

Every review catch that survives verification gets logged to the Hive review-findings
store — the durable, fleet-wide corpus that feeds the task-ripeness mining (#624 → #632).
The #624 mining proved the cost of not doing this: internal review was 26 of 1,590
findings in six months of data because its catches lived only in session transcripts.

The rule (always-loaded memory `feedback_log_review_findings`): **a review is not
finished until its surviving findings are in the store.** This skill is the procedure.

## When to invoke

- A fast-track plan's internal adversarial review settles (fast-track-plan step 9).
- An ephemeral review agent's code review reaches a verdict (run-plan-workflow Phase 1.75 —
  the review template instructs the agent to log; the orchestrator verifies it happened).
- A CodeRabbit pass produced catches worth keeping alongside the internal corpus.
- Kyle or an agent spots a review-shaped catch outside a formal review (a regression a
  deploy surfaced, a bug found while reading code) — log it with `reviewer` reflecting
  who/what actually caught it.

A review pass with zero surviving findings logs nothing — do not log "no findings" entries.

## How

One `hive_review_finding_add` call per review with all findings batched. The call
accepts at most 50 findings — a review with more than 50 splits into chunks of ≤50,
and the review only counts as logged once **every** chunk has returned success (a
failed chunk is safe to retry whole: the server rolls back partial batches).
Fallback when the MCP tool isn't loaded in the session: `POST /api/review-findings`
with `{"findings":[...]}` and your agent key in `X-Api-Key`.

Per finding:

| field | rule |
|---|---|
| `plan` | plan number as text — prefer the raw number ("632"); dotted display numbers ("623.6") also work (the store token-matches both, the dashboard panel queries both) |
| `reviewer` | `internal-adversarial` for subagent/self review; `coderabbit` for transcribed CR catches; something honest otherwise (e.g. `deploy-regression`) |
| `lens` | the review dimension that caught it: security, concurrency, quality, … |
| `category` | kebab-case class: security-xss, crash-consistency, availability-dos, correctness, efficiency, consistency, maintainability |
| `severity` | critical / major / minor |
| `criterion` | task-ripeness criterion 0–6 — which planning check would have prevented this. Set it when you can tell; omit when you can't |
| `outcome` | fixed / skipped / no_change_needed — **log skipped findings too**, with the reason in `summary`; a deliberately-declined catch is signal |
| `summary` | one-line statement of the defect (what breaks, under what input) |
| `pattern` | **the mineable field** — the generalized shape, not the specific bug. "escaper safe for element content reused in attribute context", not "escapeHtml missed quotes in plans.js" |

`loggedByAgent` and timestamps are stamped server-side from your key — never send them.

## Discipline

- Log once, when the verdict is settled — not per-iteration while findings are being argued.
- Findings are immutable and append-only. A wrong entry is corrected by context, not edited;
  don't spam corrections, get it right at log time.
- Keep `pattern` general enough to cluster: if two different bugs would produce the same
  pattern string, you've got it right.
- Check the store before repeating history: `hive_review_finding_list` with a `pattern`
  substring (or the dashboard's Review Findings view) shows whether a catch is a recurrence —
  a pattern that keeps recurring despite config fixes is a planning-phase gap worth a new
  pre-condition (raise it with Kyle).

## Relationships

- `fast-track-plan` step 9 and `run-plan-workflow` Phase 1.75 both invoke this at review-settle.
- The ephemeral review agent template (`agent-templates/review/CLAUDE.md`) carries the same
  instruction for agents that don't load orchestrator skills.
- Memory `feedback_log_review_findings` is the always-loaded one-line rule pointing here.
