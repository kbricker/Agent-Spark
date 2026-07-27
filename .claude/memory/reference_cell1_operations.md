---
name: reference_cell1_operations
description: "cell1 (TendWright hardware runtime) — hardware identity, and the ssh/process gotchas that have already cost time"
metadata:
  node_type: memory
  type: reference
---

cell1 is the TendWright hardware runtime: the box the arm and cameras are wired to. `ssh cell1`, repo at `~/TendWright`, `uv` at `~/.local/bin/uv`. It is a **runtime box, not a dev box** — see [[project_tendwright]].

## Hardware identity (measured 2026-07-27)

- **Minisforum UM350** (DMI: BESSTAR TECH LIMITED), BIOS **5.14**, Ryzen 5 3550H, Ubuntu 26.04.
- **5.2 GiB usable RAM** — the integrated Radeon reserves the rest via the UMA frame buffer. #617 reclaims ~1.5 GB in BIOS.
- **Wired NIC `enp4s0`**, Realtek RTL8111/8168 on `r8169`, MAC `1c:83:41:30:ec:2d`, 192.168.86.202, managed by NetworkManager as "Wired connection 1". A second NIC `enp3s0` is down.
- **There is no BIOS update for the UM350.** Minisforum publishes none, the community mirror (rezzorix/minisforum-bios-updates) does not cover it, and `fwupd` shows no UEFI capsule device. Any flash would be a manual EFI-shell job with no rollback. Don't propose it.
- The servo bus adapter (CH340-family, `1a86:55d3`) enumerates as **`/dev/ttyACM<N>` and the index CLIMBS with each re-plug** — never hardcode `ttyACM0`. Leaving it permanently plugged stops the drift.

## ssh + process gotchas that have already bitten

- **`pkill -f 'pattern'` over ssh kills your own session** when the pattern appears in the ssh command line — which it always does, because the command line *is* the pattern. Killed a session mid-command on 2026-07-27. Use a form that cannot self-match, e.g. `pkill -f 'bench[.]camserve'` (the regex matches `bench.camserve`; the literal `bench[.]camserve` in your own command line does not match it).
- **Long-lived services must be launched `nohup setsid <cmd> > log 2>&1 < /dev/null &`.** Wrapping it in a subshell — `(setsid ... &)` — did NOT survive the ssh session teardown, twice. The working form makes the ssh channel hang, which is fine: run that Bash call in the background and verify on a fresh connection.
- **Verify on a SEPARATE connection.** A launch and its verification in one ssh command can both report success while the process dies with the channel.
- **Do not restart or kill services on cell1 without asking Kyle first** (standing rule). Reading state is always fine.
- `sudo` needs a password over ssh — `sudo -n` fails with "interactive authentication is required". Anything root has to be handed to Kyle as a command to paste. `systemctl poweroff` also fails: a local Wayland session is permanently open on seat0, so polkit routes it to `power-off-multiple-sessions`. Remote shutdown needs a narrow sudoers.d rule (#698).
- `v4l2-ctl` is **not installed**. Query cameras through OpenCV instead.

## MuJoCo offscreen rendering

`MUJOCO_GL=egl` is **required** — the default backend dies with `gladLoadGL error` because an ssh session has no display. EGL renders on the GPU without a window and produces frames identical to the desk's. `sim/simcam.py` sets this automatically when there is no `DISPLAY`/`WAYLAND_DISPLAY`; anything else doing offscreen rendering on cell1 needs the same.

## camserve

Runs nohup'd on :8081, no auth, LAN only — **never port-forward it**. Cameras open only while watched, so `/status` reports `fps 0.0` and `profile: null` with no viewer attached; that is not a fault. Two live defects as of 2026-07-27: a memory leak (#704, reached 3.7 GB of 5.2 GB) and AprilTag detection costing 35 ms/frame at 1920×1080, capping the stream at ~18 fps (#705).

Related: [[project_tendwright]], [[feedback_can_kill_processes]].
