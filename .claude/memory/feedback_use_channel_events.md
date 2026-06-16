---
name: Use channel events instead of sleeping
description: Watch for agent_idle/agent_working events from hive-channel instead of blind sleeps when waiting for agent responses
type: feedback
scope: global
---

When waiting for an agent to respond, use the hive-channel watch events (agent_idle, agent_working) to know when the agent is done — don't use blind `sleep` commands.

**Why:** The channel watch is already set up and delivers events in real-time. Sleeping wastes time and misses the actual completion signal.

**How to apply:** After sending a message to an agent, wait for the `agent_idle` event to come through the channel before reading chat or taking the next step. Only sleep briefly if needed for initial spawn registration (where no event fires).
