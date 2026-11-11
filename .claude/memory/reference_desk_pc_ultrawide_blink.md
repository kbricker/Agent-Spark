---
name: reference_desk_pc_ultrawide_blink
description: "Kyle's desk-PC screen that 'blanks out momentarily' is the BIG screen (Dell S3425DW 34in ultrawide), never the 27in; its mini-DP-to-HDMI cable is rated only 1080p — prime suspect; fix: an active 4K60+ mini-DP-to-HDMI cable (it has no DP input), else warranty"
metadata:
  node_type: memory
  type: reference
  originSessionId: 0858899d-0dab-4eda-aa10-c17ded878874
  modified: 2026-11-11T22:17:23.291Z
---

Kyle's complaint — the desk-PC screen "blanks out momentarily", at random, many times a day — is the big screen, the Dell S3425DW 34" ultrawide (EDID code DELD194, made 2025 wk17). On 2026-11-11 he said he has never had issues with the 27" S2725DS. The September 2026 diagnosis wrongly pinned the blink on the 27", whose separate wake dropout he never notices ([[reference_desk_pc_monitor2_wake_drop]]).

Checked 2026-11-11, a day with many blinks: no Kernel-PnP 1010 removal of DISPLAY\DELD194 all day, no Display or nvlddmkm events, and the screens stayed on from 08:38 to 13:22 with no off/on transition. So the blink never drops the monitor off the bus and never trips the graphics driver — Windows cannot see it. It lives inside the monitor, or in the signal path glitching while hot-plug stays up.

The ultrawide does log occasional full removals: 592 since June 2025 (about one a day, 9 in Nov 1–11), almost none at a screen wake, 8 of the latest 12 between 22:55 and 01:15. Unexplained — possibly Kyle switching it off at night; not the many-a-day blink.

Hookup on 2026-11-11: both monitors run on one-piece mini-DP-to-HDMI cables, no separate dongles — call it "the cable" with Kyle, never "the adapter" (he objected: "not sure what else this could possibly be but the cable"). The ultrawide's is an Amazon Basics Mini DisplayPort to HDMI cable (6 ft, sold for MacBooks) rated only up to 1080p — a passive cable carrying 3440x1440 @ 60 Hz, about 2.4x the pixels of 1080p at the same rate. That is the prime suspect. WmiMonitorConnectionParams VideoOutputTechnology reads 4 (DVI-type TMDS signal from the GPU) for both monitors. The 27" runs 2560x1440 @ 59 Hz on its HDMI 1 input; which cable it uses is unknown. The S3425DW ("Dell 34 Plus USB-C") has NO DisplayPort input — its own DDC/CI capabilities list inputs 60(1B 11 12) = USB-C, HDMI 1, HDMI 2, and RTINGS and Digital Trends agree — so a straight mini-DP to DP cable is not an option. The 27" lists 60(0F 11 12), so it does have DP.

Both monitors answer DDC/CI (MCCS 2.1) through those cables — dxva2 GetVCPFeatureAndVCPFeatureReply via Add-Type. Useful codes: C0 usage hours (2026-11-11: ultrawide 3451, 27" 3443), C9 firmware, 60 input, D6 power mode, AC horizontal frequency as the monitor measures it ((max & 0xFF) << 16 | cur = 88.9 kHz), AE vertical frequency x100 (6000 = 60.00 Hz). No fault log exists in the standard set; Dell's own codes (E0–FD) are undocumented.

Told Kyle 2026-11-11, after first wrongly suggesting a straight mini-DP to DP cable: replace the ultrawide's cable with an active mini-DP-to-HDMI cable rated 4K 60 Hz or 8K 60 Hz. He was looking at an 8K60 one — check the PC end is MINI DisplayPort, and keep the screen at 60 Hz, since flicker reports for HDMI 2.1 converters cluster at high refresh. If the blinking stops, that settles it; if not, it's the monitor — warranty (term not verified; check before quoting it). A free DDC/CI watcher (poll AE/AC/D6 several times a second while Kyle says when it blinks) was offered as a discriminator; Kyle went straight to replacing the cable.
