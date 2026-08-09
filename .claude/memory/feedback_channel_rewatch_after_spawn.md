---
name: An empty channel watch list looks exactly like a quiet fleet
description: Watch lists are process-local, so any process boundary clears them. Silence is ambiguous — check hive_channel_watching before diagnosing agents as stuck.
type: feedback
scope: global
---

**The kill-drop bug this file was originally written about is FIXED and has been since 2026-04-17.** `hive_kill_agent` does *not* drop the agent's key from the watch list. Do not add defensive re-watches on that basis, and do not re-file it.

Fixed in commit `b78697a` (plan #183, addressing CodeRabbit review), whose message reads: *"Preserve watchedAgents membership across AgentRemoved so restart and respawn paths don't silently drop channel forwarding."* Verified 2026-08-08: the only two `watchedAgents.delete` calls left in `McpBridge/src/index.ts` are the 200-entry cap eviction (line 94) and explicit `hive_channel_unwatch` (line 1672). Neither is the kill path.

The original ticket (#149, filed 2026-04-10) was fixed **seven days later** and nobody closed it, so this memory kept asserting *"the bug remains until then"* for four months — in five agents' system prompts, while the memory budget was the binding constraint on two other plans. #149 was cancelled 2026-08-08. **That history is the reason this file still exists rather than being deleted: the general rule below is true, load-bearing, and was buried under a dead bug.**

## The general rule: watch lists are process-local

Kill/respawn is one instance of a broader fact — **the watch list lives in the session process, so any process boundary clears it.** A restart empties it on either launch path (dev flag or `--channels plugin:hive-channel@wonderforge`); this is expected behaviour, not a migration symptom. Confirmed 2026-08-03 with overwatch: both our lists read `(none)` after restart and overwatch knew it had `3dproppipeline` watched beforehand.

An empty watch list produces **exactly the same observation as a quiet fleet** — silence, no error, no warning. Don't diagnose silence as "agents still working" or as a channel/migration fault until `hive_channel_watching` has been checked.

The **planned** restart is already covered: `prepare-restart` requires a watch-list section in the handoff, and the CLAUDE.md consumption block re-establishes it and polls each agent once (events during the restart window are lost). That skill is `scope: global` and byte-identical to the canonical copy in `wfa2/orchestrator-shared` — verified 2026-08-03, so do not "discover" this gap again and propose fleet work for it.

What is genuinely **not** covered is the **unplanned** restart — crash, hang, reboot. No handoff was ever written, so nothing on disk names who was being coordinated. Raised with overwatch 2026-08-03; unresolved, and Kyle's call whether it's worth continuously-maintained state.
