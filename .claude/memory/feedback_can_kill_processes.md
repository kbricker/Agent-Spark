---
name: Kill only the specific process you spawned, never by image name
description: You may kill a process you started, but NEVER use taskkill //IM dotnet.exe or //IM claude.exe — those are blanket kills that nuke Kyle's other sessions
type: feedback
scope: global
---

You may kill processes you spawned yourself (e.g. a RemoteAgent or AgentStudio2 server you just started in the background). But you MUST target them by PID, not by image name.

**FORBIDDEN — never run these:**
- `taskkill //F //IM dotnet.exe` — kills every .NET process including verletdev, other AgentStudio2 instances, any running ephemeral Claude Code dotnet hosts
- `taskkill //F //IM claude.exe` — kills every Claude Code session Kyle has open, destroying their state and conversation context
- Any `//IM <image>` form that targets a shared binary

**Required pattern:**
- When you start a process in the background, capture its PID from the Bash tool's returned metadata.
- To stop it later: `taskkill //F //PID <that_pid>` — targets that one process only.
- If you lost the PID, use `wmic process where "CommandLine like '%<unique-flag>%'"` or check `tasklist` to identify the exact PID before killing.

**Why:** On 2026-04-17 I ran `taskkill //F //IM dotnet.exe` and `taskkill //F //IM claude.exe` to clean up after a local Playwright test. It killed my own session, Kyle's verletdev Claude Code session, and every other dotnet process on the machine — destroying their in-flight state and contexts. Kyle: "that was stupid as shit... NEVER FUCKING DO THIS."

**How to apply:** Before running any `taskkill`, check the flags. If it's `//IM` against a shared image name (dotnet, claude, node, powershell, pwsh, etc.), STOP — switch to PID-based killing. Blanket kills by image name are never acceptable on Kyle's workstation because he runs many concurrent Claude Code sessions and dev servers.
