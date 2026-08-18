---
name: Never kill Chrome by image or process name
description: NEVER kill Chrome by any means — Kyle works on this machine and blanket kills destroy his open work
type: feedback
scope: global
---

NEVER kill Chrome. Do not run `taskkill //IM chrome.exe`, `Stop-Process -Name chrome`, or any image-name / process-name kill that targets `chrome.exe`. Kyle is actively using this machine and his browser holds live work — a blanket kill blows it all away. This already happened more than once and made him (rightly) angry.

**Why:** `//IM chrome.exe` / `-Name chrome` kill EVERY Chrome process, including Kyle's real browser windows, not just any headless instance an agent spawned. There is no safe blanket Chrome kill on a machine a human is using.

**How to apply:**
- Never issue a kill/taskkill/Stop-Process that matches Chrome by image or process name. Full stop.
- For headless-Chrome test harnesses (CDP/DevTools), close ONLY the instance you launched, via its own debug socket: send `Browser.close` over the websocket you opened. That targets your one process, not Kyle's browser. If unsure it's scoped, just leave the headless instance running — a stray headless process is harmless; killing Kyle's browser is not.
- This is the general form of [[feedback_can_kill_processes]]: only ever touch the specific PID/instance you spawned; never a blanket image-name kill (`dotnet.exe`, `claude.exe`, `chrome.exe`, anything).
