---
name: Re-watch agent on hive-channel after every spawn (kill drops watches)
description: hive_kill_agent silently removes the agent key from the hive-channel watch list. After any respawn — especially same-key respawn — call hive_channel_watch again or events go silent.
type: feedback
scope: global
---

After calling `hive_kill_agent`, the killed agent's key is dropped from the hive-channel watch list. Any subsequent `hive_spawn_agent` (even under the same key) starts un-watched — `agent_working`, `agent_idle`, and `chat_message` events will NOT arrive until you re-call `hive_channel_watch`.

**Why:** Observed during the plan #136/#68 smoke test on 2026-04-09. After killing test-plan136 and respawning, no notifications arrived. `hive_channel_watching` returned "(none)". Re-calling `hive_channel_watch` immediately fixed it. This caused a real debug detour — symptoms looked like the agent was stuck or hooks weren't firing, but it was just the watch list being silently cleared. Tracked as a backlog plan to fix server-side, but the bug remains until then.

**How to apply:** Whenever you spawn an agent, call `hive_channel_watch [key]` immediately after the spawn — even if you "already watched it earlier in the session". The cheapest reliable pattern is: spawn → watch → send message, every time. Don't trust that a previous watch survived a kill. If notifications go quiet on an agent you expect to be running, check `hive_channel_watching` first before assuming the agent is broken.

## The general rule: watch lists are process-local

Kill/respawn is one instance of a broader fact — **the watch list lives in the session process, so any process boundary clears it.** A restart empties it on either launch path (dev flag or `--channels plugin:hive-channel@wonderforge`); this is expected behaviour, not a migration symptom. Confirmed 2026-08-03 with overwatch: both our lists read `(none)` after restart and overwatch knew it had `3dproppipeline` watched beforehand.

An empty watch list produces **exactly the same observation as a quiet fleet** — silence, no error, no warning. Don't diagnose silence as "agents still working" or as a channel/migration fault until `hive_channel_watching` has been checked.

The **planned** restart is already covered: `prepare-restart` requires a watch-list section in the handoff, and the CLAUDE.md consumption block re-establishes it and polls each agent once (events during the restart window are lost). That skill is `scope: global` and byte-identical to the canonical copy in `wfa2/orchestrator-shared` — verified 2026-08-03, so do not "discover" this gap again and propose fleet work for it.

What is genuinely **not** covered is the **unplanned** restart — crash, hang, reboot. No handoff was ever written, so nothing on disk names who was being coordinated. Raised with overwatch 2026-08-03; unresolved, and Kyle's call whether it's worth continuously-maintained state.
