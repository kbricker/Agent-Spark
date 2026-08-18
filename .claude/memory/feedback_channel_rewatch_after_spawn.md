---
name: An empty channel watch list looks exactly like a quiet fleet
description: Check hive_channel_watching before calling silent agents stuck — process boundaries clear the process-local watch list
type: feedback
scope: role:orchestrator
---

**Watch lists are process-local — any process boundary clears them.** A restart empties the list on either launch path (dev flag or `--channels plugin:hive-channel@wonderforge`); this is expected, not a migration symptom (confirmed 2026-08-03: both overwatch's and its own list read `(none)` after restart, though it knew it had `3dproppipeline` watched before).

An empty watch list produces **exactly the same observation as a quiet fleet** — silence, no error, no warning. Don't diagnose silence as "agents still working" or a channel fault until `hive_channel_watching` has been checked.

**Coverage:**
- **Planned restart** is handled: `prepare-restart` requires a watch-list section in the handoff, and the CLAUDE.md consumption block re-establishes it and polls each agent once (events during the restart window are lost). That skill is `scope: global` and byte-identical to canonical — do not "discover" this gap again and propose fleet work for it.
- **Unplanned restart** (crash, hang, reboot) is NOT covered — no handoff was written, so nothing on disk names who was being coordinated. Raised 2026-08-03, unresolved; Kyle's call whether continuously-maintained state is worth it.

*(The kill-drop bug #149 this file was first written for is FIXED — since 2026-04-17, commit `b78697a`, plan #183; `hive_kill_agent` does not drop watch membership. Don't add defensive re-watches on that basis, and don't re-file it.)*
