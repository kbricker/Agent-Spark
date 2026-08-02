---
name: Channels is a platform dependency — pin the version, test delivery after every upgrade
description: The whole fleet's inbound event pipeline rides on a preview Claude Code feature; how to pin the version, how to test delivery before rolling an upgrade, and how to recognise a silent inbound drop in minutes instead of hours
type: reference
scope: global
---

Every orchestrator launches with `--dangerously-load-development-channels server:hive`. That flag is the fleet's **entire inbound event pipeline** — `agent_idle`, `agent_working`, `chat_message`, CodeRabbit webhook relays, connection sentinels. There is no fallback: hooks fire only on local events, Remote Control drives a session but pushes nothing into it, and standard MCP is pull-only. Channels is the only mechanism that delivers unsolicited external events into a running session.

It is a **documented, official feature** (`https://code.claude.com/docs/en/channels`, `/channels-reference`), but the contract is explicitly unstable:

> Availability is rolling out gradually, and the `--channels` flag syntax and protocol contract may change based on feedback.

So treat Claude Code the way you would treat any pinned dependency. Recorded on plan #754, 2026-08-02.

## The failure mode that costs hours: silent inbound drop

**Claude Code v2.1.195 silently dropped inbound channel notifications** (GitHub issue #71792). Nothing errored. Sessions launched normally, the MCP server connected, tools worked, the dashboard looked healthy — and no agent event ever arrived.

Know this symptom cold, because it mimics a platform outage:

- Orchestrators sit idle while agents visibly work and finish on the dashboard.
- No `agent_idle` ever lands, so nothing drives the pipeline forward.
- Outbound is unaffected — `hive_send_message`, status updates and plan writes all succeed, which makes it *look* like Hive is fine.
- Nothing appears in any log, because from the session's perspective no event was ever offered.

**The tell is asymmetry: outbound works, inbound is silent.** If you are diagnosing "the orchestrator went deaf", check the Claude Code version *first*, before AgentStudio2, McpBridge, SignalR, or the network. It is the cheapest check and it has been the answer before.

## Pin the version

Version gating is a managed setting, and on the Kyle box **it needs no admin rights** — see the escape-hatch note below for why. Real knobs, verified in the 2.1.220 binary:

- `requiredMinimumVersion` — refuses to run anything older, with "Claude Code X is older than the minimum version required by your organization".
- `requiredMaximumVersion` — refuses to run anything newer, "Your organization requires version X or older."
- `autoUpdatesChannel`, `minimumVersion` also exist in the same settings schema.

Both parse as semver and are ignored (with a logged error) if malformed, so a typo fails open — verify the pin took rather than assuming it.

Rollback is local and cheap: previous versions stay on disk at `~/.local/share/claude/versions/<version>` (2.1.218, 2.1.219 and 2.1.220 were all present on 2026-08-02), and `claude install <version>` is a supported command.

## Test delivery after every upgrade, before rolling to the fleet

Claude Code auto-updates. The fleet is five orchestrators plus every ephemeral, so an upgrade that breaks inbound delivery goes wide before anyone notices. Sequence:

1. Upgrade **one** session. Do not let the fleet follow yet.
2. Launch it and confirm a **real inbound event arrives** — not that the flag is on the command line, and not that MCP tools work. Those pass while inbound is dead. Watch for an actual `<channel source="hive">` block: trigger one by having an agent go idle, or send a chat message to that agent's key from the dashboard.
3. Only then let the rest of the fleet take the version.
4. If inbound is silent, pin back to the last known-good version and record the bad version here.

**Proving the flag reached the command line is not proving delivery works.** Plan #752 verified the flag for all five configs and still had to leave the "a real inbound event arrived on a newly launched session" observation open, precisely because those are different claims.

Known-good: **2.1.220** (in fleet use from 2026-07-24, confirmed delivering 2026-08-02). Known-bad: **2.1.195**.

## The escape hatch off the dev flag exists — it is not admin-gated

Corrected 2026-08-02 against the shipped binary, after the docs were misread as saying otherwise. Full derivation on plan #754's shaping log, entry `14f5b782`.

- `getEffectiveChannelAllowlist` takes a locally-supplied `allowedChannelPlugins` **verbatim** — no plan check, no org check, no signature — and it replaces Anthropic's default allowlist.
- `isChannelsPolicyBlocked` blocks only subscription types `team` and `enterprise` on the first-party branch. `max` is its own type, so **Max is not blocked**, and the schema's "requires `channelsEnabled: true`" does not apply on that path.
- On Windows, managed settings are **the registry**, not a `ProgramData` JSON file: `HKLM\SOFTWARE\Policies\ClaudeCode` and `HKCU\SOFTWARE\Policies\ClaudeCode`, value name `Settings`, plus a `C:\Program Files\ClaudeCode\managed-settings.d` drop-in directory. macOS uses `/Library/Application Support/ClaudeCode`, Linux `/etc/claude-code`. **`HKCU` is user-writable — no admin, no organization.**

A Claude Code "marketplace" is not a storefront: it is a directory or git URL holding a `.claude-plugin/marketplace.json` manifest, added with `/plugin marketplace add <path/url>`, and **a local path is accepted**. Nothing is published or submitted anywhere.

So migrating to supported `--channels` is: a manifest file, the existing McpBridge channel wrapped as a plugin, one registry value, and a launch-flag swap. The allowlist check is skipped entirely for dev-loaded channels, so building the supported path cannot disturb the dev-flag path still in use.

**Not yet exercised end-to-end**, and `tengu_harbor` — a remote feature flag feeding the `/channels` status view's `disabled` field — is unexamined and outside our control.

## Related

- [[reference_channel_launch]] — how orchestrators actually launch, and the `claudeArgs` all-or-nothing trap that can drop the channels flag silently
- [[feedback_use_channel_events]] — why the pipeline matters: watch events, don't sleep
- [[feedback_verify_before_asserting]] — the discipline that catches "the flag is set" being mistaken for "delivery works"
