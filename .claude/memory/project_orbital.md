---
name: project_orbital
description: Orbital — gravity-slingshot puzzle game, Spark's first project; repo + Hive app + stack + status pointers
type: project
---

**Orbital** is a gravity-slingshot puzzle game (launch a craft, steal momentum from moving planets via gravity assists to reach a target ring). Spark's first hosted project.

- **Repo:** `C:\Projects\webstorm\orbital` — remote `git@github.com:kbricker/Orbital.git` over Kyle's PERSONAL GitHub SSH (see [[feedback_personal_repo_git_identity]]). Local git config is the personal identity; do not reset it.
- **Hive app:** 7 (Orbital), modules Game/Content/Infra. Plans fast-tracked here.
- **Stack (hard constraints):** vanilla JS ES modules + Vite, **no runtime dependencies**; HTML5 Canvas 2D; procedural Web Audio (zero audio asset bytes); deterministic fixed-timestep sim. The repo's own `CLAUDE.md` is the authoritative deep guide — read it when working Orbital.
- **Key systems built:** deterministic epoch/snapshot + time control; velocity-inheritance launch; gravity-assist detection + scoring engine (`src/assist.js`); planning suite (trajectory fan, lead-ghost, predicted Δv, honest gravity rings); dev run-capture/replay + `advance()` (`src/runlog.js`, backquote hotkey, `window.__orbital`); headless-Chrome solver/scoring harness.
- **Scoring (v3, decided 2026-06-13):** `score = Σ(BASE + Δv·q)·chainMult + launchBonus`, BASE 100 / q 0.5 / chain ×1,×1.5,×2.1… — more assists generally wins, Δv is the quality tiebreaker.
- **NEVER kill Chrome** during headless testing — close only the harness's own instance via CDP `Browser.close` (general machine rule lives in overwatch's `feedback_never_kill_chrome`). The harness already does this.
- **Status:** spec `orbital-finding-the-fun` — assist engine (#488), planning suite (#489), scoring v3 (#498), run-capture (#497), playtest refinements (#496) all shipped. **Open: #495 levels-as-basins** (close off 0-assist "lazy" wins, widen winning wedges, re-tune medals). Hosted on Vercel is the intended deploy; backend/leaderboard/replay persistence is brainstormed but not built.
