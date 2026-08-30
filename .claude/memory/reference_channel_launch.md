---
name: How to launch orchestrator agents with Hive channel events
description: "Five PRIMARY agents: .lnk launchers, plugin channel; 3dpp is RemoteAgent-hosted; read for claudeArgs or deaf agents"
type: reference
scope: role:orchestrator
---

Primary agents launch through **`primary-launcher/launch.ps1`** (the directory was `virtual-launcher/` until 782.31 renamed it with the class), which resolves the agent's identity key from Windows Credential Manager, assembles the `claude` arguments, and runs `claude` in the agent's working directory. It is launch-time only — nothing stays resident once the session is up.

Wired up today: **overwatch, vaexdev, vaexdev2, spark, finley** — each has a `configs/<key>.json` and a desktop shortcut. That is every PRIMARY agent, which is not the same set as every orchestrator: finley (added 2026-08-18, plan 929) launches exactly like the rest but composes no `orchestrator` role, so he does not hold this memory. **3dproppipeline has no launcher any more** — 782.31 reclassified it remote, so RemoteAgent starts it and a channel problem there is never a launcher problem (its launcher config and shortcut were removed with the move). **codexhive is NOT wired up**: a `Hive/codexhive` credential exists in the store, but there is no config and no shortcut, so `-Agent codexhive` exits 2. That is deliberate — codexhive is completed R&D and currently unused; to revive it, add `configs/codexhive.json` and an entry in `shortcuts/setup.ps1`. **verletDev** retired 2026-07-09 and its config was deleted 2026-08-16 (782.20); it would have launched on the legacy channel path with no model or effort flags.

**Preferred (desktop icons):** double-click the `.lnk` for your agent. One exists for every key listed above — `setup.ps1`'s `$agents` array is what creates them, so read that rather than any list transcribed here. They invoke `C:\Projects\wfa2\primary-launcher\shortcuts\primary-launcher.cmd <agent-key>`, which calls `launch.ps1`.

**Preferred (terminal):**

```powershell
powershell -ExecutionPolicy Bypass -File C:\Projects\wfa2\primary-launcher\launch.ps1 -Agent <agent-key>
```

`<agent-key>` names `configs/<agent-key>.json`; filenames are lowercased, and the config's own `agentKey` field is authoritative for the Hive identity (so `-Agent verletdev` resolves identity `verletDev`).

**Debug-only direct launch:**

```bash
claude --dangerously-load-development-channels server:hive
```

A bare session with no identity injection. Channel notifications (`agent_idle`, `agent_working`, `chat_message`) still flow, because they are handled inside the MCP server rather than by the launcher — but only if the `hive` server can see `HIVE_AGENT_KEY` in its env, which a direct launch relies on `.mcp.json` for.

## Remote slash commands: use native Remote Control

**Plan #752 (2026-08-02) retired the `hive <verb>` mechanism.** `hive compact` typed into Hive dashboard chat is now ordinary prose that reaches the agent as text — it triggers nothing.

For `/compact`, `/clear`, `/model <name>` and friends from a phone or the web, use **Claude Code's native Remote Control**, which covers a superset of the old whitelist plus mobile push notifications and remote permission approval. Requires Pro/Max/Team/Enterprise and workspace trust accepted for the project directory.

## API key resolution (plan #239)

On the Kyle box, **Windows Credential Manager is the primary source** — target `Hive/<agentKey>`, one entry per agent.

**There is no shared-secret fallback.** Plan #242 retired the shared `HIVE_API_KEY` env var; a value in that variable today is always a *per-agent identity key*, never a shared secret. So `HIVE_API_KEY` is still a live mechanism — it just carries something different from what it carried before #242. Do not read "no shared secret" as "no env var".

Install with `node C:\Projects\wfa2\hive-key\dist\index.js install <agent>` after generating a key at the dashboard's `/admin/identities.html`. **Use the authoritative mixed-case form the dashboard shows** (`verletDev`, not `verletdev`) — not because the credential lookup needs it (Windows credential target names are case-insensitive) but because the value is sent to Hive verbatim as the agent's identity.

Who resolves it how, and in what order:

| Client | Resolution |
|---|---|
| `launch.ps1` | Credential Manager only, read directly via the Win32 `CredReadW` API. No env fallback — a missing credential warns and launches unauthenticated. |
| `hive-key` | The **writer**, via `keytar`. Byte-compatible with the `CredReadW` reader. |
| Hooks | `hive-key get <agent>` (2s timeout). |
| `McpBridge`, `wait-for-*` | `hive-key get <agent>` **first**; the injected `HIVE_API_KEY` env value is used **only if that lookup returns nothing** (`McpBridge/src/index.ts` `resolveApiKey`, and the same shape in `wait-for-idle.js` / `wait-for-message.js`). It logs "no local hive-key store" when it takes the env path. |

That precedence is the important part: on the Kyle box the store wins, so a stale env value cannot shadow a correctly-installed credential. The env path exists for agents spawned somewhere with no local store — both AgentStudio2 and RemoteAgent set it at spawn — so spawned children land on it by design, while local orchestrators never do.

**Gotcha if you ever hand-roll a credential reader:** keytar writes the secret as UTF-8 bytes while the Win32 `CREDENTIAL` struct is otherwise marshalled as Unicode. Decoding the blob with `Marshal.PtrToStringUni` yields mojibake at exactly half the true length — a 44-character key reads back as 22 garbage characters, which looks like a truncated key rather than a decoding fault. Copy the bytes and decode UTF-8 explicitly.

## Details

- `server:hive` references the `hive` key in `.mcp.json` — the merged McpBridge server exposing both tools and the `claude/channel` capability.
- Channel features arm only when the `hive` server sees `HIVE_AGENT_KEY` in its env. The launcher injects it; a direct launch relies on `.mcp.json`.
- VM agents (NightWatch) don't set `HIVE_AGENT_KEY` and stay dormant on the channel.
- For unattended operation, add `--dangerously-skip-permissions` to the agent's `claudeArgs` in its config JSON.
- `claudeArgs` is **all-or-nothing** — a config that sets it must restate every flag it wants, including whichever channel flag that agent is on (`--dangerously-load-development-channels server:hive` or `--channels plugin:hive-channel@wonderforge`). Dropping the channel flag detaches the agent from the entire inbound event pipeline; `launch.ps1` warns when the resolved arguments omit both. This bites hardest on a config that *already* had `claudeArgs` — migrating overwatch meant restating `--chrome` and `-n Overwatch` alongside the new flag, whereas 3dproppipeline had no `claudeArgs` at all so its migration was purely additive.
- That flag is a **preview-contract dependency on Claude Code itself**. Before upgrading Claude Code, and whenever an orchestrator has gone deaf while outbound still works, read [[recall:reference_channels_platform_dependency]] — it covers version pinning, the post-upgrade delivery test, the silent-inbound-drop symptom, and the route off the dev flag.

## The whole fleet is on the supported `--channels` path

**Every active Primary agent launches with `--channels plugin:hive-channel@wonderforge` and no dev flag (since 2026-08-04, plan 754.2):** `overwatch`, `vaexdev`, `vaexdev2`, `spark`, and `finley`, which was BORN on that path 2026-08-18 (plan 929) rather than migrated — so it has no `_rollback` hive block in its workspace `.mcp.json` and no dev-flag state to revert to. 3dproppipeline was the pilot on 2026-08-03 (754.1), overwatch followed the same day, vaexdev and spark migrated on 2026-08-04, and vaexdev2 was born on it; 782.31 then moved 3dproppipeline off the launcher entirely (remote class, RemoteAgent-hosted, no channel). (verletDev is retired as of 2026-07-09 and codexhive is parked — neither launches, so neither is on either path.)

**The dev flag still works and is NOT deprecated.** `launch.ps1`'s guard accepts either form and warns only if a config has neither (or confusingly, both). Keep the rollback path in mind: every migrated workspace's `.mcp.json` carries its original `hive` server definition in a `_rollback` key, and reverting means restoring that block into `mcpServers` **and** reverting `claudeArgs` in the launcher config. Both halves, or you get an agent with no channel at all.

**What migrating actually buys:** the launch-time acknowledgement prompt disappears. On the dev flag a session blocks on a keypress before it starts, so **an agent launched unattended never comes online at all**. It buys nothing against `tengu_harbor`, which sits upstream of both paths — see [[recall:reference_channels_platform_dependency]].

**Delivery between two migrated agents is proven in both directions** (2026-08-03, overwatch ↔ 3dproppipeline, each confirming the other's `source=` attribute). Note the limit of that proof: a round trip shows delivery works, it does *not* show the absence of silent drops — a dropped event leaves no trace at the receiver, so that property is unobservable from one side and would need a counted sequence of numbered pings to measure.

Migrating an agent takes three changes together. Doing only the first is the failure that cost an iteration:

1. `claudeArgs` in its `configs/<key>.json` → `["--channels", "plugin:hive-channel@wonderforge"]`
2. **Remove the `hive` server from its workspace `.mcp.json`.** The plugin must be the *sole* definition. Two servers both named `hive` collide, the plugin's copy loses, and you get the worst failure shape available: tools keep working, so the agent looks healthy, while the channel never arms and no event ever arrives.
3. Add `mcp__plugin_hive-channel_hive__*` to its `.claude/settings.json` allow list. Plugin-provided tools are namespaced, so the existing `mcp__hive__*` rule cannot match them and **every** Hive call prompts.

Two consequences that surprise people:

- **Channel blocks arrive as `source="plugin:hive-channel:hive"`, not `source="hive"`.** Anything matching on the literal string — docs, hooks, parsing, the MCP server's own instructions — is wrong for a migrated agent.
- **`/mcp` output is not evidence either way.** The capability report reads a different, non-override-aware allowlist than the one that actually gates delivery, so it can claim the channel capability is absent while events flow perfectly. The only proof is a real inbound block arriving.

One-time machine setup, already done: the marketplace lives at `C:\Projects\wfa2\claude-plugins` (added by local path — nothing is published anywhere), and `allowedChannelPlugins` is in the managed-settings policy key. **That policy write requires elevation** — `HKCU\SOFTWARE\Policies` is ACL'd, so it is a UAC prompt, not a user-writable key. `claude-plugins/setup-channel-policy.ps1` performs it and takes `-Remove` to undo.

## Historical notes

- **2026-04-17 (plan #183):** merged the separate `hive-channel` MCP server into `hive` (McpBridge). The old `server:hive-channel` flag now errors with "no MCP server configured with that name".
- **2026-04-17 (plan #188):** introduced the `virtual-launcher` wrapper + desktop icons.
- **2026-04-18 (plan #239):** moved the launcher's API key source to Windows Credential Manager. Desktop `.lnk` launches no longer depend on `HIVE_API_KEY` in the shell that spawned Explorer.
- **2026-04-18 (plan #240):** migrated hooks and McpBridge off the `HIVE_API_KEY` env var onto the `hive-key get` CLI. Plan #242 (2026-07-10) removed the shared-secret fallback everywhere.
- **2026-08-02 (plan #752):** retired the Node wrapper. `node-pty`, `keytar`, the SignalR client, the whole Node project, and server-side `VirtualSlashCommandService` are gone; the launcher is `launch.ps1`. The desktop shortcuts and their paths were deliberately left unchanged. Remote slash commands are now native Remote Control.
- **2026-08-29 (plan 782.31):** renamed the class virtual → Primary and the launcher directory `virtual-launcher/` → `primary-launcher/` (shortcuts regenerated by `setup.ps1`); 3dproppipeline reclassified to remote and left the launcher; hivedev01 retired to a subagent.
