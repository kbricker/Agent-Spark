---
name: prepare-restart
description: When Kyle says "get ready for a restart", write the restart handoff to .claude/restart-handoff.md so the fresh session resumes seamlessly. The startup side consumes the file by moving it to .claude/restart-journal/ BEFORE acting — the no-replay guarantee. Use only on Kyle's trigger.
scope: global
---

# Prepare Restart

During core-infra phases, agents restart often to absorb config/bridge/container changes. Kyle used to request a handoff blurb manually and paste it back in after the restart. This skill automates both halves (plan #652): Kyle triggers, the agent writes the handoff file, the fresh session consumes it exactly once.

## Trigger

Kyle says "get ready for a restart", "prep for restart", "restart incoming", or similar — via chat or typed in-session (no difference). **Only Kyle triggers this** — never write a handoff unprompted because a restart seems likely.

## Procedure (the pre-restart half)

1. Finish or cleanly pause the current tool action. From this moment, **start no new work**.
2. Write the handoff to `<workspace>/.claude/restart-handoff.md`. If the file already exists, **overwrite it** — latest state wins; a stale blurb from an earlier prep must not survive. Never append.
3. Reply to Kyle: "Ready to restart" plus a one-line summary of what's parked. Then stand by.
4. **If Kyle resumes normal work after the prep without restarting** (new instructions arrive, the session moves on), the handoff is now stale state that the next startup — possibly days later — would wrongly "resume". Delete `.claude/restart-handoff.md` before doing the new work, and re-run this skill if Kyle preps again.

### Handoff content spec

Write for a cold reader — the fresh session has zero session-local context. No shorthand that only this session understands.

- **Header:** agent key, date, and why this restart is happening (what change is being absorbed).
- **Post-restart verification first:** any check that proves the new config/binary actually landed (e.g. "your hive_send_message description must read X" after a McpBridge change; `/health` version after a dashboard deploy). The fresh session runs these before resuming work.
- **In-flight work, in priority order:** for each item — plan number + current status, the exact next step, and the event/gate it's waiting on (PR number, CR state, validation item, a message from another agent).
- **Watch-list to re-establish:** `hive_channel_watch` state is process-local and a restart clears it — list the agent keys the fresh session must re-watch (and why). Note in the handoff: after re-watching, the fresh session must poll each listed agent's current chat/status once — channel events that fired during the restart window are lost, and a gate may already have opened.
- **Loose ends and dormant items** with their wake conditions (e.g. "plan #N waits on Kyle's bench validation — do not nag").

## Startup consumption (the post-restart half)

The consumption rule lives in each workspace's CLAUDE.md so the fresh session sees it at launch. **It is in FIVE workspaces — overwatch, vaexdev, vaexdev2, spark, 3dproppipeline** (correctly absent from hivedev01, which RemoteAgent starts). Verify by grepping `claim-restart-handoff` across the managed workspaces rather than trusting this list; vaexdev2 was missing from it for weeks, and it is the one instance whose silent divergence from vaexdev the composition model exists to prevent. **The block below is canonical — the CLAUDE.md copies must match it verbatim (sans the blockquote `>` markers).** propagate-shared-config does NOT touch CLAUDE.md; changing this block requires a manual pass over all FIVE workspaces named above — vaexdev2 included, and it is the one that gets forgotten.

> ## Restart handoff (fresh process launch only)
>
> This rule applies ONLY to the interactive orchestrator main session, at a fresh process launch. Subagents, headless runs, and scheduled routines must NEVER touch `.claude/restart-handoff.md`. A context-compaction resume is NOT a startup — do not consume the handoff after compaction.
>
> At session start, right after reading MEMORY.md: if `.claude/restart-handoff.md` exists, CLAIM it before reading it, in exactly this sequence: `mkdir -p .claude/restart-journal`, then a no-clobber claim loop: `mv -n .claude/restart-handoff.md .claude/restart-journal/<yyyy-MM-dd-HHmmss>.md` (timestamp = time of consumption, local, 24h — obtain it with a SEPARATE `date` call and write the filename as a literal; a `TS=$(date ...)` assignment inside the claim command defeats the Bash allow rule and re-prompts on every single launch) — if the source still exists after the attempt, the target was occupied: increment a numeric suffix (`-2`, `-3`, ...) and retry, bounded at 5 attempts (a source that survives 5 no-clobber attempts is a move FAILURE — permissions or filesystem trouble, not collisions — use the fallback below); any existing path counts as occupied and no journal entry is ever overwritten. Then verify `.claude/restart-handoff.md` no longer exists. Only after it is confirmed gone: read the journal file you just created and act on it — run its verification checks, re-establish its watch list (then poll each watched agent's current state once — events during the restart were lost), and resume its work. A crash between claim and read loses only the trigger — the content is safe in the journal for Kyle to point at. If the move fails for any reason, fall back to read-then-delete: read the handoff, DELETE it, and only then act — deletion beats replay; if deletion also fails, stop and tell Kyle before acting on the handoff.
>
> If the file doesn't exist, start normally. Never read `.claude/restart-journal/` at startup except the single file you just claimed — it is an archive, not an input. Handoffs are written by the `prepare-restart` skill when Kyle says "get ready for a restart".

## Git hygiene

`.claude/restart-handoff.md` and `.claude/restart-journal/` are **gitignored transient state** in every orchestrator workspace — never committed. A committed handoff would replay on a fresh clone or checkout even after the local copy was consumed. The journal is a local archive: keep forever, gitignored; crash-mid-resume recovery is Kyle directing the session to the journal entry (never the agent reading the journal on its own).

## Do not

- Do not delete the handoff on successful consumption — journal it (deletion is only the move-failure fallback).
- Do not read the handoff before claiming it — move first, verify gone, then read the archived copy. A crash between read and move would let the next session replay it; claim-first closes that window. Read-then-delete is only the move-failure fallback.
- Do not append to an existing handoff — overwrite. One file, latest state.
- Do not start new work between "Ready to restart" and the restart, and do not trigger the restart yourself — Kyle owns the restart.
- Do not consume a handoff from a subagent, headless run, or post-compaction continuation — fresh interactive process launch only.
- Do not commit `.claude/restart-handoff.md` or `.claude/restart-journal/` in any workspace.
