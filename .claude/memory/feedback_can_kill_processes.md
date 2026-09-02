---
name: Kill only the specific process you spawned, never by image name
description: Reaching for taskkill? Kill only what you started, by PID — image-name kills are denied and provenance is still on you
type: feedback
scope: global
---

You may kill processes you spawned yourself (a server or RemoteAgent you started in the background), but only by PID: capture it at spawn from the tool's returned metadata, then `taskkill //F //PID <pid>` (Bash) or `Stop-Process -Id <pid>` (PowerShell). If you lost the PID, identify the exact one via `tasklist` or a CommandLine filter before killing.

**Why:** on 2026-04-17 a `taskkill //F //IM dotnet.exe` + `//IM claude.exe` cleanup killed Kyle's other live Claude sessions and every dotnet process on the box, destroying their in-flight state. Kyle: "NEVER FUCKING DO THIS." Blanket image/name kills are never acceptable on a machine running many concurrent sessions and dev servers.

**How to apply:** `hooks/kill-guard.mjs` (782.32) DENIES the common image/name-based kill forms on both shells, so the pattern list no longer lives here — but it is a backstop against the reflexive blanket kill, not a complete guarantee (exotic spellings can slip it). The rule itself, and the provenance half the hook cannot see, stay yours: the PID you target must be one you started. See [[feedback_never_kill_chrome]] for the stricter Chrome rule.
