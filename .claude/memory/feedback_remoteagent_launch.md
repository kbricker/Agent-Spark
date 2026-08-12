---
name: RemoteAgent launch method
description: NEVER launch RemoteAgent from bash — overwatch owns starting/stopping the WPF app; how to do it properly
type: feedback
scope: global
---

NEVER try to launch RemoteAgent.exe from bash — it fails. Kyle's desktop shortcut handles it correctly.

**Why:** Bash and PowerShell don't always inherit user-level env vars properly. Multiple failed attempts wasted time.

**How to apply:**
- To stop: `powershell -Command "Stop-Process -Name RemoteAgent -Force"`
- To start: `Start-Process -FilePath "C:\Users\kyleb\OneDrive\Desktop\RemoteAgent.lnk"` from the **PowerShell** tool. Launching the `.lnk` rather than the `.exe` is the point — the shortcut carries the working directory and environment the app needs, which is what bash was failing to supply.
- Shortcut location: `C:\Users\kyleb\OneDrive\Desktop\RemoteAgent.lnk`

**Corrected 2026-08-11.** This file previously said "tell Kyle to use his desktop shortcut", and overwatch followed it — stopping RemoteAgent mid-task and then waiting on Kyle to press an icon. Kyle: *"of course you can start it."* The real constraint was only ever **bash**, never permission; PowerShell launching the shortcut works and is overwatch's to run. A rule that reads as an authority limit when it is actually a tooling limit costs a round trip every time, and it cost one during a half-finished deploy.

## `deploy-hive.ps1` has two ways to ship something other than what you merged

Both print `Deployment complete!`. Both happened on 2026-08-11, hours apart, to the same epic.

**1. It does not touch RemoteAgent.** The script ships AgentStudio2 to the VM; RemoteAgent is a WPF app on Kyle's machine. Plan #852's server half went live while the RemoteAgent half sat inert for **every remote agent** — the running binary predated the branch by 16 hours. If a change touches `RemoteAgent/`, stop it, `dotnet build RemoteAgent/RemoteAgent.csproj` (Debug is what runs), and restart it.

**2. It builds from the LOCAL working copy, not from origin.** Merging on GitHub deploys nothing. After merging PR #129 and deploying immediately, the local clone was still two commits behind and the fix never shipped — the subsequent `PUT /config` returned `{"status":"saved"}` and the field read back unchanged. **`git -C C:/Projects/wfa2 pull` before every deploy**, and confirm `git log -1` is the merge you expect.

**The tell in both cases is that everything reports success.** The deploy says complete, the write says saved, the service restarts cleanly — and the behaviour is the old behaviour. When a change you just merged has no effect in production, suspect the deploy before suspecting the code; see [[feedback_prove_the_check_ran]], which is the same shape one layer down.
