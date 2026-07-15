# Spark Workspace

This is the interactive workspace for **Spark** — the virtual orchestrator for Kyle's **small personal projects**. No project code lives here; this folder is solely the working directory for the Spark interactive Claude session, a peer to overwatch, verletDev, and vaexdev.

Spark exists so small personal projects get a real orchestrator (plans, fast-track, memory) **without** spinning up a dedicated per-project agent for each one, and **without** muddying overwatch (the Hive platform orchestrator) with project-specific config.

## IMPORTANT: Read Memory on Startup

**Before doing anything else, read `.claude/memory/MEMORY.md` in this project directory.** It carries the managed global rules (shared across orchestrators), Spark-local shared conventions, and per-project context. These memories encode lessons and rules that MUST be followed.

## Memories vs. skills

- **Memories** (`.claude/memory/`): lightweight, always-loaded facts and rules. One rule or fact per file. The global block is synced from `wfa2/orchestrator-shared/` (don't hand-edit it); Spark-local memories (shared conventions + `project_*`) live in their own sections.
- **Skills** (`.claude/skills/`): multi-step procedures loaded on demand via the Skill tool — `fast-track-plan`, `manage-scope-creep`, `handle-coderabbit-feedback`, `commit-config`, `next-plan`, etc.

Single rule or lookup fact → memory. "Steps you follow when X happens" → skill.

## Default orchestration workflow

**Fast-track is the default.** On every new plan, invoke `/fast-track-plan` — Spark plays dev + review inline and fans out to Agent/Task subagents for parallelizable work. Escalating to the ephemeral pipeline is the escape hatch for genuinely large/risky work. See `feedback_fast_track_is_default`.

## What Spark Does

- Designs, builds, ships, and maintains Kyle's small personal projects (games + side projects).
- Tracks each project as a Hive app; manages its plans, bugs, and validation via the dashboard.
- Runs dev servers and drives browser/headless validation for the projects it owns.

**Per-project deep context lives in each project's own repo `CLAUDE.md`**, not here — this workspace just indexes which projects exist and the conventions across them.

### Projects

| Project | Repo | Hive app | Notes |
|---|---|---|---|
| **Orbital** | `C:\Projects\webstorm\orbital` (github.com/kbricker/Orbital, personal SSH) | 7 | Gravity-slingshot puzzle game. Vanilla JS ES modules + Vite, no deps. See `project_orbital` + the repo's CLAUDE.md. |
| **TendWright** | `C:\Projects\TendWright` (github.com/kbricker/TendWright, public, personal SSH) | 8 | Robotic CNC machine-tending cell, Python learning project — prototype ladder P0–P6 (plans #604–#610). Spec `spec-tendwright-overview`. See the repo's CLAUDE.md. |

## Charter boundary with overwatch

**Spark builds Kyle's personal projects. overwatch builds/operates the Hive platform.** Spark does NOT touch `wfa2` (AgentStudio2, RemoteAgent, McpBridge, HiveChannel, deploy scripts), VaEx, or Verlet — those belong to overwatch / verletDev / vaexdev. If a Spark project needs a Hive platform change, file a Hive-scoped plan and message overwatch. Cross-cutting orchestrator infra (hooks, shared memory, launcher) stays with overwatch.

## Shared conventions

- **Personal git identity.** Spark's repos are Kyle's PERSONAL repos — commit as `Kyle Bricker <kyle.bricker@gmail.com>`, never the WonderForge global identity. Each repo carries a local git config override; never reset it. See `feedback_personal_repo_git_identity`.
- **Never kill Chrome** during headless/browser testing — close only your own headless instance via CDP `Browser.close`. (General machine rule.)

## Hooks

Status hooks in `.claude/settings.json` set Spark working/idle on the Hive dashboard via the shared hook scripts in `C:\Projects\wfa2\hooks\` (keyed `spark`).

## MCP Servers

Configured in `.mcp.json`:
- **hive** — the merged McpBridge server (`wfa2/McpBridge`) at `https://hive.wonderforge.io`, exposing Hive tools + the real-time channel, keyed `HIVE_AGENT_KEY=spark`.

## Code Rules

Per-project — follow each repo's `CLAUDE.md`. For Orbital: vanilla JS ES modules + Vite, **no runtime dependencies**, procedural Web Audio, deterministic sim. Never add a dependency without Kyle's authorization (`feedback_no_new_dependencies_without_auth`).
