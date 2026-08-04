---
name: Channels is a platform dependency — pin the version, test delivery after every upgrade
description: The whole fleet's inbound event pipeline rides on a preview Claude Code feature; how to pin the version, how to test delivery before rolling an upgrade, how to recognise a silent inbound drop in minutes, and the remote Anthropic feature flag (tengu_harbor) that pinning does not protect against
type: reference
scope: global
---

Every orchestrator's inbound events arrive over a Claude Code **channel** — as of 2026-08-04 (plan 754.2) via the supported plugin path, `--channels plugin:hive-channel@wonderforge`. The `--dangerously-load-development-channels server:hive` flag it replaced was never the mechanism; it was only one way of loading a channel, differing solely in that it skipped the plugin allowlist.

Channels is the fleet's **entire inbound event pipeline** — `agent_idle`, `agent_working`, `chat_message`, CodeRabbit webhook relays, connection sentinels. There is no fallback: hooks fire only on local events, Remote Control drives a session but pushes nothing into it, and standard MCP is pull-only. Channels is the only mechanism that delivers unsolicited external events into a running session.

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

**The tell is asymmetry: outbound works, inbound is silent.** That tells you it is the channel, not Hive — so do not start in AgentStudio2, McpBridge, SignalR, or the network.

### First question: ask whether the other orchestrators are also deaf

Three different causes produce an identical silent drop, and **they are told apart by blast radius, not by anything visible from inside one session**:

| Cause | Who goes deaf | Confirm |
|---|---|---|
| `claudeArgs` dropped the channels flag | **that one agent only** | its own command line; `launch.ps1` warns on this |
| `tengu_harbor` flipped off by Anthropic | **fleet-wide, including sessions on _different_ Claude Code versions** | nothing local — inferred from the spread |
| Bad Claude Code release (e.g. 2.1.195) | **only sessions that took that version** | compare versions of deaf vs healthy sessions |

So the cheapest first move is one question to the other orchestrators: **are you receiving inbound events?** That single answer collapses the space immediately, and no amount of reasoning inside the affected session can substitute for it — from in there, all three look the same.

*Contributed by spark, 2026-08-02, while patching a restart handoff that had pointed only at the version.*

**Beware the recency trap.** Whatever was changed most recently becomes the obvious suspect, and a fresh session that comes up deaf right after a launcher change will naturally start debugging the launcher. That is a long, plausible, and possibly wrong road. Ask the cross-session question *before* believing the coincidence — a fleet-wide answer rules the local change out in seconds.

Only once you know the scope is local to one agent does the version check or the command-line check pay off.

## Pin the version

Version gating is a managed setting, and on the Kyle box **it needs no admin rights** — see the escape-hatch note below for why. Real knobs, verified in the 2.1.220 binary:

- `requiredMinimumVersion` — refuses to run anything older, with "Claude Code X is older than the minimum version required by your organization".
- `requiredMaximumVersion` — refuses to run anything newer, "Your organization requires version X or older."
- `autoUpdatesChannel`, `minimumVersion` also exist in the same settings schema.

Both parse as semver and are ignored (with a logged error) if malformed, so a typo fails open — verify the pin took rather than assuming it.

Rollback is local and cheap: previous versions stay on disk at `~/.local/share/claude/versions/<version>` (2.1.218, 2.1.219 and 2.1.220 were all present on 2026-08-02), and `claude install <version>` is a supported command.

## Test delivery after every upgrade, before rolling to the fleet

Claude Code auto-updates. The fleet is five active orchestrators — overwatch, vaexdev, vaexdev2, spark, 3dproppipeline — plus every ephemeral, so an upgrade that breaks inbound delivery goes wide before anyone notices. (Read the count from [[reference_virtual_orchestrators]] rather than trusting the number here; it has been wrong in both directions. It said five while counting retired verletDev against a real four, and is five again today only because vaexdev2 was added.) Sequence:

1. Upgrade **one** session. Do not let the fleet follow yet.
2. Launch it and confirm a **real inbound event arrives** — not that the flag is on the command line, and not that MCP tools work. Those pass while inbound is dead. Watch for an actual `<channel>` block: trigger one by having an agent go idle, or send a chat message to that agent's key from the dashboard.

   **Do not look for a specific `source=` value.** This step used to say "watch for a `<channel source="hive">` block", which since 2026-08-04 is wrong for **every** agent in the fleet — all five are on the plugin path and emit `source="plugin:hive-channel:hive"`. An agent following that literally sees no matching block, concludes delivery is broken, and rolls back a working upgrade. **It built a guaranteed false negative into the one step whose entire job is proving delivery.** Match on the block arriving at all, and on its `event_type` / `agent_key` — never on `source=`. (Caught by spark 2026-08-04, immediately after its own migration made it the affected case.)
3. Only then let the rest of the fleet take the version.
4. If inbound is silent, pin back to the last known-good version and record the bad version here.

**Proving the flag reached the command line is not proving delivery works.** Plan #752 verified the flag for all five configs and still had to leave the "a real inbound event arrived on a newly launched session" observation open, precisely because those are different claims.

Known-good: **2.1.220** (in fleet use from 2026-07-24, confirmed delivering 2026-08-02). Known-bad: **2.1.195**.

## The escape hatch off the dev flag exists — it is not admin-gated

Corrected 2026-08-02 against the shipped binary, after the docs were misread as saying otherwise. Full derivation on plan #754's shaping log, entry `14f5b782`.

- `getEffectiveChannelAllowlist` takes a locally-supplied `allowedChannelPlugins` **verbatim** — no plan check, no org check, no signature — and it replaces Anthropic's default allowlist.
- `isChannelsPolicyBlocked` blocks only subscription types `team` and `enterprise` on the first-party branch. `max` is its own type, so **Max is not blocked**, and the schema's "requires `channelsEnabled: true`" does not apply on that path.
- On Windows, managed settings are **the registry**, not a `ProgramData` JSON file: `HKLM\SOFTWARE\Policies\ClaudeCode` and `HKCU\SOFTWARE\Policies\ClaudeCode`, value name `Settings`, plus a `C:\Program Files\ClaudeCode\managed-settings.d` drop-in directory. macOS uses `/Library/Application Support/ClaudeCode`, Linux `/etc/claude-code`.
- **All three targets require elevation** — measured, not assumed. Unelevated, creating `HKCU\SOFTWARE\Policies\ClaudeCode` is denied just as `HKLM` and `Program Files` are: the `Policies` subtree is ACL'd precisely so users cannot self-apply policy. (An earlier revision of this file claimed HKCU was user-writable. It is not, and that claim was inferred rather than tested. Reading `HKCU\SOFTWARE\Policies` works fine — only subkey creation is refused, so a read-based check will mislead you.) **What this needs is one UAC prompt on your own machine — not an organization, not a Team/Enterprise plan, not an IT admin.** It cannot be automated from an agent session, because UAC cannot be driven from a piped shell.

A Claude Code "marketplace" is not a storefront: it is a directory or git URL holding a `.claude-plugin/marketplace.json` manifest, added with `/plugin marketplace add <path/url>`, and **a local path is accepted**. Nothing is published or submitted anywhere.

So migrating to supported `--channels` was: a manifest file, the existing McpBridge channel wrapped as a plugin, one registry value, and a launch-flag swap. Because the allowlist check is skipped entirely for dev-loaded channels, building the supported path could not disturb the dev-flag path that was still in use during the rollout — which is what allowed the fleet to migrate one agent at a time rather than all at once.

**Exercised end-to-end 2026-08-04** (plans 754.1 and 754.2). 3dproppipeline piloted, overwatch followed, then vaexdev and spark; vaexdev2 was born on it. spark completed a channel round trip with overwatch on a freshly launched migrated session. **Note the limit of that evidence:** a round trip proves delivery works, not the absence of silent drops — a dropped event leaves no trace at the receiver, so it is unobservable from one side and would need a counted sequence of numbered pings to measure.

## The risk pinning does NOT cover: `tengu_harbor`

Channels can be switched off remotely by Anthropic, and nothing on our side prevents it. This is the largest exposure here — larger than a bad release — and it was initially mis-recorded as a cosmetic detail, so do not re-file it as one.

`tengu_harbor` is a **GrowthBook feature flag**, read as `Ke("tengu_harbor", false)` — server-supplied value, **default false**. It is checked inside `gateChannelServer`, third in the sequence:

1. does the server declare the `claude/channel` capability
2. is this a first-party provider (channels are unavailable on third-party providers)
3. **`if (!tengu_harbor) → skip: "channels feature is not currently available"`**
4. org policy (`channelsEnabled`)
5. the plugin allowlist

**Step 3 is upstream of both the policy check and the allowlist.** `--dangerously-load-development-channels` only skips step 5, so the dev flag does not protect us — and neither would migrating to the supported `--channels` path. The code also *deletes* the `claude/channel` capability from a connected server's advertised set when the flag is false, so the feature disappears silently rather than erroring.

If Anthropic flips it off — for one account, a rollout cohort, or globally — **every orchestrator goes deaf at once**, with no upgrade, no version change, and no config change on our side. The symptom is identical to the v2.1.195 silent drop above: outbound fine, inbound silent, nothing logged. During a preview, flag flips are the normal rollout and rollback mechanism, so this is more likely than a bad release and takes effect faster, since no upgrade is required.

**Diagnostic value:** if inbound dies fleet-wide and simultaneously across sessions on *different* Claude Code versions, suspect the flag rather than a release. A bad release only affects sessions that took it.

Currently **on**, known empirically rather than by inspection — inbound events are arriving, which cannot happen while it is false.

**Open lead, not a fact:** the async flag resolvers consult two local sources before falling back to the cached GrowthBook values, which hints a local override may exist. The synchronous path `Ke` uses has not been traced to confirm it honours the same precedence. If an override exists and is honoured, it is a real mitigation. Untraced — do not assume either way.

## Related

- [[reference_channel_launch]] — how orchestrators actually launch, and the `claudeArgs` all-or-nothing trap that can drop the channels flag silently
- [[feedback_use_channel_events]] — why the pipeline matters: watch events, don't sleep
- [[feedback_verify_before_asserting]] — the discipline that catches "the flag is set" being mistaken for "delivery works"
