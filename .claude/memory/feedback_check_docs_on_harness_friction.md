---
name: Check the Claude Code docs when the harness fights you
description: Read Claude Code docs when shaping any ticket about agent behaviour — docs first, before measuring, not just on friction
type: feedback
scope: global
---

When a ticket's SUBJECT is how Claude Code agents behave — launch flags, permissions, hooks, settings, context accounting, transcripts, subagents — reading the relevant docs page is **step zero**, before the problem statement, before any measurement. And when the harness itself behaves unexpectedly (permission prompts that shouldn't fire, allow rules that don't match, hooks not running, a flag that changed meaning), read the current docs before forming a theory. Don't reason from how the harness worked last month — permission semantics, sandbox behaviour, channel plumbing and settings keys all change under us between versions, and a stale model produces a *plausible* wrong answer that survives scrutiny longer than no answer would.

**Kyle, 2026-08-11 — a statement about the orchestrator's JOB:** *"your job is to research and plan tickets for hive... THE FIRST PLACE YOU SHOULD GO WITH ANY PLANNING AROUND AGENT ASSEMBLY AND HANDLING IS THE CLAUDE CODE DOCS."* Research is the deliverable, so a plan built on an unchecked assumption about the harness fails at the job itself. "Agent assembly and handling" is the whole surface — how agents launch, what flags/settings/permissions govern them, how hooks and transcripts and subagents behave — all documented; docs first, not a fallback.

**The trigger is the subject, not the friction.** Friction is the easy case: something's visibly broken, so you know to look. The expensive case is design time, when nothing is broken and "check the manual" never occurs to you because you feel like the system's author rather than a product's user. Measuring feels like rigour and produces real evidence — so an earned-feeling number arrives for a question the docs already answered.

*Incidents (2026-08, epic #852):* `/capabilities` built wrong twice because nobody checked how permissions resolve under `claude -p` (docs: project `.claude/settings.json` allow rules require workspace trust; under `-p` no dialog appears and the rules stay ignored). 852.4 shipped a full context-occupancy reconstruction for a number `get_context_usage` returns on the control channel RemoteAgent already holds open. And the bare-Bash permission prompts produced two confident wrong diagnoses from first principles, settled by one doc fetch — an allow rule won't match past a shell variable assignment ([[reference_bash_permission_matching]]).

**How to apply:**
- **At shaping time:** if the subject is harness behaviour, ask first *does the harness already do this, or document the answer?* Reverse-engineering is for when the docs are silent, not instead of reading them. When a probe and the docs disagree, that disagreement is the finding — record it.
- **On friction:** fetch the page under `https://code.claude.com/docs/en/` (`permissions`, `settings`, `permission-modes`, `hooks`, `iam`) before writing a fix or telling Kyle what's wrong. Note the CLI version (`/status`) so the finding is dated, then record it as a `reference_` memory — the next agent hits it too.

Related: [[reference_channels_platform_dependency]] (same lesson, channel side); [[feedback_verify_before_asserting]] (a ticket you wrote is a briefing you wrote); [[feedback_research_before_asking]] (don't make Kyle the sensor for documented facts).
