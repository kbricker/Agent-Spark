---
name: How to launch orchestrator agents with Hive channel events
description: Preferred launch is the virtual-launcher wrapper with keys in Windows Credential Manager (plan #239); direct claude invocation is a debug-only fallback
type: reference
scope: global
---

Virtual orchestrator agents (overwatch, vaexdev, verletDev, 3dproppipeline, codexhive, spark) should be launched through the **virtual-launcher wrapper** so Kyle can remote-trigger built-in slash commands (`/compact`, `/clear`, `/model <name>`) from Hive chat when working away from the desk. Plan #188 shipped the wrapper; plan #239 moved the wrapper's API key from `HIVE_API_KEY` env var to Windows Credential Manager via `keytar` (DPAPI) so desktop-shortcut launches work reliably.

**Preferred (desktop icons):** double-click `Overwatch.lnk`, `VaExDev.lnk`, `VerletDev.lnk`, or `3DPropPipeline.lnk` on the desktop. They invoke `C:\Projects\wfa2\virtual-launcher\shortcuts\virtual-launcher.cmd <agent-key>`.

**spark (added 2026-06-15, plan #501) — launcher setup PENDING:** spark has its workspace (`C:\Projects\spark`) but is not yet wired into the launcher. To finish: (1) generate the `spark` identity key in the dashboard `/admin/identities.html`, (2) `node C:\Projects\wfa2\hive-key\dist\index.js install spark` to store it in Credential Manager, (3) add a `spark` agent entry to the virtual-launcher config + create `Spark.lnk`. Until then, launch spark debug-only: `cd C:\Projects\spark && claude` (channel/remote-slash-commands won't arm without the key).

**Preferred (terminal):**

```bash
cd C:\Projects\wfa2\virtual-launcher
node dist\index.js --agent <your-agent-key>
```

Replace `<your-agent-key>` with the authoritative mixed-case form (e.g. `overwatch`, `verletDev`, `vaexdev`, `3dproppipeline`).

The wrapper spawns `claude --dangerously-load-development-channels server:hive` as a child via `node-pty` (full TTY passthrough — Ctrl+C, line editing, colors, resize all work natively) and opens a parallel SignalR connection to the Hive dashboard hub. When AgentStudio2 sees `hive <verb>` in chat targeted at a virtual agent, it broadcasts `VirtualSlashCommand`; the wrapper forwards the matching keystroke to the claude child's stdin.

## API key resolution (plan #239)

All Kyle-box clients (wrapper, hooks, McpBridge, wait-for-* helpers) look up the per-agent key in this order:

1. **Windows Credential Manager** — `Hive:<agent-key>` via `keytar` / DPAPI. Install with `node C:\Projects\wfa2\hive-key\dist\index.js install <agent>` after generating a key in the dashboard `/admin/identities.html` page. **Agent keys are case-sensitive** — use the authoritative mixed-case form the dashboard shows (e.g. `verletDev`, not `verletdev`).
2. There is no fallback — plan #242 retired the shared `HIVE_API_KEY` env var; a missing credential-store entry is a visible failure (`hive-key install <agent>` fixes it).

The wrapper uses `keytar` directly; hooks + McpBridge + wait-for-* shell out to the `hive-key get <agent>` CLI with a 2s timeout. McpBridge/wait-for-* additionally accept an injected `HIVE_API_KEY` env value — that is the wire mechanism spawned agents receive their per-agent identity key through (never a shared secret, per #242).

**Debug-only direct launch:**

```bash
claude --dangerously-load-development-channels server:hive
```

Works for a bare session without remote slash-command support — useful for debugging the MCP bridge itself. You lose remote `/compact`, but the channel notifications (`agent_idle`, `agent_working`, `chat_message`) still flow because they're handled inside the MCP server, not the wrapper.

**Details:**
- `server:hive` references the `hive` key in `.mcp.json` — the merged McpBridge server that exposes both tools and the `claude/channel` capability.
- Channel features only arm when the `hive` server sees `HIVE_AGENT_KEY` in its env (set per agent — the wrapper injects it automatically; direct launch relies on `.mcp.json`).
- VM agents (ephemerals, NightWatch) don't set HIVE_AGENT_KEY and stay dormant on the channel.
- For unattended operation in either mode, add `--dangerously-skip-permissions` to auto-approve tool calls (wrapper config: put it in `claudeArgs` of the agent's JSON).

Historical notes:
- **2026-04-17 (plan #183):** merged the separate `hive-channel` MCP server (HiveChannel/index.mjs) into `hive` (McpBridge). The old `server:hive-channel` flag now errors with "no MCP server configured with that name".
- **2026-04-17 (plan #188):** introduced the `virtual-launcher` wrapper + desktop icons.
- **2026-04-18 (plan #239):** moved the wrapper's API key source to Windows Credential Manager via `keytar`. Desktop `.lnk` launches no longer depend on `HIVE_API_KEY` being set in the shell that spawned Explorer.
- **2026-04-18 (plan #240):** migrated hooks (`hive-status-*.sh`, `hive-orchestrator.mjs`, `hive-agent-watcher.mjs`) and McpBridge (`index.ts`, `wait-for-message.js`, `wait-for-idle.js`) off `HIVE_API_KEY` env var onto `hive-key get` CLI. Plan #242 (2026-07-10) removed the shared-secret fallback everywhere.
