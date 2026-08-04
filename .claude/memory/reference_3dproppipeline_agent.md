---
name: 3dproppipeline Blender agent — DCC capability on Hive
description: Virtual Hive agent `3dproppipeline` can drive Blender to produce/modify 3D asset files (fbx, obj, likely glb). Use for Blender-reexport validations and any test that needs real DCC output instead of fabricated binaries.
type: reference
scope: global
---

`3dproppipeline` is a virtual agent on Hive (parallel to overwatch / vaexdev / spark) that wraps Blender. Kyle confirmed 2026-04-15: *"he is another virtual called 3dproppipeline. if you send him requests he can make fbx and obj and make changes to them, tell him where to put them so your test agent can use."*

## What it can do

- Produce 3D asset files from scratch (fbx, obj, and glb — Kyle confirmed 2026-04-15 that the agent "does a lot of Python also," so any format the Blender bpy API supports is fair game).
- **Modify existing assets** — e.g. take `vehicles.glb`, rename a mesh, re-export. This is the piece that unblocks the "test harness can't fabricate a modified binary glb" problem that parked #181 Phase 2 validations `0c9ef1cc` and `b4e55875`.
- Place output at a caller-specified destination path so a test agent running in the same clone can immediately consume it.
- Run arbitrary Blender Python scripts. If a use case doesn't fit the "make/modify asset" framing but needs Blender as a compute engine, frame the request as Python and the agent can handle it.

## How to use it

- **Reaching 3dproppipeline requires `hive_send_message(agentKey="3dproppipeline", ...)`.** It is a *virtual* orchestrator — Kyle launches it, the server does not — so neither of you can reach the other by speaking into your own output. See [[reference_how_to_reach_another_agent]]. (This used to be phrased as an exception to a rule about ephemerals; that rule never applied to either of you, and the memory carrying it has been retired.)
- **You must manually watch its channel for responses.** Per Kyle 2026-04-15: *"for now you need to watch its channel for responses manually, we don't have that baked in yet but it's coming."* So after sending a request:
  1. `hive_send_message(agentKey="3dproppipeline", message=<request>)` to dispatch the work
  2. `hive_channel_watch(keys=["3dproppipeline"])` to subscribe — auto-subscription-on-send isn't wired up yet
  3. Watch your hive-channel feed for `chat_message` and `agent_idle` events with `agent_key="3dproppipeline"` to see the response
  4. When done, `hive_channel_unwatch(keys=["3dproppipeline"])` to clean up the subscription
- **Scratch-folder sandbox model (trial phase, Kyle 2026-04-15):** every request must specify the exact scratch folder(s) `3dproppipeline` should read from and write to. The agent does NOT have broad filesystem access — it only touches what you explicitly hand it in the request. Pick a scratch path inside the test agent's clone (e.g. `C:\projects\agents\plans\planN\Verlet\workspace\...\_scratch\`) or an agreed shared scratch location, and name it in the request.
- Request shape: (a) input file path (absolute, inside the scratch folder you're granting), (b) the operation ("rename mesh X to Y", "add a new mesh", "export as glb", etc.), (c) output path (absolute, inside the scratch folder).
- Wait on `agent_idle` via the (manually-subscribed) channel watch before dispatching the test agent to consume the output (volleyball pattern).
- If a use case needs `3dproppipeline` to read/write outside the scratch folder you set up, DO NOT try to work around it — ask Kyle. He explicitly said the permission surface can be expanded if the trial goes well, but only at his discretion.

## When to use it

- Any Verlet validation that needs a real DCC re-export rather than a fabricated binary. Specifically the plan #187 parked items: `0c9ef1cc` (sub-asset rename detection) and `b4e55875` (mesh addition preserves sub-asset keys).
- Any future plan that needs a specific 3D asset fixture that would be painful to hand-author.
- **NOT** for testing pure GLTF parsers in isolation — fabricated fixtures are still fine there. Use 3dproppipeline when you specifically need the binary to come out of a real DCC pipeline because the behavior under test depends on real DCC output.

## Charter note

`3dproppipeline` is a separate charter like overwatch or vaexdev. Other orchestrators do not edit its internals — they send requests and consume output. If it is missing a capability another agent needs, file a plan on its side via a message, the same coordination pattern used between any two orchestrators.
