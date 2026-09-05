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
4. **If Kyle resumes normal work after the prep without restarting** (new instructions arrive, the session moves on), the handoff is now stale state that the next startup — possibly days later — would wrongly "resume". The `hive-restart-nag.mjs` UserPromptSubmit hook (782.9) flags this deterministically on every following prompt — this step as previously written ("delete it before the new work") was model recall at a moment with no edge, and it failed live: spark consumed a two-day-old handoff nobody deleted. When the nag fires, pick one: restart still imminent and the prep current → leave it alone; work has resumed → CANCEL with `node C:/Projects/wfa2/hooks/claim-restart-handoff.mjs --cancel "<workspace>"` (the nag supplies the workspace path), which journals it unconsumed as `<ts>-cancelled.md` (evidence preserved, unlike the bare delete this step used to prescribe); restart still coming but state moved on → RECONCILE by overwriting the handoff with current state. Re-run this skill if Kyle preps again later. If a cancel reports `ERROR_STOP`, the journal write failed and the handoff remains in place. Tell Kyle, fix the journal-write failure, and rerun the cancellation command. Do not read, delete, or move the handoff manually — the claim-first ordering below exists precisely so nothing reads it before it is safely journaled.

### Handoff content spec

Write for a cold reader — the fresh session has zero session-local context. No shorthand that only this session understands.

- **Header:** agent key, date, and why this restart is happening (what change is being absorbed).
- **Post-restart verification first:** any check that proves the new config/binary actually landed (e.g. "your hive_send_message description must read X" after a McpBridge change; `/health` version after a dashboard deploy). The fresh session runs these before resuming work.
- **In-flight work, in priority order:** for each item — plan number + current status, the exact next step, and the event/gate it's waiting on (PR number, CR state, validation item, a message from another agent).
- **Declared plan to re-declare:** the plan id this session had declared with `hive_set_status(planId)`, if any. The restart clears it server-side (#937 — a new session id expires the declaration), so the fresh session re-declares it as its first act after the claim when that work continues, and declares nothing when it does not.
- **Watch-list to re-establish:** `hive_channel_watch` state is process-local and a restart clears it — list the agent keys the fresh session must re-watch (and why). Note in the handoff: after re-watching, the fresh session must poll each listed agent's current chat/status once — channel events that fired during the restart window are lost, and a gate may already have opened.
- **Loose ends and dormant items** with their wake conditions (e.g. "plan #N waits on Kyle's bench validation — do not nag").

## Startup consumption (the post-restart half)

The consumption rule lives in each workspace's CLAUDE.md so the fresh session sees it at launch. **It is in FOUR workspaces — overwatch, vaexdev, vaexdev2, spark** (correctly absent from the RemoteAgent-started agents — 3dproppipeline since 782.31 reclassified it remote — and from finley, who orchestrates nothing). Verify by grepping `claim-restart-handoff` across the managed workspaces rather than trusting this list; vaexdev2 was missing from it for weeks, and it is the one instance whose silent divergence from vaexdev the composition model exists to prevent. **The block below is canonical — the CLAUDE.md copies must match it verbatim (sans the blockquote `>` markers).** Delivery is split since 782.30/.31: the twins receive their copy inside the managed `vaex-dev` CLAUDE.md block (edit `roles/vaex-dev/CLAUDE.shared.md`, and the next sync carries it), while overwatch and spark still hand-carry theirs in the local head — changing this block means editing the role source AND a manual pass over those two.

> ## Restart handoff (fresh process launch only)
>
> At session start, right after reading MEMORY.md — and ONLY in the interactive main session at a fresh launch (never a subagent, headless run, scheduled routine, or a context-compaction resume) — run:
>
> ```text
> node C:/Projects/wfa2/hooks/claim-restart-handoff.mjs
> ```
>
> It claims the handoff in one literal command — all file work is internal to the script, so nothing prompts — and prints what to do next:
> - `NONE` — no handoff; start normally.
> - `CLAIMED` / `RECOVERED` — act on the printed content: run its verification checks, re-establish its watch list (then poll each watched agent once, since events during the restart were lost), and resume its work.
> - `ERROR_STOP` — stop and tell Kyle; do not act on the handoff.
>
> Handoffs are written by the `prepare-restart` skill when Kyle says "get ready for a restart".

(The claim mechanics — mkdir + no-clobber move into `.claude/restart-journal/`, numeric-suffix retries, the read-then-delete fallback, deletion-beats-replay — live INSIDE `claim-restart-handoff.mjs` now; the script replaced the hand-run `mv -n` procedure precisely because a timestamp assignment inside the claim command defeated the Bash allow rule and re-prompted on every launch. Edit the script, not this block, to change claim behaviour.)

## Git hygiene

`.claude/restart-handoff.md` and `.claude/restart-journal/` are **gitignored transient state** in every orchestrator workspace — never committed. A committed handoff would replay on a fresh clone or checkout even after the local copy was consumed. The journal is a local archive: keep forever, gitignored; crash-mid-resume recovery is Kyle directing the session to the journal entry (never the agent reading the journal on its own).

## Do not

- Do not delete the handoff on successful consumption — journal it (deletion is only the move-failure fallback).
- Do not read the handoff before claiming it — move first, verify gone, then read the archived copy. A crash between read and move would let the next session replay it; claim-first closes that window. Read-then-delete is only the move-failure fallback.
- Do not append to an existing handoff — overwrite. One file, latest state.
- Do not start new work between "Ready to restart" and the restart, and do not trigger the restart yourself — Kyle owns the restart.
- Do not consume a handoff from a subagent, headless run, or post-compaction continuation — fresh interactive process launch only.
- Do not commit `.claude/restart-handoff.md` or `.claude/restart-journal/` in any workspace.
