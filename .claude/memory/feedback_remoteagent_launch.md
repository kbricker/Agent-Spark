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
- To start: Tell Kyle to use his desktop shortcut
- Shortcut location: `C:\Users\kyleb\OneDrive\Desktop\RemoteAgent.lnk`
