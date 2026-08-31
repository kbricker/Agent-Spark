# GarageBox hardware check — open the case once, get everything

Plans #951 (bulk storage) and #951.2 (printed caddy). Both need the case open, so do them in one trip.

Box: Dell OptiPlex 7070 SFF, `camhost` / 192.168.86.142, in the garage.

Drive ordered: **Seagate SkyHawk 4 TB**. Read the exact part number off the label when it arrives (ST4000VX016 / VX015 / VX007 are all shipping) and tell me — it goes on the ticket.

## Before you open it

- Shut down from the OS (`ssh camhost` then `sudo poweroff`, or the desktop menu). Frigate is recording — don't yank power.
- Unplug the power cord, then hold the power button ~5 s to drain.
- Side cover: release latch at the rear, slide the cover back and lift off. No tools.
- The 3.5" bay sits under the hinged ODD/drive cage — release it to see the bay floor.

Tools: digital calipers, phone camera, small Phillips.

## Check 1 — SATA power cable (the one that decides whether you can install at all)

The 7070 SFF does **not** power drives straight off the PSU. A small **black 6-pin header on the system board** feeds a Dell cable that ends in SATA power plug(s).

- [ ] Is that 6-pin header populated, or bare?
- [ ] If a cable is plugged in, does it have a **free SATA power end** (the second plug on the chain, usually meant for the ODD)?
- [ ] Photograph the header and the cable end either way.

**If missing:** Dell SFF SATA power cable, GP2JM family — ~$10 on eBay, listed for 3040/5040/7040/7050/7060/5060/3070/7070/3080 SFF. Order it before the drive arrives if you can.

## Check 2 — SATA data cable and free ports

- [ ] Count the SATA ports on the board and confirm they are all **empty** (the ticket assumes this from software; this is the visual confirmation).
- [ ] Is there a **spare SATA data cable** in the chassis? NVMe-only machines often shipped with neither cable.
- [ ] Note which port number you'd use, and photograph the port cluster.

**If missing:** any standard SATA data cable works — no Dell-specific part needed. A right-angle end helps in an SFF.

## Check 3 — measure the bay for the printed caddy (#951.2)

Only the **chassis side** needs measuring. The drive side is a published standard (SFF-8301: four bottom holes, three per side, 6-32 UNC), so it gets modelled from spec.

- [ ] Photograph the empty bay straight on, plus one angled shot showing depth.
- [ ] Caliper the **mounting hole positions and centre-to-centre spacing** on the bay floor / side rails.
- [ ] Caliper **standoff depth** — how far the drive sits off the chassis floor.
- [ ] Caliper **clearance** from the bay to the ODD cage above and to the PSU beside it. This is what says whether a downloaded caddy will foul something.
- [ ] Note the screw type the chassis expects.

Put a ruler or a known object in the photos for scale.

## Also on this trip — flash the BIOS from USB

The OS-side route does not work on this box. `fwupdmgr` stages the capsule correctly and Dell's firmware silently ignores it — tried twice on 2026-08-31, ESRT recorded no attempt either time. Currently on **1.29.0**, target **1.35.0**.

- [ ] Beforehand: download the OptiPlex 7070 BIOS update (`.exe`, ~20 MB) from Dell's support site and copy it to the root of a **FAT32** USB stick. The file goes on as-is; nothing needs extracting.
- [ ] At the box: power on and tap **F12** for the one-time boot menu, choose **BIOS Flash Update**, pick the file off the stick.
- [ ] Do not interrupt it. There is no UPS on this machine, so this is the one genuinely risky minute of the trip — if a storm is rolling through, do it another day.
- [ ] After it reboots, tell me and I will confirm the version and re-check the BIOS settings, since Dell updates can reset them.

Settings to compare against, recorded 2026-08-31 before the attempts: AC power recovery **On**, Wake-on-LAN **LanOnly**, USB wake **Enabled**, UEFI capsule updates **Enabled**. AC power recovery is the one that matters — it is what brings the NVR back by itself after a power cut.

## While the case is open — worth doing

- [ ] Blow the dust out, especially the CPU cooler and PSU intake. It's a garage box running 24/7.
- [ ] Note the PSU wattage sticker.

## Report back

Send me: the two cable answers (present / missing / free end available), the photos, and the caliper numbers. That's enough to close the cable question on #951 and start the caddy model on #951.2.

## What happens after the drive is in

Still on #951, and all of it needs `sudo` (no NOPASSWD grant on this box, so it's an interactive password):

- Partition and format the HDD, add it to `/etc/fstab`.
- Move Frigate's `recordings/` to the HDD. **OS and `frigate.db` stay on the NVMe** — the database holds the UI login, and it wants the fast disk.
- Then set a retention number that is actually true for the new capacity.
