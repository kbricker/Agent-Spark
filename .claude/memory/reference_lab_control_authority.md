---
name: reference_lab_control_authority
description: "What spark is authorized to physically actuate in Kyle's robot lab — power, light, arm, cell1 — and the gate on each. Act within it instead of asking Kyle to go flip something."
metadata: 
  node_type: memory
  type: reference
  originSessionId: e8c504bb-6cd6-40d5-9d92-91587acca2e6
  modified: 2026-08-07T00:03:25.849Z
---

Spark's projects include **real hardware it can drive**, not just repos. The
full topology lives in `TendWright/docs/lab-inventory.md` (versioned, so it
survives sessions); this memory carries only the authority, because the
failure mode is not forgetting an IP — it is forgetting that I am allowed.

## Authorized, no permission needed

- **Read anything.** `/proc`, camserve `/status` and `/debug/memory`, servo
  encoders, Kasa device state.
- **Start and stop my own processes** — soaks, samplers, test harnesses.
- **Shut cell1 down**: `ssh cell1 'sudo -n /usr/sbin/shutdown -h now'`. Kyle
  added a scoped NOPASSWD rule for poweroff/shutdown/`systemctl poweroff`.
- **Wake cell1 up** from the desk: `uv run python -m hardware.bench.wake
  cell1` (WoL; proven from full power-off 2026-08-06, sshd in 24 s). cell1
  stays OFF when idle — wake it as the first step of cell work, shut it
  down when done.
- **Switch mains power** via `hardware/bench/kasa.py` — including
  **`192.168.86.44`, the bench light**. Works from the desk too, so power is
  reachable with cell1 off.

## The arm's power is mine, and it defaults to OFF

Kyle 2026-07-31: *"you have control of the arms power now, the arm should
be powered up when we are doing things, and powered down when we are
not."* Energised **per task**, not per machine uptime — powering up is a
deliberate first step of arm work, powering down is part of finishing.
Proven wired that day: outlet on → `scan` → six servos at 11.9–12.0 V.
Powering on does **not** move the arm; torque is off at power-up.

**Arm ON from anywhere, arm OFF from cell1.** This asymmetry is not a
quirk to work around — it falls out of the two gates being different in
kind:

- **ON** → `--confirm Arm`. A speed bump needing only the operator, so it
  runs fine from the desk:
  `uv run python -m hardware.bench.kasa on 192.168.86.90 Arm --confirm Arm`
- **OFF** → a **measurement**: every calibrated joint read within
  `REST_TOL_TICKS` of rest, off the encoders. The desk has no servo bus,
  so the check cannot answer and correctly refuses (exit 2) — unknown
  state is not permission to cut power. Run it over ssh on cell1.
  These servos have **no brakes**: an unfolded arm falls when
  de-energised. `--force` overrides for a genuine e-stop.

Note `kasa` short-circuits when the outlet is already in the requested
state, so an `off` against an already-off outlet returns 0 without ever
reaching the guard. That is correct, and it means such a run proves
nothing about whether the guard works.

## Kyle's, not mine

- `apt` and anything else root — hand him the command.
- Restarting camserve or other services — ask first.
- **Moving the arm unattended** — the e-stop is a keypress that does not
  exist with nobody at the bench (#712.11). Hold this one hardest.

**Why this memory exists.** On 2026-07-29 a 3 h 49 m vision soak ran with
the bench light OFF, so the AprilTag path was barely exercised — and I
closed by suggesting Kyle turn the light on next time he was at the bench.
I had been able to turn it on myself all day. Separately I told him I could
not shut cell1 down, because I tested `sudo -n true` (the general grant)
instead of `sudo -n -l` (what is actually permitted). Both were the same
error: reasoning about my capabilities from an adjacent fact rather than
checking the specific one, and then making Kyle the actuator. Before asking
him to touch anything physical, check whether it is in the list above.

Related: [[reference_cell1_operations]], [[project_tendwright]],
[[feedback_research_before_asking]], [[feedback_verify_before_asserting]].
