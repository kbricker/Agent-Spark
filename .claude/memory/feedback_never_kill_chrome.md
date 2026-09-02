---
name: Never kill Chrome by image or process name
description: Reaching to kill Chrome — even by PID, even a wedged tab? Never; only scoped CDP Browser.close (kill-guard blocks names)
type: feedback
scope: global
---

NEVER kill Chrome — not by image name, not by process name, and not by PID either. Kyle works on this machine and his browser holds live work; a Chrome kill blows it away. This already happened more than once and made him (rightly) angry.

**How to apply:** `hooks/kill-guard.mjs` (782.32) denies the common name-based kill forms on both shells — a backstop, not a guarantee — and a PID is opaque to it entirely, so the rule stays yours in full: never target a PID that belongs to Chrome, and never reach for a spelling the guard happens to miss. For headless-Chrome test harnesses (CDP/DevTools), close ONLY the instance you launched, via its own debug socket: send `Browser.close` over the websocket you opened. If unsure it's scoped, leave it running — a stray headless process is harmless; killing Kyle's browser is not. This is the strict form of [[feedback_can_kill_processes]].
