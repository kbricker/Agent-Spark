---
name: reference_desk_pc_monitor2_wake_drop
description: "Kyle's desk PC (Thucydides, Precision 5860, RTX A1000) — Display 2 is the Dell S2725DS on HDMI; it drops off the bus for ~10 s at nearly every Windows display wake from screen-off; how it was diagnosed 2026-09-22"
metadata: 
  node_type: memory
  type: reference
  originSessionId: f7b133de-0e98-46d6-a8dc-c7850c3af0f4
  modified: 2026-09-22T20:27:05.316Z
---

Kyle's desk PC "Thucydides" (Dell Precision 5860 Tower, RTX A1000, mini-DP outputs only) drives two monitors over HDMI: Display 1 = Dell S3425DW (34" ultrawide, firmware M3C101), Display 2 = Dell S2725DS (27", firmware M2C101, made 2025 wk15, HDMI 1 input, no USB upstream so DDPM cannot flash it). Windows "turn off display after" is 10 min on AC.

Diagnosed 2026-09-22 (Kyle: "monitor 2 randomly loses power briefly, for months"): the S2725DS is "surprise removed as missing on the bus" (Kernel-PnP/Device Management event 1010) 458 times in 6 months, solo, never the S3425DW. 448 of 458 fall within 3 s of a Kernel-Power event 566 session transition type 1→0 (display wake, reason 31/32 = user input), zero at display-off. 451 of 604 display wakes trigger it, most reliably after 1–120 min of screen-off. Outage lasts 9–13 s (median 10.3 s) measured from the 1010 event to the DDPM re-enumeration line ("Update_DeviceChanged() executed MonitorInfo AliasDeviceName = DELL_S2725DS") in C:\ProgramData\Dell\DDPM.Subagent\DDPMSubagent.0N.log (locked while running; open with FileShare.ReadWrite). Kernel-PnP/Configuration and the System log show nothing for these; no GPU TDRs.

Useful logs for monitor hot-plug work on any Windows 11 box: Kernel-PnP/Device Management 1010 = removal (no arrival event), Kernel-Power 566 EventData PreviousSessionType/NextSessionType (1 = display off session, 0 = display on) with Reason (12 idle timeout, 31/32 user input, 6 display burst). Display numbering: `\\.\DISPLAYn` from QueryDisplayConfig/EnumDisplayDevices is the number Windows Settings shows. Scripts lived in the 2026-09-22 spark scratchpad, not kept.

Kyle's complaint is NOT this wake dropout: he says the blink happens mid-work "all the time" and idle wakes seem fine. Only 10 solo removals in 6 months fall outside a wake, so the mid-work blink never detaches the monitor from the bus and never reboots its scaler (a reboot would log 1010 and take ~10 s). It is therefore invisible to Windows: either backlight/panel power inside the monitor, or the HDMI signal blipping with hot-plug held. DDPM polls the S2725DS over DDC/CI about every 8 s (VcpCore "Watching" triggers), reads only. Next steps at time of writing: Kyle to report LED behaviour, Dell logo, duration and a clock time of a blink; test with a native mini-DP to DP cable; if it persists on DP, Dell 3-year warranty (built 2025 wk15).
