---
name: Check the Claude Code docs when the harness fights you
description: Permission prompts, hook misfires, settings that don't take effect — read the current docs before theorising. The harness is a moving target and yesterday's mental model is stale.
type: feedback
scope: global
---

When Claude Code itself behaves unexpectedly — permission prompts that shouldn't fire, allow rules that don't match, hooks not running, settings with no effect, a flag that changed meaning — **go read the current documentation before forming a theory.** Do not reason from how the harness worked last month.

**Why:** Kyle, 2026-08-03. Overwatch burned a long stretch on recurring Bash permission prompts and produced two confident, wrong diagnoses from first principles (sandbox escape; then "it's writes to `.claude/`"), killing each against evidence only after asserting it. Kyle's call — *"I bet they made these blankets less blankety, maybe we need specific sub permissions now"* — was the instinct to check whether the platform's rules had changed. One doc fetch settled it in a single pass: an allow rule, **including a bare `Bash`, will not match past a shell variable assignment**. Documented behaviour, not a bug, and unguessable from the outside. See [[reference_bash_permission_matching]].

The general shape: **the harness is a moving target.** Permission semantics, sandbox behaviour, channel plumbing and settings keys all change under us between versions — [[reference_channels_platform_dependency]] is the same lesson from the channel side. Our mental models silently go stale, and a stale model produces a *plausible* wrong answer, which is worse than no answer because it survives scrutiny.

**How to apply:** the moment friction is with Claude Code rather than with our own code, fetch the relevant page under `https://code.claude.com/docs/en/` — `permissions`, `settings`, `permission-modes`, `hooks`, `iam`. Read it before writing a fix and before telling Kyle what is wrong. Note the CLI version you observed the behaviour on (`/status`, or the `version` field in the session transcript) so the finding is dated. Then record what you learned as a `reference_` memory, because the next agent will hit it too. Never make Kyle the sensor for something the docs state plainly — see [[feedback_research_before_asking]] and [[feedback_verify_before_asserting]].
