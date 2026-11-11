---
name: reference_desk_pc_ultrawide_blink
description: "Kyle's desk-PC screen that 'blanks out momentarily' is the BIG screen (Dell S3425DW 34in ultrawide), never the 27in; Windows logs nothing for the blink; next step a native mini-DP to DP cable, then warranty"
metadata:
  node_type: memory
  type: reference
  originSessionId: 0858899d-0dab-4eda-aa10-c17ded878874
  modified: 2026-11-11T21:35:46.840Z
---

Kyle's complaint — the desk-PC screen "blanks out momentarily", at random, many times a day — is the big screen, the Dell S3425DW 34" ultrawide (EDID code DELD194, made 2025 wk17). On 2026-11-11 he said he has never had issues with the 27" S2725DS. The September 2026 diagnosis wrongly pinned the blink on the 27", whose separate wake dropout he never notices ([[reference_desk_pc_monitor2_wake_drop]]).

Checked 2026-11-11, a day with many blinks: no Kernel-PnP 1010 removal of DISPLAY\DELD194 all day, no Display or nvlddmkm events, and the screens stayed on from 08:38 to 13:22 with no off/on transition. So the blink never drops the monitor off the bus and never trips the graphics driver — Windows cannot see it. It lives inside the monitor, or in the signal path glitching while hot-plug stays up.

The ultrawide does log occasional full removals: 592 since June 2025 (about one a day, 9 in Nov 1–11), almost none at a screen wake, 8 of the latest 12 between 22:55 and 01:15. Unexplained — possibly Kyle switching it off at night; not the many-a-day blink.

Hookup on 2026-11-11: both monitors go through mini-DP-to-HDMI adapters (WmiMonitorConnectionParams VideoOutputTechnology 4 = DVI-type TMDS signal from the GPU; a native DP link reads 10). The ultrawide runs 3440x1440 @ 60 Hz, the 27" 2560x1440 @ 59 Hz, so the ultrawide pushes about a third more pixels through its adapter.

Told Kyle 2026-11-11: replace the ultrawide's adapter with a straight mini-DP to DP cable; if it still blinks on DP, it's the monitor — go to warranty (term not verified here; check before quoting it). Confirm the swap happened by the ultrawide's VideoOutputTechnology reading 10.
