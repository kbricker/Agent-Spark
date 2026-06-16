---
name: Virtual orchestrator roster
description: The six interactive Claude orchestrators are overwatch, verletDev, vaexdev, 3dproppipeline, codexhive, and spark — use this list whenever a change must propagate to "the other orchestrators"
type: reference
scope: global
---

The complete set of virtual (interactive-Claude-session) orchestrators:

1. **overwatch** — Hive platform, `C:\Projects\overwatch\`, workspace for this session
2. **verletDev** — Verlet/VaEx game dev, `C:\Projects\verletDev\` (see `feedback_coordinate_hive_deploy_with_verletdev.md`, `feedback_ephemeral_for_wfa2_and_verlet.md`)
3. **vaexdev** — game design / VaEx world content, `C:\Projects\vaexdev\` (see `project_vaexdev_rehome.md`)
4. **3dproppipeline** — 3D asset / prop pipeline orchestrator
5. **codexhive** — Codex-model virtual orchestrator (`C:\projects\codexhive`)
6. **spark** — Kyle's small **personal** projects studio, `C:\Projects\spark\` (Orbital first; added 2026-06-15, plan #501). NOTE: spark's Hive identity key + virtual-launcher `.lnk` are pending the plan #501 handoff — once set up it launches like the others.

Each has its own workspace, its own `.claude/settings.json`, its own `.claude/memory/`, and its own git repo. When a cross-orchestrator change lands (new hook, new shared memory rule, new launcher behavior), it must go to ALL of them — easy to under-count: I've historically blanked on 3dproppipeline, and codexhive + spark are newer still.

**Why:** Plan #255 (2026-04-18) started with "the three orchestrators" and I initially said "verletdev? vaexdev? third?" because 3dproppipeline wasn't in my roster awareness — Kyle had to name it explicitly. Then codexhive (a Codex-model orchestrator) and spark (2026-06-15, small personal projects) joined without this roster being updated. The count keeps growing; don't trust a remembered number, read this list.

**How to apply:** Any time the task scope is "roll this out to the other orchestrators" or "tell my agents X", enumerate ALL of them from this list before asking Kyle who's in scope. Ask only if Kyle's intent specifically excludes one. A full propagation beyond overwatch now has FIVE destinations: verletDev, vaexdev, 3dproppipeline, codexhive, spark. Charter caveat: spark builds Kyle's personal projects only (not wfa2/VaEx/Verlet) — some platform-specific globals still propagate to it for the shared baseline, but it won't act on Hive-platform work.

Also see `reference_channel_launch.md` for launcher details (virtual-launcher wrapper, desktop .lnk files, credential manager key storage) — this file is the "who exists" file; that file is the "how they start up" file.
