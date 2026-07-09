---
name: Virtual orchestrator roster
description: Active interactive Claude orchestrators are overwatch, vaexdev, spark, and 3dproppipeline (verletDev retired 2026-07-09; codexhive parked R&D) — use this list whenever a change must propagate to "the other orchestrators"
type: reference
scope: global
---

The ACTIVE set of virtual (interactive-Claude-session) orchestrators:

1. **overwatch** — Hive platform, `C:\Projects\overwatch\`
2. **vaexdev** — game design / VaEx world content, `C:\Projects\vaexdev\` (see `project_vaexdev_rehome.md`)
3. **spark** — Kyle's small **personal** projects studio, `C:\Projects\spark\` (Orbital first; added 2026-06-15, plan #501)
4. **3dproppipeline** — 3D asset / prop pipeline orchestrator, `C:\Projects\3dproppipeline\`

Not active (do NOT propagate to these, do not count them in "the other orchestrators"):

- **verletDev** — RETIRED 2026-07-09 (#538 roster refresh). Workspace at `C:\Projects\verletDev\` is frozen as-is.
- **codexhive** — completed R&D (Codex-model harness experiment, `C:\projects\codexhive`); setup works but Codex is not currently in use. Parked, per Kyle 2026-07-09.

Each active orchestrator has its own workspace, its own `.claude/settings.json`, its own `.claude/memory/`, and its own git repo. When a cross-orchestrator change lands (new hook, new shared memory rule, new launcher behavior), it must go to ALL active ones.

**Why:** Plan #255 (2026-04-18) started with "the three orchestrators" and overwatch under-counted because 3dproppipeline wasn't in roster awareness — Kyle had to name it explicitly. The roster has churned repeatedly since (codexhive + spark joined, verletDev retired). Don't trust a remembered number or an old propagation table — read this list.

**How to apply:** Any time the task scope is "roll this out to the other orchestrators" or "tell my agents X", enumerate ALL active orchestrators from this list. A full propagation beyond overwatch currently has THREE destinations: vaexdev, spark, 3dproppipeline. Charter caveat: spark builds Kyle's personal projects only (not wfa2/VaEx/Verlet) — some platform-specific globals still propagate to it for the shared baseline, but it won't act on Hive-platform work.

Also see `reference_channel_launch.md` for launcher details (virtual-launcher wrapper, desktop .lnk files, credential manager key storage) — this file is the "who exists" file; that file is the "how they start up" file.
