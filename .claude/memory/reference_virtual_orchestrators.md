---
name: Virtual orchestrator roster
description: Before rolling anything out to "the other orchestrators" or counting how many exist — read this list; it is overwatch, vaexdev, vaexdev2, spark, 3dproppipeline, and it churns
type: reference
scope: global
---

The ACTIVE set of virtual (interactive-Claude-session) orchestrators:

1. **overwatch** — Hive platform, `C:\Projects\overwatch\`
2. **vaexdev** — game design / VaEx world content, `C:\Projects\vaexdev\`. Clone `C:\Projects\Unity\VaEx`.
3. **vaexdev2** — **second instance of the same role as vaexdev**, `C:\Projects\vaexdev2\`. Clone `C:\Projects\Unity\VaEx2`. Added 2026-08-04, plan 782.2.
4. **spark** — Kyle's small **personal** projects studio, `C:\Projects\spark\` (Orbital first; added 2026-06-15, plan #501)
5. **3dproppipeline** — 3D asset / prop pipeline orchestrator, `C:\Projects\3dproppipeline\`

**vaexdev and vaexdev2 are one role with two instances, not two agents.** They compose the same role bundles (`unity-dev`, `vaex-dev`) and those copies must stay byte-identical. A change to VaEx knowledge is a change to *both*, and it reaches them by editing the canonical original in `orchestrator-shared/roles/` and re-propagating — never by editing one workspace. This is the first instance of the composition model in #678; see `orchestrator-shared/roles/README.md`.

Not active (do NOT propagate to these, do not count them in "the other orchestrators"):

- **verletDev** — RETIRED 2026-07-09 (#538 roster refresh). Workspace at `C:\Projects\verletDev\` is frozen as-is.
- **codexhive** — completed R&D (Codex-model harness experiment, `C:\projects\codexhive`); setup works but Codex is not currently in use. Parked, per Kyle 2026-07-09.

Each active orchestrator has its own workspace, its own `.claude/settings.json`, its own `.claude/memory/`, and its own git repo. When a cross-orchestrator change lands (new hook, new shared memory rule, new launcher behavior), it must go to ALL active ones.

**Why:** Plan #255 (2026-04-18) started with "the three orchestrators" and overwatch under-counted because 3dproppipeline wasn't in roster awareness — Kyle had to name it explicitly. The roster has churned repeatedly since (codexhive + spark joined, verletDev retired). Don't trust a remembered number or an old propagation table — read this list.

**How to apply:** Any time the task scope is "roll this out to the other orchestrators" or "tell my agents X", enumerate ALL active orchestrators from this list. A full propagation beyond overwatch currently has FOUR destinations: vaexdev, vaexdev2, spark, 3dproppipeline. Charter caveat: spark builds Kyle's personal projects only (not wfa2/VaEx/Verlet) — some platform-specific globals still propagate to it for the shared baseline, but it won't act on Hive-platform work.

**All five launch on the supported plugin channel** (`--channels plugin:hive-channel@wonderforge`) as of 2026-08-04, plan 754.2. The legacy `--dangerously-load-development-channels server:hive` flag still works but nothing uses it. See `reference_channel_launch.md` for the rollback path if one ever needs to go back.

Also see `reference_channel_launch.md` for launcher details (`virtual-launcher/launch.ps1`, desktop .lnk files, credential manager key storage) — this file is the "who exists" file; that file is the "how they start up" file. The word "wrapper" was correct until plan #752 (2026-08-02) retired the resident Node process; the launcher is now a launch-time PowerShell script and nothing stays running.
