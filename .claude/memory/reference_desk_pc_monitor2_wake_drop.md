---
name: reference_desk_pc_monitor2_wake_drop
description: "Kyle's desk PC (Thucydides, Precision 5860, RTX A1000) — the 27in Dell S2725DS drops off the bus for ~10 s at most Windows display wakes from screen-off; Kyle never notices it (his screen-blink complaint is the ultrawide); how it was diagnosed 2026-09-22"
metadata: 
  node_type: memory
  type: reference
  originSessionId: f7b133de-0e98-46d6-a8dc-c7850c3af0f4
  modified: 2026-11-11T21:36:31.382Z
---

Kyle's desk PC "Thucydides" (Dell Precision 5860 Tower, RTX A1000, mini-DP outputs only) drives two monitors through mini-DP-to-HDMI adapters (WmiMonitorConnectionParams VideoOutputTechnology 4 = DVI-type TMDS for both; a native DP link reads 10): Dell S3425DW (34" ultrawide, EDID code DELD194, firmware M3C101, made 2025 wk17) and Dell S2725DS (27", EDID code DELD17E, firmware M2C101, made 2025 wk15, HDMI 1 input, no USB upstream so DDPM cannot flash it). Windows "turn off display after" is 10 min on AC. Display numbers are not stable identifiers: this note said Display 1 = ultrawide on 2026-09-22, but on 2026-11-11 `\\.\DISPLAY1` was the 27" — identify monitors by EDID code, and ask Kyle which screen by size, never by number.

Diagnosed 2026-09-22 (Kyle: "monitor 2 randomly loses power briefly, for months"): the S2725DS is "surprise removed as missing on the bus" (Kernel-PnP/Device Management event 1010) 458 times in 6 months, solo. 448 of 458 fall within 3 s of a Kernel-Power event 566 session transition type 1→0 (display wake, reason 31/32 = user input), zero at display-off. 451 of 604 display wakes trigger it, most reliably after 1–120 min of screen-off. Outage lasts 9–13 s (median 10.3 s) measured from the 1010 event to the DDPM re-enumeration line ("Update_DeviceChanged() executed MonitorInfo AliasDeviceName = DELL_S2725DS") in C:\ProgramData\Dell\DDPM.Subagent\DDPMSubagent.0N.log (locked while running; open with FileShare.ReadWrite). Kernel-PnP/Configuration and the System log show nothing for these; no GPU TDRs. Recount 2026-11-11 (1010 messages matching DISPLAY\DELD17E): 1539 since June 2025; 677 of 906 since Feb 2026 (when the System log's 566 events begin) within 3 s of a wake. The ultrawide (DISPLAY\DELD194) also has 592 removals of its own since June 2025, almost none at a wake.

Useful logs for monitor hot-plug work on any Windows 11 box: Kernel-PnP/Device Management 1010 = removal (no arrival event), Kernel-Power 566 EventData PreviousSessionType/NextSessionType (1 = display off session, 0 = display on) with Reason (12 idle timeout, 31/32 user input, 6 display burst). Current mode per display: EnumDisplayDevices + EnumDisplaySettings via Add-Type; EDID name, code and build week: WmiMonitorID. Scripts were not kept.

Kyle never notices this wake dropout — on 2026-11-11 he said he has never had issues with the 27". The September session pinned his mid-work blink on the 27" and aimed its next steps (DP cable, warranty) at the wrong monitor; the blink is the ultrawide — see [[reference_desk_pc_ultrawide_blink]]. DDPM polls the S2725DS over DDC/CI about every 8 s (VcpCore "Watching" triggers), reads only.
