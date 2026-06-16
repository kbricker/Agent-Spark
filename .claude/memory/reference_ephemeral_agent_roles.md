---
name: Ephemeral agent role definitions — dev / review / test
description: Canonical reference for the three ephemeral-agent roles orchestrators spawn per plan. Explains what each role is, when to use it, and — critically for test — when NOT to use it. Use when picking the role for a spawn.
type: reference
scope: global
---

There are **exactly three ephemeral roles** in the WonderForge Hive platform: `dev`, `review`, and `test`. Orchestrators (overwatch, verletdev, vaexdev, any future app orchestrator) spawn some combination of these per plan. The templates live in `C:/Projects/wfa2/agent-templates/<role>/CLAUDE.md` and are copied into each spawned ephemeral's clone at spawn time.

Other folders under `agent-templates/` (`planning/`, `action/`, `persistent/`) are not roles orchestrators normally spawn — they're for other spawn paths or are legacy. Stick to `dev`, `review`, `test` unless you have a specific reason not to.

---

## `dev` — writes product code

**One-line:** the implementer. Writes code, runs the project's own test suites while implementing, commits to the feature branch, opens the PR, responds to CodeRabbit feedback.

**When to use:**
- Every plan that has `task`-type checklist items needing code changes.
- Any situation where the work output is a git commit or a PR.
- Running the project's local test commands (`npm test`, `bun test`, `jest`, `dotnet test`, etc.) — that's part of dev's own implementation loop, not a separate test-agent spawn.
- Responding to CodeRabbit findings on an open PR.

**When NOT to use:**
- Reviewing work someone else wrote (that's `review`).
- Driving a running UI to verify end-user behavior (that's `test`).
- Plan review, research, audits, or anything read-only before implementation (all `review`).

**What it has:** full write access to the plan's clone, shell access for running the project's build/test/lint commands, permission to commit and push on the feature branch, permission to open the PR via `gh`.

---

## `review` — the generic read-and-analyze role

**One-line:** reads, analyzes, reports. Does NOT write product code. General-purpose — this is the role you use for anything that isn't dev or test.

**When to use:**
- **Plan review** (status `Review`): reading a plan's description and checklist, validating it's sound, refining items, flagging risks before it moves to `Ready`.
- **Code review** (status `CodeReview`): reading the PR diff, adding `fix`-type or `validation`-type checklist items for the dev agent to address. Never posts PR comments directly.
- **Research:** investigating an unfamiliar library API before dev starts, auditing a codebase for a pattern, reading documentation for a framework, drafting a spec or design doc.
- **Investigation without fixing:** reproducing a bug, tracing a failure, compiling a root-cause report — without actually changing the code.
- **Audits:** security audits, performance audits, dead-code audits, accessibility audits, component-leaf audits (e.g. Verlet's serialization audit on plans touching asset references — see `feedback_review_serialization_audit` on verletdev's side).

**When NOT to use:**
- When the task's output is a code change or a commit (that's `dev`).
- When the verification requires driving a running product UI (that's `test`).

**What it has:** full read access, can write reports and edit plan metadata, can add checklist items, but does not own the implementation branch and does not write product code.

**Why review is general-purpose:** the role is a tool bundle, not a job description. The briefing message at spawn time is where you tell the agent what to do. Don't create bespoke roles for "planning agent" or "research agent" or "audit agent" — all of those are `review` briefed differently. Kyle confirmed this on 2026-04-11: *"yes review is sort of generic we can use it for most any other functions just not dev and test."*

---

## `test` — Playwright-driven end-to-end validation on a live dev server

**One-line:** specialized. Drives a running instance of the product through a browser via Playwright, exercises user flows, takes screenshots, and reports PASS/FAIL on the plan's `validation`-type checklist items.

This role is NOT "run the tests" in the general sense. It is specifically a *visual and functional end-to-end validation via Playwright on a live dev server* role. The narrow scope is intentional — the template gives this agent a specific setup (Playwright installed globally, port selection in the 6000–7000 range, a dev-server startup procedure, screenshot capture, a PASS/FAIL report format) that only makes sense for browser-driven validation.

**When to use:**
- The plan has `validation`-type checklist items that require driving a running instance of the product — clicking through a UI flow, verifying visual output, exercising an end-to-end user scenario, confirming a deploy actually works from a user's perspective.
- You need screenshots of real rendered UI to confirm a change.
- You need to confirm a full stack (dev server + frontend + backend + DB) behaves correctly together post-deploy.

**When NOT to use:**
- **Running unit tests.** If the task is "run `npm test`" or "make sure jest/mocha/bun test passes," that's the **dev** agent's job during implementation. Dev runs the project's own test suites as part of closing out Task items.
- **Type-check runs, build verification, lint runs.** All dev's job.
- **Integration tests against a mock backend.** Usually dev's job unless the mock backend is itself a running service that needs Playwright-driven verification.
- **API testing without a browser.** If you're hitting endpoints with `curl` or `fetch`, spawn a review agent briefed to do the API probing — you don't need Playwright.
- **"Make sure the tests still pass" after a refactor.** That's dev, running the project's test commands as part of its own implementation loop.

**What it has:** Playwright installed globally, port-selection rules (6000–7000 pool to avoid colliding with editors or other test agents), a dev-server startup procedure for the relevant codebase (Verlet, VaEx, Hive, etc.), screenshot capture, a structured PASS/FAIL report format for validation items.

---

## Rule of thumb for ambiguous cases

- *"Does the code work as written?"* → **dev**, during implementation, using the project's own test suites. Not a test-agent spawn.
- *"Does the product behave correctly for a user?"* → **test**, after the feature is implemented and running.
- *"Is this plan sound / is this diff good / do I need to investigate or research X?"* → **review**.
- *"Am I inventing a new role?"* → you probably shouldn't be. Use `review` and brief it clearly in the spawn message.

## Full-plan spawn roster

A normal plan lifecycle (see `run-plan-workflow`) spawns **one of each** — 1 dev + 1 review + 1 test — persistent for the whole plan, not swapped between phases. The review agent does both plan review (Phase 1) and code review (Phase 3) on the same plan and keeps context across them. The test agent waits during dev and validates post-deploy. The dev agent implements and owns the branch.

Plans that don't have UI validation can skip the test-agent spawn — not every plan needs one. Plans that are pure docs/config can skip test entirely and may only need dev + review, or sometimes just review if no code changes at all.
