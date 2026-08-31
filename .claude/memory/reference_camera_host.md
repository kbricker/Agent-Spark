---
name: reference_camera_host
description: "Camera host (GarageBox) — Frigate NVR box: ssh alias, hardware identity, running state, and the Amcrest CGI gotchas"
metadata:
  node_type: memory
  type: reference
---

The camera host is the Frigate NVR for the house security cameras. `ssh camhost` from the desk. Build/config reference is the doc at `C:\Projects\spark\CameraHost\camera-host-setup.md` — detail belongs there, this memory only carries what I need to reconnect and not re-derive.

## Identity (measured 2026-08-20)

- **Dell OptiPlex 7070 SFF**, i5-9500 (6 cores; UHD 630 iGPU does decode + OpenVINO detection), 14 GiB usable, 468 GB NVMe (WDC PC SN730 SDBQNTY-512G-1001).
- Hostname **GarageBox**, user **kyle**, **Ubuntu 26.04 LTS Desktop**, `America/Los_Angeles`.
- NIC **`eno1`**, MAC **`a4:bb:6d:aa:6e:ed`**, **192.168.86.142** (DHCP, no reservation yet).
- **Desktop, not Server — deliberate.** Kyle had already installed it and would not rebuild. Compensated: `openssh-server` added by hand, and all four sleep/suspend targets masked so it cannot suspend mid-recording. The setup doc still says Server; it has not been corrected.

## Running state

- **Frigate 0.17.2** lives in **`~/frigate`**, not `/opt` — deliberate, so nothing needs root. `docker compose` as `kyle` (in the `docker` group). UI on **https://192.168.86.142:8971** (self-signed).
- OpenVINO detection on the iGPU **works**, ~10 ms inference. `preset-vaapi` decode.
- Secrets are in `~/frigate/.env`, referenced from config as `{FRIGATE_...}`. **Frigate substitutes `{VAR}` even inside the `go2rtc:` block — do NOT write `${VAR}` there**, it substitutes the inner braces and leaves a stray `$` on the front of the password. And `docker compose restart` does not reload `.env`; only `up -d --force-recreate` does.
- Harmless recurring log line: `Unable to poll intel GPU stats: Failed to initialize PMU`. That is the UI's GPU meter wanting elevated caps; decode and detection are unaffected. Not worth privileging the container.

## Cameras

- **192.168.86.48 — Amcrest IP2M-841B**, Frigate camera `side`. Main stream 1920x1080 H.264 15 fps. **Its substream is hard-capped at 640x480 (`ResolutionTypes=VGA`)** — 4:3 against a 16:9 main, so detection runs on the MAIN stream for this camera. Do not keep trying to make a 720p substream; the firmware has no such mode.
- Configured 2026-08-20: NTP on (pool.ntp.org), TZ + DST correct, **P2P/cloud tunnel to `p2p.amcrestview.com` turned OFF** (`T2UServer.Enable=false`), on-camera motion detect off, dedicated `frigate` viewer account added.

- Every camera-side setting is replayable: **`CameraHost/apply-camera-settings.sh`** (a copy runs from `~/frigate/` on the box). Idempotent, verifies what it wrote, takes credentials from `CAM_ADMIN_PW` / `FRIGATE_CAM_PW` so none are in the file. Run it after any factory reset or camera swap.

- **192.168.86.139 — Sunba `IPC_NT98566_N8F`**, Frigate camera `outdoor`, PTZ, street-facing. XiongMai board, NOT Dahua — none of the Amcrest CGI applies. Main 3840x2160 H.264 10 fps; sub 800x448 H.264 15 fps feeds detection. **ONVIF is on port 8899, not 80.** Admin password SET 2026-08-29 (was blank); it lives in `~/frigate/.env` as `FRIGATE_CAM139_ADMIN_PASSWORD`.
- Configured 2026-08-20: **XMEye P2P tunnel to `secu100.net:8765` turned OFF** (`NetWork.Nat.NatEnable=false`) — it ships ON. Substream flipped from H.265 to H.264. Camera NTP disabled on purpose; see the time note below.

### Sunba / XiongMai gotchas

- **ONVIF can read but barely write.** Streams, PTZ, `SetNTP` and `SetSystemDateAndTime` work; `SetUser` returns `Sender not Authorized`. All real config goes through the **XM DVRIP binary protocol on port 34567** — client at `CameraHost/xm_dvrip.py` (stdlib only, no dependency). msgids: 1000 login, 1042 get, 1040 set, 1452 time query, 1450 time set, 1472 users (→ 1473). Account ops, confirmed against the sofiactl reference client and corroborated because its 1472/1473 pair matched this device exactly: **1482 ADDUSER, 1484 MODIFYUSER, 1486 DELETEUSER, 1488 MODIFYPASSWORD (→ 1489)**, 1474 groups, 1470 full authority list.

- **The 1488 payload that works on this firmware** (verified 2026-08-29) is FLAT, shaped like the login packet rather than the `Name`-plus-same-named-key convention the config ops use:
  ```
  {"Name": "", "SessionID": sid, "EncryptType": "MD5",
   "NewPassWord": sofia_hash(new), "PassWord": sofia_hash(old), "UserName": "admin"}
  ```
- **1488 updates `Password` but NOT `PasswordV2`.** The V2 blob is left holding its old value and appears to be vestigial here — DVRIP login validates against `Password`, and after the change the blank password was correctly refused with `Ret 203`. Do not panic at the stale V2, and do not try to hand-write one.
- **ONVIF lies about the substream codec** — it reported H264 while the stream was actually HEVC. Always `ffprobe` rather than trusting `GetProfiles`.
- **This firmware answers `Ret 603` for changes it nonetheless applies.** Only the read-back is truth; never treat 603 as a failure or 100 as proof.
- **It ignores its own DST rule.** `DSTRule=Week` with correct US dates, a reboot, every `NetWork.NetNTP.TimeZone` index from 10-19, and an ONVIF `PST8PDT,M3.2.0,M11.1.0` TZ string all leave the clock exactly 1 h behind all summer. Resolution: camera NTP is **off**, and `sync-camera-time.py` pushes host local time daily from cron (03:17, `crontab -l` as kyle). Don't re-enable its NTP.

### Amcrest/Dahua CGI gotchas that cost time

- **ONVIF PTZ needs the ADMIN account, not the viewer account.** The limited `frigate` user gets `Sender not Authorized` on GetProfiles. RTSP stays on the viewer account; only the `onvif:` block uses admin.
- **Frigate rewrites `config.yml`** (it appends a `version:` key). Never append a camera block to the end of the file — rewrite the whole file instead, or the block lands after a top-level key and YAML parsing fails.
- **This firmware rejects digest auth — use `curl --basic`.** Digest returns 401 forever.
- **`curl` needs `-g` (--globoff) for any indexed parameter.** `Encode[0].MainFormat[0]...` silently returns empty without it, because curl eats `[` `]` as glob syntax. URL-encoding to `%5B0%5D` does NOT work either — the camera answers `Error`.
- `getConfig&name=all` returns `Error` on this model. Query one subtree at a time.
- **`NTP.TimeZone` is an index, not an offset**, and the table is not the published one. Measured on this firmware: `0`=GMT+00:00 rising to `19`=GMT+13:00, then `20`=GMT-01:00 rising to `29`=GMT-09:00. **Pacific is `28`.** Probe it by setting the value and reading back the unauthenticated ONVIF `GetSystemDateAndTime` at `/onvif/device_service`.

## State as of 2026-08-29 — tracked on plan #951 (TendWright/Hardware)

Both ethernet cameras are live in Frigate and clean (5 fps each, 0 skipped, detector ~12 ms). Recording motion-only, retention configured at 30 days.

**History was wiped clean on 2026-08-29** at Kyle's instruction, after the fixes below went in: all `recordings/` and `clips/` deleted from inside the container (everything is root-owned and there is no sudo here, so `docker exec` is the route). 414 GB freed — disk went 98% -> 5%, 425 GB available. The DB was NOT deleted: Frigate 0.17 keeps the UI login in `frigate.db`, so removing it would reset the admin password and lock Kyle out. Consistent backup at `~/frigate/config/frigate.db.bak-20260829` (taken with sqlite3's `.backup()` against the live DB). Frigate restarted healthy and is recording fresh from 2026-08-29 12:12.

**Before the wipe, retention was fiction:** disk 98% full, 12 GB free, only 9 days held against a configured 30, burning ~46 GB/day. Frigate self-protects by evicting the oldest hour, so the failure mode is silently short retention, never a crash or a warning. Whether that is fixed is now an open measurement — the clock restarted 2026-08-29.

**The 2026-08-20 diagnosis of that was wrong on both counts — do not repeat it.** It blamed the Sunba's 4K main stream and proposed dropping to 1440p.
- Wrong camera. Hourly `du` for 2026-08-28: `side` wrote ~1.2 GB EVERY hour, 03:00 and noon alike (~28 GB/day), while `outdoor` tracked real street traffic (450 MB at midday, 1.6 GB at 18:00, ~18 GB/day). The indoor camera was the bigger consumer and the only continuous one.
- Wrong lever. Both streams are VBR with a bitrate CAP, so bytes = bitrate x hours recorded. Resolution does not enter it — 4K to 1440p at an unchanged 2560 kbps cap would have saved nothing and merely raised quality per pixel.

**Root cause of `side`: it is in an unlit garage, so it sits in IR/night mode around the clock even at noon.** `improve_contrast: true` stretches that dark, grainy IR frame until sensor noise reads as motion, and it recorded a solid empty garage 24/7. Set to **`improve_contrast: false` on 2026-08-29** (config line 97; `outdoor` deliberately left at `true`). Backups at `~/frigate/config/config.yml.bak-20260829` and `.bak2-20260829`. **Effect not yet measured — needs a full day, then a week.**

**Do not try to validate either fix by counting segment files.** Frigate's recorder writes segments continuously and a later retention pass prunes the ones with no motion, so a file count taken minutes after a restart measures writing, not keeping. The only valid measure is hourly `du` on `storage/recordings/<date>/<hour>/<camera>` after the pruning pass has run.

**`contour_area` is resolution-INDEPENDENT — do not "scale" it per camera.** Frigate resizes every motion frame to `motion.frame_height` (default 100 rows, aspect preserved) and measures contour area on that; `resize_factor` only maps boxes back to full-res. So 30 means the same on a 1920x1080 detect stream as on an 800x448 one. Verified in `frigate/motion/improved_motion.py` in the running container.

Still open:
- ~~Sunba admin password blank~~ **set 2026-08-29** via DVRIP 1488. Verified properly rather than trusted: new password logs in, stored hash matches `sofia_hash(new)`, and the old blank password is refused with `Ret 203`. `Ret 100` on the write was NOT treated as proof — this firmware lies about both success and failure.
- **This camera's ONVIF does not authenticate at all.** Measured 2026-08-29: `GetDeviceInformation` on port 8899 was ACCEPTED with the blank password, the new password, and two deliberately wrong passwords. So ONVIF reads are open to anyone on the LAN regardless of credentials — a firmware property, not something the password change caused or can fix. What the password *does* protect is the DVRIP control channel on 34567, which is the one that can reconfigure the camera or re-enable the P2P tunnel. Frigate's `onvif:` block carries the real password for correctness, not protection.
- **`outdoor` mask is a first pass.** Applied 2026-08-29 covering the FAR SIDE of the street only — neighbour's garage, buildings opposite, far-kerb parked cars — per Kyle; the road itself is deliberately unmasked so passing traffic still records. Polygon `0.33,0,1,0,1,0.26,0.47,0.27,0.33,0.14`, verified by rendering it over a live detect frame, not by trusting the numbers. Not yet masked and the next suspects if `outdoor` still records flat around the clock: the near foliage top-left (~x 0-0.37, y 0-0.30) and the street tree on the right, both of which move in wind.
- ~~DHCP reservations~~ **done.** All three reserved in Google Wifi as of 2026-08-29: host `.142` (`a4:bb:6d:aa:6e:ed`), `side` Amcrest `.48` (`9c:8e:cd:09:b9:95`), `outdoor` Sunba `.139` (`00:12:34:cf:64:c9`). Table is in section 2 of the setup doc.
- Retention must be set to a number that is TRUE once a real week has been measured from the 2026-08-29 restart. Do not leave 30 if the disk cannot hold 30. With 425 GB free, 30 days needs the two cameras to average under ~14 GB/day combined; they were at 46.

Next session: final physical placement of the host, then the first USB camera — which is the step that needs the udev pinning in section 5 of the doc, and the first thing here that will actually need sudo.

## Sudo — NOPASSWD grant added 2026-08-31

`kyle` has a passwordless grant at `/etc/sudoers.d/kyle-nopasswd`, so this box is administrable end-to-end over SSH, same as [[reference_cell1_operations]]. Not a real privilege increase — `kyle` was already in the `docker` group, which is root by another name.

**If the account password is lost again**, that docker membership IS the recovery route, with no reboot, keyboard or monitor: `docker run --rm -it -v /:/host alpine chroot /host passwd kyle`. Have Kyle run it in his own terminal so the value never enters an agent transcript. Used exactly this way on 2026-08-31.

## BIOS and firmware

- **BIOS is 1.29.0 and CANNOT be flashed from the OS — do not retry that route.** `fwupdmgr` stages the 1.35.0 capsule correctly (20 MB on the ESP, BootNext armed to Boot0002) and Dell's firmware silently ignores it. Failed twice on 2026-08-31. Decisive evidence is ESRT: `/sys/firmware/efi/esrt/entries/entry0/last_attempt_status` and `last_attempt_version` are BOTH `0`, meaning no attempt was recorded at all rather than a failed one. Already ruled out, do not re-check: `CapsuleFirmwareUpdate` is Enabled, no BIOS admin password, ESP has 1.1 GB free, `lowest_supported_fw_version` equals current so it is not a downgrade block. `OsIndicationsSupported` is 0x3, so this firmware has no capsule-on-disk support and fwupd is correctly using the fwupdx64.efi runtime path. **The route is a FAT32 USB stick and F12 -> BIOS Flash Update, on a physical trip.** Tracked as a checklist item on #951.
- Secure Boot is **disabled**. db is at 2023 and dbx at 20260402 — both applied 2026-08-31, and both of those DID work from the OS.
- **BIOS settings are readable and writable over SSH** through `dell-wmi-sysman` at `/sys/class/firmware-attributes/dell-wmi-sysman/attributes/` (root; no BIOS admin password set), so auditing or changing one needs no garage trip. Baseline recorded 2026-08-31: `AcPwrRcvry=On` — the box powers itself back up after an outage, which matters because there is **no UPS** — plus `WakeOnLan=LanOnly`, `UsbWake=Enabled`, `CapsuleFirmwareUpdate=Enabled`. Re-check all four after any successful BIOS flash; Dell updates can reset them.
- Ubuntu holds some apt upgrades back at `phased 0%` (its staged rollout). They are not broken and must not be forced.

## Gotcha: PowerShell mangles remote ssh commands

Handing Kyle an `ssh host "...quoted command..."` line to run from his **Windows desk** silently corrupts it — inner quotes and backslashes get stripped, so `printf "%s\n" "a b"` arrives word-split as `printf %sn a b`. Cost two rounds writing `authorized_keys` on 2026-08-20. **Give him commands to type in the target box's own shell**, or keep the remote command free of quotes and backslashes. Not host-specific — same trap applies to cell1.

Related: [[reference_cell1_operations]].
