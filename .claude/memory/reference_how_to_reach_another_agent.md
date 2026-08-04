---
name: How to actually reach another agent
description: Before replying to an orchestrator, reporting a result, or wondering why your last message went unanswered — check whether your output reaches Hive at all, because for interactive agents it does not
type: reference
scope: global
---

**Whether speaking is enough depends on who launched you.**

| you are | launched by | your terminal output | to reach another agent |
|---|---|---|---|
| **virtual** (overwatch, vaexdev, vaexdev2, spark, 3dproppipeline) | Kyle, from a desktop shortcut | goes to Kyle's screen and **nowhere else** | you MUST call `hive_send_message` or `hive_respond` |
| **ephemeral / cloud / remote** | the server | captured and forwarded to the channel | speaking is enough |

**If Kyle launched you, writing a beautiful report in your output sends it to nobody.** The orchestrator watching your channel sees silence, and silence is indistinguishable from you still thinking.

- `hive_send_message` — directed to a specific agent key
- `hive_respond` — reply on your own channel

## Why this is easy to get wrong

The reverse rule is real and correct for the agents it covers: a server-spawned ephemeral's stdout *is* captured, so telling it to call `hive_send_message` is redundant work and a routing-bug risk. That guidance lives with `run-plan-workflow`, which is where ephemerals get briefed.

The trap is that both rules are about "how do I report", they sound universal, and only one applies to you.

**2026-08-04:** vaexdev2's first session was asked five validation questions, answered all five carefully, and overwatch saw nothing. It had read the ephemeral guidance — which at the time was a global memory with no class caveat — and followed it correctly. The agent did nothing wrong; the rule simply did not belong to it.

## The check

Ask **"did the server start me?"** If no, a tool call is the only way out.

Related: [[reference_virtual_orchestrators]] lists which agents are virtual.
