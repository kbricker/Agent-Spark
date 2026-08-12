---
name: Check the Claude Code docs when the harness fights you
description: Read the Claude Code docs BEFORE shaping any ticket about agent behaviour, not just when the harness fights you — building against it is the case that never triggers and costs the most
type: feedback
scope: global
---

When Claude Code itself behaves unexpectedly — permission prompts that shouldn't fire, allow rules that don't match, hooks not running, settings with no effect, a flag that changed meaning — **go read the current documentation before forming a theory.** Do not reason from how the harness worked last month.

**Why:** Kyle, 2026-08-03. Overwatch burned a long stretch on recurring Bash permission prompts and produced two confident, wrong diagnoses from first principles (sandbox escape; then "it's writes to `.claude/`"), killing each against evidence only after asserting it. Kyle's call — *"I bet they made these blankets less blankety, maybe we need specific sub permissions now"* — was the instinct to check whether the platform's rules had changed. One doc fetch settled it in a single pass: an allow rule, **including a bare `Bash`, will not match past a shell variable assignment**. Documented behaviour, not a bug, and unguessable from the outside. See [[reference_bash_permission_matching]].

The general shape: **the harness is a moving target.** Permission semantics, sandbox behaviour, channel plumbing and settings keys all change under us between versions — [[reference_channels_platform_dependency]] is the same lesson from the channel side. Our mental models silently go stale, and a stale model produces a *plausible* wrong answer, which is worse than no answer because it survives scrutiny.

## Kyle, 2026-08-11 — this is a statement about the orchestrator's JOB

> *"your job is to research and plan tickets for hive, and now you have a dedicated dev agent, THE FIRST PLACE YOU SHOULD GO WITH ANY PLANNING AROUND AGENT ASSEMBLY AND HANDLING IS THE CLAUDE CODE DOCS"*

Read that as a role definition, not a debugging tip. The orchestrator researches and plans; a dedicated dev agent implements. **Research is the deliverable**, so shipping a plan built on an unchecked assumption about the harness is failing at the job itself — not a small process miss upstream of the real work.

"Agent assembly and handling" is the whole surface: how agents are launched, what flags they carry, what settings and permissions govern them, how they are provisioned and torn down, what the harness reports about them, how hooks and transcripts and subagents behave. **All of it is documented, and the docs are the first stop, not a fallback.**

## The trigger is the SUBJECT, not the friction

Friction is the easy case: something is visibly broken, so you know to look. **The expensive case is design time, when nothing is broken at all.** You are building infrastructure that targets Claude Code agents — permissions, hooks, context accounting, launch flags, transcripts, subagents — and because nothing is failing, "check the manual" never occurs to you. You feel like the author of the system rather than a user of a product.

**Why:** 2026-08-10, epic #852. Overwatch shaped and built two things without opening the docs. `/capabilities` was built wrong twice because nobody had established how permissions resolve under `claude -p`; the docs answer it in one sentence — project `.claude/settings.json` **allow** rules require workspace trust, and *"In non-interactive mode with `-p`, no dialog appears and the rules stay ignored."* And plan 852.4 shipped a full reconstruction of context occupancy — baselines, a per-model window table, a snapshot dictionary — for a number the harness computes and hands over on request. `get_context_usage` returns occupancy, window and an integer percentage on the stdin control channel RemoteAgent **already holds open**, proven on the wire.

Both were reached by measurement rather than by reading. That is the trap's engine: **measuring feels like rigour and produces real evidence**, so an earned-feeling number arrives for a question that was already answered, and nothing about it feels like a shortcut.

It compounds. Overwatch asserted "RemoteAgent holds no control channel" without checking, wrote that assertion into a plan, and later quoted the plan back as established fact — **an inference laundered into documentation by the act of filing it.** See [[feedback_verify_before_asserting]]; a ticket you wrote is a briefing you wrote.

**How to apply at shaping time:** if a ticket's SUBJECT is how Claude Code agents behave, reading the relevant docs page is step zero — before the problem statement, before the checklist, before any measurement. Ask first: *does the harness already do this, or already document the answer?* Reverse-engineering is what you do when the docs are silent, not instead of reading them. And when a probe and the docs disagree, that disagreement is itself the finding — record it rather than picking whichever you found first.

**How to apply on friction:** the moment friction is with Claude Code rather than with our own code, fetch the relevant page under `https://code.claude.com/docs/en/` — `permissions`, `settings`, `permission-modes`, `hooks`, `iam`. Read it before writing a fix and before telling Kyle what is wrong. Note the CLI version you observed the behaviour on (`/status`, or the `version` field in the session transcript) so the finding is dated. Then record what you learned as a `reference_` memory, because the next agent will hit it too. Never make Kyle the sensor for something the docs state plainly — see [[feedback_research_before_asking]] and [[feedback_verify_before_asserting]].
