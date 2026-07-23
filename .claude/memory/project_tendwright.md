---
name: project_tendwright
description: "TendWright (Hive app 8) — MuJoCo stack decision, P0 status, and working facts not in the repo docs"
metadata: 
  node_type: memory
  type: project
  originSessionId: 08c4549d-0dcb-4d3f-b861-a56f84597918
---

TendWright — robotic CNC machine-tending cell, Python learning project. Repo `C:\Projects\TendWright` (github.com/kbricker/TendWright, personal SSH), Hive app 8, epic plan #612, rungs #604–#610 worked strictly in order.

- **Stack (Kyle, 2026-07-15):** dependencies must be actively maintained — MuJoCo (`mujoco` + `mink` + vendored Menagerie UR5e/2F-85 models) chosen; PyBullet explicitly rejected as stale (last release Jan 2025). Tooling `uv` + `pyproject.toml`.
- **Bench status 2026-07-23: ARM BUILD COMPLETE.** IDs 1–6 programmed + labeled, horns mounted at center; joint 1's horn re-spotted after monitor caught its travel crossing the encoder wrap (target: mid-travel ≈ 2048, spline ≈ 160 ticks/tooth). cell1 back online with hardline; `uv`/`uvx` symlinked into /usr/local/bin (fixes non-interactive ssh/cron PATH). **Next session = bring-up per `docs/arm-bring-up.md`** (scan → monitor sweep → `calibrate capture` → commit calibration.json → first jog → teach/replay); Kyle sends `calibrate show` output for sanity check. Gotcha from bench day: the kit mixes 7.4V leader motors with 12V follower motors — a 7.4V motor on the 12V bus flashes red + "input voltage error" (harmless, self-protection); check the case sticker, and `scan` voltage ~7.4V is the same tell. Follower is the 12V set (Seeed SO-ARM101 Pro); leader servos are shelved for future teleop — their gear ratios (3× 1/147, 2× 1/191, 1× 1/345) are physically different hardware, not configurable.
- **Calibrate tool (#631, 612.11) COMPLETED 2026-07-23** — `hardware.bench.calibrate` capture/show: torque-off-only per-joint range/rest/direction-sign capture to calibration.json (merge-per-joint, wrap detection). Review log at `docs/reviews/plan631-calibrate-review-log.md`; operator runbook `docs/build-day-calibration.md`.
- **P1 (#605) + bench toolkit (#618) COMPLETED 2026-07-21.** Standing re-scope: NO OPC UA until a real CNC (P6-era); NO FSM/servo-framework libraries — FSMs are hand-rolled on `orchestrator/fsm.py` (Kyle: "usually the libraries are nasty"); the CNC is a physical mock bay (#619: printed nest + KW12-3 switch + Pico bridge). cell1 (UM350, `ssh cell1`) is the hardware runtime; repo cloned at `~/TendWright`, uv at `~/.local/bin/uv`. Review policy (in repo CLAUDE.md): three independent subagent reviews (adversarial w/ hardware-safety focus, code-quality, functional) before every merge.
- **P0 (#604) COMPLETED 2026-07-15**, merged to main (f65488f): MjSpec-composed cell, mink differential IK, weld-constraint grasp/clamp (documented simplification), headless validator with task-semantic checkpoints (`uv run python -m sim.validate`). **No PRs on this repo** — Kyle's process is adversarial subagent review (Python + robotics + validation-breaker) then merge to main. That review caught a critical bug: never gate waypoint completion on the IK twin — the physical servos lag ~0.2 s; gate on the plant's actual site pose + settle velocity before any weld latch. Next rung: P1 (#605) FSM + OPC UA.
- `uv` was installed via winget; in a stale shell its exe lives at `%LOCALAPPDATA%\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe` (or use `.venv\Scripts\python.exe` directly).

Related: [[feedback_personal_repo_git_identity]], [[reference_gh_cli_is_wonderforge_account]].
