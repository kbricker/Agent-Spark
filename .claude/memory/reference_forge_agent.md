---
name: reference-forge-agent
description: Forge — the persistent infra agent for VaEx/Hive. What it is, its remit (deploys, GCP, build promotion), when to route work to it vs doing it yourself vs escalating to overwatch, and the hard security rules.
metadata:
  type: reference
scope: global
---

# Forge — the infrastructure agent

**What it is:** a persistent named Hive agent (`forge`, remote, infra archetype). Per plan #280 it boots Offline and must be explicitly woken (`hive_agent_wake({agentKey: "forge"})`) and slept after use (`hive_agent_sleep`). Its dedicated workspace is the infra repo clone at `C:\projects\rider\vaex\infra` — the repo that owns every deploy and promotion script. Never force-sleep a Working forge; wait for idle.

## Remit (what forge owns)

- **VaEx server deploys** — `deploy-dev1.ps1` (vaex-dev1), `deploy-stage1.ps1` (vaex-staging).
- **Gateway deploys** — `deploy-gateway.ps1` (vaex-gateway; fixed 2026-07-12, scp-staging pattern).
- **Hive platform deploys** — `deploy-hive.ps1` (vaex-hive), normally driven by overwatch via its deploy-hive skill with forge awake as support.
- **VaEx build promotion** (new 2026-07-12, plans #586/#587) — the `promote-vaex-build` skill in `infra/.claude/skills/`: `package-build.ps1` zips a smoke-tested Unity build; `promote-build.ps1` uploads to the staging gametool, makes it primary, flips gateway routing (current→staging, next→dev), and bumps/commits/pushes `bundleVersion` in VaEx4. The build number source of truth is `ProjectSettings.asset` `bundleVersion` on VaEx master.
- **Release notes** — living file `infra/release-notes/{version}.md`; published to the `ve-releases` Slack channel (Hive outbox) at promotion time.
- **GCP operations** — VM lifecycle, logs, SSH (as `claude-infra@e-parsec-483816-k6`), Secret Manager *reads*. Bootstrap recipes for new infra live in [[GCP infra agent bootstrap recipe (from Forge)]].

## Auth facts forge (and you) rely on

- **VaEx deploy key** — header `X-Deploy-Key` on the staging/dev gametool APIs and the gateway admin API. Raw key: Windows Credential Manager (`VaEx/deploy`) locally + GCP secret `vaex-deploy-key`. Scripts resolve it from the credential store; it is never passed as an arg/env or printed.
- **Hive identity keys** — every agent authenticates to Hive with its own provisioned identity (no shared secrets since wfa2 plan #242). VaExServer's webhooks use the `vaexserver` identity (GCP secret `vaexserver-hive-key`).
- **claude-infra SA limits** — it cannot create secrets or change IAM. Those operations need Kyle's `gcloud auth login` + `--account=kyle@wonderforge.io`, typically driven from the overwatch session.

## Routing: forge vs yourself vs overwatch

- **Route to forge:** anything that runs a deploy script, touches a VM, promotes a build, or reads GCP state. Wake → message with a concrete briefing → watch (`hive_channel_watch`) → sleep when idle.
- **Do it yourself (vaexdev):** game code, Unity content, VaEx PRs, gameplay data — forge is not a game dev.
- **Escalate to overwatch:** Hive platform changes (AgentStudio2/McpBridge/RemoteAgent), agent identity provisioning, Slack channel allowlisting, anything hitting the claude-infra IAM wall.

## Credentials

Credential-level work is forge's exclusively — see [[feedback_credentials_radioactive]]. forge holds the detailed operating rules in its own memory; everyone else routes credential work to forge and never touches a credential directly.

## Gotcha

Infra `.ps1` scripts run under **Windows PowerShell 5.1** via `powershell -File` — no PS7 operators (`??`, ternary), ASCII-only content, and git's stderr must be exit-code-judged, not stream-redirected. Test with `powershell -File`, not pwsh.
