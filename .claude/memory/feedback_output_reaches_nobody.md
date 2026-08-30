---
name: If Kyle launched you, speaking reaches nobody
description: Primary agents' terminal output goes only to Kyle's screen — reach any agent via hive_send_message / hive_respond
type: feedback
scope: global
---

**Ask "did the server start me?" before reporting anything to another agent.** If Kyle launched you from a desktop shortcut — every Primary agent — your terminal output goes to Kyle's screen and NOWHERE else: a report written into your output reaches nobody, and the orchestrator watching your channel sees silence, which is indistinguishable from you still thinking. The only routes out are `hive_send_message` (directed to an agent key) and `hive_respond` (your own channel). Server-launched agents are the reverse — stdout is captured and forwarded, speaking is enough — which is why the wrong half of this rule sounds right. Mechanics, the wake flow for sleeping targets, and the incident behind this: `hive_recall` "how to reach another agent".
