---
name: next-plan
description: Drive the next cycle of the Verlet A/B/C/D plan series per META-PLAN.md. Reads the meta roster, determines current state (in-flight plan needs attention, or pick next from the queue), and executes via the fast-track workflow. Kyle triggers this between compactions to resume execution without re-explaining where we are.
scope: global
---

# Next-plan — cycle the Verlet series

This skill is the resume-from-compaction entry point. Every cycle starts by invoking it. It reads the meta-plan and does the right next thing.

## Step 1 — Read the meta-plan

Read `C:\projects\verletdev\META-PLAN.md` first, always. It's the source of truth for:
- What's merged
- What's in flight (including PR number, status)
- The ordered Planning queue
- Process rules + risk notes + fixture-acquisition ownership

Everything below flows from that file. If it's missing or looks stale, STOP and ask Kyle before doing anything else.

## Step 2 — Triage the current state

Use `mcp__hive__hive_plan_get` to pull the live state of whatever's marked "in flight" in META-PLAN. One of three cases applies:

### Case A: PR is open, CR auto-review is running or feedback pending

- Check GitHub PR status via `gh pr view <num> --json reviewDecision,statusCheckRollup,comments,reviews`.
- If CR has posted actionables: handle them via `/handle-coderabbit-feedback` skill.
- If CR is clean and Kyle has said "merge" in chat: `gh pr merge <num> --merge` (NEVER `--squash` — Kyle wants full history).
- If CR is clean but no merge authorization yet: report status, wait for Kyle's explicit "merge".
- Never poll in a loop — CR events arrive via channel webhook (`feedback_no_cr_polling`). Trust the event.

### Case B: plan is mid-development, no PR yet

- Check task state via TaskList (look for the plan's execution tasks if they exist).
- Pick up where the work left off. Build, test, commit, push, open PR — then transition to Case A.

### Case C: in-flight plan is marked Completed OR no in-flight plan at all

- Update META-PLAN.md: move the completed plan to the "✅ Merged" section with a brief note.
- Pick the **next** plan from the Planning queue per the table's execution order.
- Apply the `run-plan-workflow` skill to it in fast-track mode. Status flow: Planning → Review → Ready → Development → CodeReview → Completed. Kyle's 2026-04-18 steer authorizes fast-track on every plan in this series without re-asking.
- When the plan hits CodeReview with a PR open, you're back in Case A on the next cycle.

## Step 3 — Honor the fixed rules

Every cycle, regardless of case:

- **No new deps** without explicit Kyle authorization — invoke `no-new-deps` skill on any moment that might imply one.
- **No migration shims** per `feedback_no_migration_in_prototype` — change formats outright.
- **Every plan populates** its pre-committed stub spec at `packages/editor/tests/e2e/specs/<name>.spec.mjs` and adds fixtures into the right `test-*` project.
- **Fixture acquisition** ownership is defined in META-PLAN.md's bottom section — do the asset work as part of the plan that consumes it, not ahead of time.
- **Use internal review sub-agents** (Agent tool with `subagent_type: Explore` or `general-purpose`) for risky deep dives — scene-format checks, auth flow audits, render-path analysis — per Kyle's 2026-04-18 steer.
- **Visual regression** stays deferred until a plan explicitly needs it (expected first: #246 HDR/IBL).

## Step 4 — Update META-PLAN.md at the end of the cycle

Before returning control to Kyle, update `C:\projects\verletdev\META-PLAN.md`:
- Move merged plan to the ✅ section
- Update the 🏗 In flight block to the new current plan
- Bump the `Last updated:` line at the bottom
- If something surprising happened (scope shift, new bottleneck, dep discovered), note it in the risk notes section

The file is the handoff artifact — if it's accurate, the next post-compaction me can resume without asking.

## What NOT to do

- Don't re-explain the series roster to Kyle — it's in META-PLAN.md.
- Don't re-litigate decisions already resolved (fast-track, no-new-deps exemption for internal tooling, no visual regression in v1, no migration shims). If a rule is documented in META-PLAN or a memory, follow it silently.
- Don't file new plans unless a gap is discovered in the series. If one is, propose to Kyle first, don't file solo.
- Don't merge without Kyle's explicit authorization per cycle.
