---
name: Use channel events instead of sleeping
description: Watch for agent_idle/agent_working events from hive-channel instead of blind sleeps when waiting for agent responses
type: feedback
scope: global
---

When waiting for an agent to respond, use the hive-channel watch events (agent_idle, agent_working) to know when the agent is done — don't use blind `sleep` commands.

**Why:** The channel watch is already set up and delivers events in real-time. Sleeping wastes time and misses the actual completion signal.

**How to apply:** When you begin coordinating an agent, call `hive_channel_watch` on it FIRST (send has no watch side effect — plan #639), then send and wait for `agent_idle`; if `agent_crashed` arrives instead, handle the failure (restart, escalate, or stop) — a crashed agent never emits idle, so don't keep waiting. Unwatch when the coordination ends. Only sleep briefly if needed for initial spawn registration (where no event fires). Replying to someone never requires watching them — messages to your own key always arrive.
