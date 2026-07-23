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
- **Bench status 2026-07-22:** all six follower servo IDs programmed + labeled (1=base…6=gripper) via set_id on cell1. Kyle is assembling the arm at the bench with cell1 relocated OFFLINE until he runs ethernet — he'll ping via dashboard when back. Next milestones: per-joint horn centering (`jog --id N`, t, c ritual), then full-chain `scan` (1–6) and `monitor` tick ranges → jog soft limits. Gotcha found on bench day: the kit mixes 7.4V leader motors with 12V follower motors — a 7.4V motor on the 12V bus flashes red + "input voltage error" (harmless, self-protection); check the case sticker.
- **P1 (#605) + bench toolkit (#618) COMPLETED 2026-07-21.** Standing re-scope: NO OPC UA until a real CNC (P6-era); NO FSM/servo-framework libraries — FSMs are hand-rolled on `orchestrator/fsm.py` (Kyle: "usually the libraries are nasty"); the CNC is a physical mock bay (#619: printed nest + KW12-3 switch + Pico bridge). cell1 (UM350, `ssh cell1`) is the hardware runtime; repo cloned at `~/TendWright`, uv at `~/.local/bin/uv`. Review policy (in repo CLAUDE.md): three independent subagent reviews (adversarial w/ hardware-safety focus, code-quality, functional) before every merge.
- **P0 (#604) COMPLETED 2026-07-15**, merged to main (f65488f): MjSpec-composed cell, mink differential IK, weld-constraint grasp/clamp (documented simplification), headless validator with task-semantic checkpoints (`uv run python -m sim.validate`). **No PRs on this repo** — Kyle's process is adversarial subagent review (Python + robotics + validation-breaker) then merge to main. That review caught a critical bug: never gate waypoint completion on the IK twin — the physical servos lag ~0.2 s; gate on the plant's actual site pose + settle velocity before any weld latch. Next rung: P1 (#605) FSM + OPC UA.
- `uv` was installed via winget; in a stale shell its exe lives at `%LOCALAPPDATA%\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe` (or use `.venv\Scripts\python.exe` directly).

Related: [[feedback_personal_repo_git_identity]], [[reference_gh_cli_is_wonderforge_account]].
