---
name: Ephemeral agents report via their own channel output — never hive_send_message to the orchestrator
description: Ephemerals speak in their own dedicated hive-channel and the spawning orchestrator is already watching it. Reports and heartbeats must be normal assistant output, NOT hive_send_message calls targeting the orchestrator's inbox. Per Kyle 2026-04-15.
type: feedback
scope: global
---

**Scope note:** this governs the **ephemeral** dev/review/test path, which is a legacy route — see [[project_named_agents_over_ephemerals]] and [[feedback_fast_track_is_default]]. It still applies whenever ephemerals are spawned (the `run-plan-workflow` escape hatch), but it is not the default orchestration model.

**The rule:** Ephemeral dev/review/test agents communicate via their own dedicated hive-channel. The spawning orchestrator is already subscribed to each ephemeral's channel via `hive_channel_watch` after spawning, so every `chat_message` on that agent's channel surfaces to the orchestrator automatically as a `<channel>` event.

**What that means for briefings:**

- ❌ **Do NOT** instruct an ephemeral to "send your report to <orchestrator> via `hive_send_message` with agentKey=<orchestrator>"
- ❌ **Do NOT** instruct them to send heartbeats via `hive_send_message` targeting the orchestrator's inbox
- ✅ **DO** instruct them to just speak in their own output: *"Post your report in your own chat — the orchestrator is watching your channel."*
- ✅ **DO** instruct them to post heartbeats as normal output: *"After each validation item, write a one-liner to your chat (normal output, no tool call)."*

**Why the old pattern was wrong:**

Review and test agents were being told to call `hive_send_message(agentKey="<orchestrator>", ...)`. That is a DIRECT INBOX MESSAGE, bypassing the channel watch model. It is extra work for the ephemeral, it is routing-bug-prone — agents confused the orchestrator's key with their own `dev-plan<N>` key and sent to the wrong inbox — and architecturally it contradicts how the channel system is supposed to work.

Kyle's 2026-04-15 correction: *"all these ephemeral agents should really only be communicating in their dedicated channel, you as the orchestrator are automatically watching that channel and responding and you know orchestrating!"*

**Exception — cross-orchestrator comms:** If an ephemeral genuinely needs to message a DIFFERENT orchestrator than the one that spawned it (e.g. filing a finding with the agent that owns another app), `hive_send_message` is still the right tool for that directed cross-channel message. But within-plan communication — dev/review/test ↔ their spawning orchestrator — is always via channel output.

**How to apply:**

Rewrite every ephemeral agent briefing's "reporting" section to something like:

> "## Reporting
>
> When you finish a phase, post your status update in your own chat output as normal text. Example:
>
> `[phase N/total] done — PASS — X`
>
> The orchestrator is already subscribed to your channel and will see every message automatically. Do NOT call `hive_send_message` to deliver reports — just speak in your output and it'll be routed through the channel.
>
> Use `hive_send_message` ONLY for cross-agent messages that should NOT go to the orchestrator (e.g. coordinating directly with another ephemeral, or filing a finding with a different orchestrator)."

This also simplifies the shared-clone writer contract: if agents are not sending MCP direct-messages, there is no risk of one landing in the wrong inbox and triggering a spurious write.

**Related skill updates needed:**
- `run-plan-workflow` — Phase 1, Phase 1.75, Phase 2 all currently say "send report via hive_send_message" or equivalent. Rewrite each to "post in own chat, orchestrator is watching the channel."
- Any future skill that dispatches ephemerals — same rewrite.
