---
name: deploy-test-before-merge
description: Deploy a feature branch for human testing before merging, then polish on the branch until approved. Use when a plan's changes need human taste review that automated validation cannot give (UI polish, UX flows, visual work).
scope: global
---

# Deploy and Test Before Merging

The default rule: polish commits go on the feature branch, not on main. Deploy the branch, exercise the deployed build — Kyle by eye, you by automated check — iterate on the branch until approved, then merge. This is the opposite of "merge now, fix on main".

## When to use this skill

Kyle says "deploy the branch so I can test it", "let me see this before we merge", "don't merge yet, I want to look" — or the change is risky enough that automated checks are not sufficient on their own: UI-heavy changes, complex UX flows, visual polish work, anything where Kyle needs to actually see and feel the result.

## When this skill adds value

The question this skill answers is whether a HUMAN needs to look before merge. Automated validation — your own checks, or a subagent driving Playwright against a deployed build — answers "does it work". It does not answer "does it look right", and that is the whole of what this skill is for.

- **Use deploy-test-before-merge when:**
  - The change is visual/UX polish that needs human taste review
  - Your automated coverage doesn't reach the flow you changed
  - Kyle has explicitly asked to see the branch before merge
  - The change is high-risk or touches something Kyle has been burned by before
  - You're not confident the automation caught something subtle

- **Skip it when:**
  - Automated validation genuinely covers the change, and the change has no visual or feel dimension
  - The change is mechanical (refactor, dependency bump, type cleanup) and the checks confirm no regressions
  - Kyle is actively watching the plan in chat

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

### 3. Run the automated pass AND notify Kyle

- Work the plan's Validation checklist items against the deployed build. Delegate the browser-driving to a subagent if the transcript would flood your context, and ask it for observed values rather than a verdict.
- Tell Kyle the branch is deployed and where (URL, session, whatever) so he can look when he has time.

Do both in parallel. Kyle's feedback and the automated findings go into the same pile.

### 4. Iterate on the branch

- The automated pass finds something → add it as a new Task checklist item → fix → redeploy branch.
- Kyle finds something → same flow.

Every fix commits to the feature branch. Every iteration redeploys the branch. Main does not move.

### 5. Final approval → merge

When both the Validation items pass AND Kyle signs off, merge the PR. Only then does the change hit main.

## Why "polish on branch, not on main"

If you merge before testing, any polish commits land directly on main — which means either (a) unreviewed changes going into the protected branch, or (b) another feature branch just for the polish, which is overhead for no reason. The feature branch exists exactly so you can iterate until ready.

## Do not

- Do not merge before the Validation items pass AND Kyle (when applicable) signs off.
- Do not commit polish directly to main "just this once".
- Do not deploy `main` and claim it represents the feature branch — you're testing the wrong build.
