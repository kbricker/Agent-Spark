---
name: deploy-test-before-merge
description: Deploy a feature branch for human testing before merging, then polish on the branch until approved. Use when a plan's changes need human taste review beyond the test agent's automated validation (UI polish, UX flows, visual work).
scope: global
---

# Deploy and Test Before Merging

The default rule: polish commits go on the feature branch, not on main. Deploy the branch, let the humans (and the test agent) exercise the deployed build, iterate on the branch until approved, then merge. This is the opposite of "merge now, fix on main".

## When to use this skill

Kyle says "deploy the branch so I can test it", "let me see this before we merge", "don't merge yet, I want to look", or a plan under `/run-plan-workflow` reaches Phase 2 and the changes are risky enough that the test agent's automated validation isn't sufficient on its own — UI-heavy changes, complex UX flows, visual polish work, anything where Kyle needs to actually see and feel the result. Skip this skill when the test agent's coverage is comprehensive enough that automated validation is the real signal.

## Current uncertainty — when this skill still adds value

When this rule was written, there was no test agent with web UI tooling. Validation was entirely manual — Kyle clicked through the UI himself. The "deploy branch first" step existed so Kyle's clicks happened against the right build.

Now (post-2026-04-11) the test agent role exists and has the special tooling to drive web UIs and exercise deployed servers. For many plans, the test agent's automated validation in `run-plan-workflow` Phase 2 is enough signal on its own — you don't need an additional human-in-the-loop deploy-and-click step.

Kyle is uncertain whether this skill is still broadly needed. Use judgment:

- **Still use deploy-test-before-merge when:**
  - The change is visual/UX polish that needs human taste review
  - The test agent's automation doesn't cover the flow you changed
  - Kyle has explicitly asked to see the branch before merge
  - The change is high-risk or touches something Kyle has been burned by before
  - You're not confident the test agent caught something subtle

- **Skip this skill when:**
  - The test agent's Validation checklist items cover the change comprehensively
  - The change is mechanical (refactor, dependency bump, type cleanup) and automation confirms no regressions
  - It's a fast-track plan that Kyle is actively watching in chat

When in doubt, ask Kyle one line: "want to see the branch before merge?" The cost of asking is tiny.

### Starting point

If the change targets the Hive platform, the deploy is `/deploy-hive`. For VaEx, vaexdev has its own deploy procedure. This skill is the human-in-loop wrapper; the actual deploy uses whichever platform skill fits.

## Procedure

### 1. Confirm the branch is ready for testing

- All Task checklist items checked off
- PR exists and CodeRabbit review is clean (or in the process of being handled — see `handle-coderabbit-feedback`)
- CI passes

Don't deploy a branch that's still red.

### 2. Deploy the feature branch

Whatever the deploy path is for this app. For Hive: `/deploy-hive`, deploying from the feature branch checkout rather than main. For VaEx: vaexdev's VaEx deploy procedure. For other orchestrators: whatever they use.

The important part is that the deployed build matches the feature branch, not main. Don't "deploy main and then mentally adjust for the PR".

### 3. Hand off to the test agent AND notify Kyle

- Point the test agent at the Validation checklist items and let it work.
- Tell Kyle the branch is deployed and where (URL, session, whatever) so he can look when he has time.

You can do both in parallel. Kyle's feedback and the test agent's findings go into the same pile.

### 4. Iterate on the branch

- Test agent finds something → add it as a new Task checklist item → dev agent fixes → redeploy branch.
- Kyle finds something → same flow.

Every fix commits to the feature branch. Every iteration redeploys the branch. Main does not move.

### 5. Final approval → merge

When both the test agent's Validation items pass AND Kyle signs off, merge the PR. Only then does the change hit main.

## Why "polish on branch, not on main"

If you merge before testing, any polish commits land directly on main — which means either (a) unreviewed changes going into the protected branch, or (b) another feature branch just for the polish, which is overhead for no reason. The feature branch exists exactly so you can iterate until ready.

## Relationship to run-plan-workflow

`/run-plan-workflow` Phase 2 already describes a deploy + validate + iterate + merge flow. This skill is the heavier-weight variant where the human-in-the-loop step is explicit and structured. For plans where the test agent is authoritative, the Phase 2 flow in `/run-plan-workflow` is enough on its own.

## Do not

- Do not merge before the test agent validates AND Kyle (when applicable) signs off.
- Do not commit polish directly to main "just this once".
- Do not deploy `main` and claim it represents the feature branch — you're testing the wrong build.
