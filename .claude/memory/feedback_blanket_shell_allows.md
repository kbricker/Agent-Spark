---
name: feedback-blanket-shell-allows
description: Kyle wants blanket Bash + PowerShell allows in orchestrator settings — endless per-command permission prompts are unacceptable
metadata:
  type: feedback
scope: global
---

Kyle (2026-07-09, mid-#538 validation): "why are you asking for 1000 permissions? you should have access to all bash, all powershell etc. the endless permissions requests is nonsense."

**Why:** Orchestrators run dozens of shell commands per task. Narrow one-off rules (`PowerShell(Get-Process *)` etc.) accumulate in settings.local.json and every novel command still prompts, blocking autonomous work.

**How to apply:** Keep bare `"Bash"` AND bare `"PowerShell"` in the project `.claude/settings.json` allow list (overwatch has both as of 2026-07-09). Never add narrow per-command shell rules on top — they're redundant noise. If a new orchestrator or workspace starts prompting for shell commands, add the blanket allows immediately rather than approving one-offs. Headless agents need the blanket allows in their own settings too — they can't self-escalate mid-run.
