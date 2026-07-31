---
name: project_tendwright
description: "TendWright (Hive app 8) — MuJoCo stack decision, P0 status, and working facts not in the repo docs"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08c4549d-0dcb-4d3f-b861-a56f84597918
---

TendWright — robotic CNC machine-tending cell, Python learning project. Repo `C:\Projects\TendWright` (github.com/kbricker/TendWright, personal SSH), Hive app 8, epic plan #612, rungs #604–#610 worked strictly in order.

## THE TARGET, in Kyle's words (2026-07-27)

*"what I really want is the openCV based ability to see a thing grab it, see a spot the thing needs dropped, move the arm and place the thing there."*

He explicitly ranked the alternatives: authoring a workflow in the sim, shipping it to cell1 and replaying it is *"a form of teleop, but its kind of dumb"* — the arm repeats what it was told. **Vision-guided pick and place (#606) is the goal**, not canned playback. There is **no leader arm and none is planned**, so "teleop" never means leader-follower here. Earlier framing: *"we can run things in mojoco, see them and validate them in the sim before running on the real arm, but we will always get the same motion we see in mojoco"* and *"I can just sit here"*.

## State as of 2026-07-27 (supersedes the 07-23/24 notes below where they conflict)

- **The twin is the SO-101, verified against the parts Kyle printed (#670 DONE).** `sim/meshcheck.py` compares the vendored meshes against `hardware/so101-print/individual/` — the STLs Kyle actually sent to the printer, independently sourced from the MJCF. All 11 parts match to 0.09%; the old SO-100 package is the **negative control** (rejected at 3.88%, a 43× separation) and is therefore KEPT, quarantined: `DO-NOT-USE.md`, both XMLs renamed `*.WRONG-ARM-DO-NOT-LOAD.xml`, and a selftest that enforces it. Do not delete it.
- **Shipped since:** `sim/clip.py` (one motion definition shared by sim and arm), `sim/trace.py` (records the arm's real path, compares to the sim), `sim/ik.py` (#606 — mink, already a dep), `sim/simcam.py` (#606 — offscreen camera + tag36h11 generation/detection), `hardware/bench/posegate.py` (#699 — the collision gate now also guards `jog` and `teach replay`), `hardware/bench/batch.py` (unattended run matrices), `hardware/bench/memprobe.py` (#704 diagnostics).
- **Closed 2026-07-27:** #643, #645, #648, #649, #670, #647, #699. **Open and live:** #660 (motion rig), #606 (vision, in Development), #656/#661 (waiting on cameras), #673 fixtures in the gate, #674 j4 overhaul, #675 gravity/payload, #676 batch, #698 remote power, #704 camserve leak, #705 camserve fps, #617 BIOS.

## Numbers worth not re-deriving

- **Tick quantisation floor ≈ 0.2 mm at the tool.** 0.088°/tick; the IK solver itself reaches 0.0002 mm. Nothing can be commanded or grasped more precisely than this — a hardware limit, not a software one. Kyle's response: *"I can live with 0.22mm"*.
- **rig → cell-world yaw is DERIVED, never a literal — do not quote a number for it from memory.** It is `cell arm_yaw − twin.reach_yaw_deg()`, measured by least-squares AND derived, agreeing to 0.0000°. Both inputs have since moved: the arm was relocated to the main table and clamped (2026-07-28), and `reach_yaw` swung 12.819° on 2026-07-30 when plan 714.6 found the twin's j1 mapping MIRRORED — with no mesh change at all, because pan zero runs through calibration.json's ratified j1 frame. An earlier version of this memory carried `−99.298°` from `arm_yaw −90 / reach_yaw +9.298`; every one of those three numbers is now wrong. Read `cell.json` and ask the twin. The SO-101 does **not** reach along +X of its own base frame, and assuming +X or +90° is the #670 attach-angle bug.
- **m1 rotation centre sits 62.4 mm above the mounting plane**, and the cell's table surface is world z = 0. Confirmed from two unrelated sources (mesh measurement and the cell model).
- **The arm base plate is 95.6 × 110.9 mm and m1 is NOT centred on it** — 31.0 mm from one X edge, 64.6 from the other, centred in Y. "The arm is on the table edge" is ambiguous by up to 2.2 in.
- **The collision gate's world is the arm + a ground plane only** — 13 arm geoms. The bench, fixtures, the object in the gripper and the cable are all invisible (#673). "Clear" means *will not hit itself*, never *safe*.
- **j4 overhauls under gravity**: measured 1594 ticks/s against a commanded 200 (~8×), accelerating all the way down. Every other joint tracks 1.1–1.6×.

## Recurring defect pattern in this project

**A constant derived from an asset, transcribed into consuming code as a literal, going silently wrong when the asset changes.** It has recurred at least four times: the `+90°` attach angle (the SO-100's own reach angle taken as universal), the SO-100 body names in a selftest that passed vacuously because `mj_name2id` returns −1 and `xpos[-1]` wraps, `qpos0` used as a default-pose knob when it is the joint REFERENCE, and model-vs-calibrated joint limits differing in **both** directions (j2/j6 physical exceeds model, j3 model exceeds physical — the latter silently clamped an IK solution and moved the tool 26 mm while reporting success). Prefer deriving at runtime and asserting the derivation; where a literal is unavoidable, label it a placeholder and say what supersedes it.

- **Stack (Kyle, 2026-07-15):** dependencies must be actively maintained — MuJoCo (`mujoco` + `mink` + vendored Menagerie UR5e/2F-85 models) chosen; PyBullet explicitly rejected as stale (last release Jan 2025). Tooling `uv` + `pyproject.toml`.
- **Bench status 2026-07-23: ARM BUILD COMPLETE.** IDs 1–6 programmed + labeled, horns mounted at center; joint 1's horn re-spotted after monitor caught its travel crossing the encoder wrap (target: mid-travel ≈ 2048, spline ≈ 160 ticks/tooth). cell1 back online with hardline; `uv`/`uvx` symlinked into /usr/local/bin (fixes non-interactive ssh/cron PATH). **Next session = bring-up per `docs/arm-bring-up.md`** (scan → monitor sweep → `calibrate capture` → commit calibration.json → first jog → teach/replay); Kyle sends `calibrate show` output for sanity check. Gotcha from bench day: the kit mixes 7.4V leader motors with 12V follower motors — a 7.4V motor on the 12V bus flashes red + "input voltage error" (harmless, self-protection); check the case sticker, and `scan` voltage ~7.4V is the same tell. Follower is the 12V set (Seeed SO-ARM101 Pro); leader servos are shelved for future teleop — their gear ratios (3× 1/147, 2× 1/191, 1× 1/345) are physically different hardware, not configurable.
- **Calibrate tool (#631, 612.11) COMPLETED 2026-07-23** — `hardware.bench.calibrate` capture/show: torque-off-only per-joint range/rest/direction-sign capture to calibration.json (merge-per-joint, wrap detection). Review log at `docs/reviews/plan631-calibrate-review-log.md`; operator runbook `docs/build-day-calibration.md`.
- **cell1 is a runtime box, not a dev box (Kyle, 2026-07-24):** no push credentials, no dev tooling beyond the repo clone + uv. Bench-day commits happen on cell1 (repo-local git identity Kyle Bricker is set) and the DESK relays the push: `git pull --ff-only cell1:TendWright main` then `git push origin main` from C:\Projects\TendWright. Don't propose deploy keys or remote swaps for cell1.
- **P1 (#605) + bench toolkit (#618) COMPLETED 2026-07-21.** Standing re-scope: NO OPC UA until a real CNC (P6-era); NO FSM/servo-framework libraries — FSMs are hand-rolled on `orchestrator/fsm.py` (Kyle: "usually the libraries are nasty"); the CNC is a physical mock bay (#619: printed nest + KW12-3 switch + Pico bridge). cell1 (UM350, `ssh cell1`) is the hardware runtime; repo cloned at `~/TendWright`, uv at `~/.local/bin/uv`. Review policy (in repo CLAUDE.md): three independent subagent reviews (adversarial w/ hardware-safety focus, code-quality, functional) before every merge.
- **P0 (#604) COMPLETED 2026-07-15**, merged to main (f65488f): MjSpec-composed cell, mink differential IK, weld-constraint grasp/clamp (documented simplification), headless validator with task-semantic checkpoints (`uv run python -m sim.validate`). **No PRs on this repo** — Kyle's process is adversarial subagent review (Python + robotics + validation-breaker) then merge to main. That review caught a critical bug: never gate waypoint completion on the IK twin — the physical servos lag ~0.2 s; gate on the plant's actual site pose + settle velocity before any weld latch. Next rung: P1 (#605) FSM + OPC UA.
- `uv` was installed via winget; in a stale shell its exe lives at `%LOCALAPPDATA%\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe` (or use `.venv\Scripts\python.exe` directly).

Related: [[feedback_personal_repo_git_identity]], [[reference_gh_cli_is_wonderforge_account]].
