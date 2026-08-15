---
name: Never add new dependencies without express authorization
description: Add a dependency only with a damn-good reason and Kyle's explicit yes — no surprises; use the no-new-deps skill to propose one
type: feedback
scope: global
---

Adding a dependency is never an agent's call to make silently. It's not that new deps are banned — it's that they must be **smart** (a damn-good reason) and **never a surprise** (Kyle is informed and says yes before install). So: propose in chat and wait for an explicit "yes add X." A yes before install, or no install.

This is package-manager-agnostic (npm/pnpm, NuGet, pip, cargo, gem, go mod, Unity Package Manager, apt/brew) and covers every category — runtime, dev, build, test, and transitive. None of "it's just a dev dep," "it's transitive," "it's tiny," or "I'll swap it later" is a reason to skip the ask; those are the rationalizations that let creep in unnoticed.

**What a damn-good reason looks like — the bar for approving:**
- **It absorbs something genuinely messy** you don't want to get distracted hand-rolling — a reverse-engineered protocol, a brittle firmware-sensitive integration, a nasty parser. Kyle on approving `bambulabs_api` (#655): *"it does something messy that we don't want to get distracted on."* A convenience wrapper around a clean problem (an FSM, a small utility) does NOT pass — hand-roll those.
- **It's actively maintained** — recent releases, a responsive maintainer, a healthy issue tracker. A dependency is maintenance you inherit; an abandoned one is a liability (unpatched CVEs, eventual fork-or-rip-out). Flag last-published date, maintainer activity, and any abandoned or security-flagged transitives.

**Why:** Kyle has hit accumulated creep he'd have pushed back on (React through the Verlet editor, Node + chokidar in the Verlet CLI). Deps shape a codebase's identity — what patterns feel natural, what gets pulled in next, how hard it is to change direction. Kyle 2026-04-15: *"I dont want any node.js in the platform... NO NEW DEPENDENCIES WITHOUT EXPRESS AUTH"* and *"you always forget fucking memories, it needs to be a skill."*

**How to apply:** Invoke the global **`no-new-deps`** skill — it's the procedural gate (manifest check, transitive fan-out inspection, maintenance status, proposal format), and its ritual is harder to skip than a mental check. Propose: package, ecosystem, why (which criterion above it meets), what it replaces/enables, the transitive tree. Wait for the yes. Dev-agent briefings carry the same pointer.

**This gates what AGENTS add — not what Kyle already authorized.** A dep Kyle brought in himself, or agreed with a human collaborator, is authorized by definition. Kyle 2026-08-10, on `com.unity.polybrush` in VaEx's manifest: *"its a tool they are using in the project... so its fine."* Still report an unexplained manifest change once, then drop it — silence is indistinguishable from a dep that slipped in. The distinction is *who added it*, never *what kind of package it is*.
