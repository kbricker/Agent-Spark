---
name: Ephemeral agents report via their own channel output — never hive_send_message to orchestrator
description: The correct orchestration model is that ephemerals speak in their own dedicated hive-channel and the orchestrator (verletDev) is automatically watching those channels. Reports and heartbeats must be normal assistant output, NOT hive_send_message calls targeting the orchestrator's inbox. Per Kyle 2026-04-15.
type: feedback
scope: global
---

**The rule:** Ephemeral dev/review/test agents communicate via their own dedicated hive-channel. The orchestrator (verletDev, overwatch, vaexdev, etc.) is already subscribed to each ephemeral's channel via `hive_channel_watch` after spawning, so every `chat_message` on that agent's channel surfaces to the orchestrator automatically as a `<channel>` event.

**What that means for briefings:**

- ❌ **Do NOT** instruct an ephemeral to "send your report to verletDev via `hive_send_message` with agentKey=verletDev"
- ❌ **Do NOT** instruct them to send heartbeats via `hive_send_message` targeting the orchestrator's inbox
- ✅ **DO** instruct them to just speak in their own output: *"Post your report in your own chat — the orchestrator is watching your channel."*
- ✅ **DO** instruct them to post heartbeats as normal output: *"After each validation item, write a one-liner to your chat (normal output, no tool call)."*

**Why the old pattern was wrong:**

I was telling review and test agents to `hive_send_message(agentKey="verletDev", ...)`. That's a DIRECT INBOX MESSAGE to the verletDev agent's inbox, bypassing the channel watch model. It's extra work for the ephemeral, it's routing-bug-prone (agents confused `verletDev` with `dev-plan<N>` and sent to the wrong inbox — see `feedback_ephemeral_agents_misroute_to_dev` for the observed cases), and architecturally it contradicts how the channel system is supposed to work.

Kyle's 2026-04-15 correction: *"all these ephemeral agents should really only be communicating in their dedicated channel, you as the orchestrator are automatically watching that channel and responding and you know orchestrating!"*

**Exception — cross-orchestrator comms:** If an ephemeral genuinely needs to message a DIFFERENT orchestrator (e.g. a test agent on a verletDev plan needs to file a finding with overwatch), `hive_send_message` is still the right tool for that cross-channel directed message. But within-plan communication — dev/review/test ↔ their spawning orchestrator — is always via channel output.

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

This also greatly simplifies the shared-clone writer contract: if agents aren't sending MCP direct-messages, there's no risk of one landing in the wrong inbox and triggering a spurious write.

**Related skill updates needed:**
- `run-plan-workflow` — Phase 1, Phase 1.75, Phase 2 all currently say "send report via hive_send_message" or equivalent. Rewrite each to "post in own chat, orchestrator is watching the channel."
- Any future skill that dispatches ephemerals — same rewrite.
