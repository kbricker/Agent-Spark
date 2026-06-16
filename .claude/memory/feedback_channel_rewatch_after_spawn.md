---
name: Re-watch agent on hive-channel after every spawn (kill drops watches)
description: hive_kill_agent silently removes the agent key from the hive-channel watch list. After any respawn — especially same-key respawn — call hive_channel_watch again or events go silent.
type: feedback
scope: global
---

After calling `hive_kill_agent`, the killed agent's key is dropped from the hive-channel watch list. Any subsequent `hive_spawn_agent` (even under the same key) starts un-watched — `agent_working`, `agent_idle`, and `chat_message` events will NOT arrive until you re-call `hive_channel_watch`.

**Why:** Observed during the plan #136/#68 smoke test on 2026-04-09. After killing test-plan136 and respawning, no notifications arrived. `hive_channel_watching` returned "(none)". Re-calling `hive_channel_watch` immediately fixed it. This caused a real debug detour — symptoms looked like the agent was stuck or hooks weren't firing, but it was just the watch list being silently cleared. Tracked as a backlog plan to fix server-side, but the bug remains until then.

**How to apply:** Whenever you spawn an agent, call `hive_channel_watch [key]` immediately after the spawn — even if you "already watched it earlier in the session". The cheapest reliable pattern is: spawn → watch → send message, every time. Don't trust that a previous watch survived a kill. If notifications go quiet on an agent you expect to be running, check `hive_channel_watching` first before assuming the agent is broken.
