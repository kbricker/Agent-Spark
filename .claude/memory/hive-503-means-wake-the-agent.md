---
name: hive-503-means-wake-the-agent
description: "503 + asleep = sleeping agent: watch, wake, wait, send, sleep"
source: orchestrator/hive-503-means-wake-the-agent@12
metadata:
  type: feedback
---

A `hive_send_message` that returns a 503 whose body says `status: "asleep"` (before plan #1016 the body was only `{"error":"Agent 'forge' not available"}`) means the persistent agent is Offline (asleep), which is its normal resting state. The message is dropped, not queued.

**Why:** On plan #1000 (2026-09-05) I read that 503 twice as "forge is unreachable tonight", recorded it that way on the plan and in a message to overwatch, and closed the ticket without delivering forge's brief. Kyle: "haah how did you forget that you need to send a wake command to forge." The procedure was already in `reference_forge_agent` — the miss was not recalling it when the 503 arrived.

**How to apply:** Since plan #1016 the 503 body carries a `status` field: `asleep` is this case; `attached` and `undelivered` name their own fix in the body and are not wake cases; an unregistered key is a 404 with status `unknown`; a 202 `stored-unconfirmed` is a Primary agent at its launch baseline — the message is in its chat log, watch for its agent_working event, and if none follows ask Kyle to launch it (it cannot be woken). On the `asleep` 503, do not retry the send and do not escalate. `hive_channel_watch` the agent, `hive_agent_wake` it, wait for its `agent_ready` / idle event, send the brief, and `hive_agent_sleep` it once it is idle again (never while Working), then unwatch. Related: [[recall:reference_forge_agent]], [[output-reaches-nobody]].
