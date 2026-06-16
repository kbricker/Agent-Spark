---
name: Never add new dependencies without express authorization
description: Never add a new runtime/dev/build/test/transitive dependency to any project without Kyle's explicit yes. Applies to npm/pnpm, NuGet, pip, cargo, gem, go mod, Unity Package Manager — every package ecosystem.
type: feedback
scope: global
---

**Before adding any new dependency to any project Kyle owns, stop and get explicit authorization in chat.** This rule is package-manager-agnostic — it applies to every ecosystem (npm/pnpm for JS/TS, NuGet for .NET/C#, Unity Package Manager for Unity, pip for Python, cargo for Rust, gem for Ruby, go mod for Go, apt/brew for system deps, anything else). There are no escape hatches. No "it's just a dev dep." No "it's transitive so it doesn't count." No "it's tiny." No "I'll swap it out later." A yes from Kyle before install, or no install.

**Why:** Kyle has discovered accumulated framework/dependency creep across the stacks (e.g. React pervasive in the Verlet editor, Node.js + chokidar in the Verlet CLI) that he would have pushed back on if asked. Frameworks and deps shape a codebase's identity — they change what patterns feel natural, what other deps get pulled in next, and how hard it is to change direction later. Kyle's framing 2026-04-15: *"I dont want any node.js in the platform, we already have react all over the place and I didnt want that. NEW SKILL -> NO NEW DEPENDENCIES WITHOUT EXPRESS AUTH."* The explicit callout *"you always forget fucking memories, it needs to be a skill"* made the form clear — a procedural ritual is stickier than a passive rule. verletDev has a dedicated `no-new-deps` gate skill that codifies the proposal-and-auth ritual; orchestrators without that skill follow the same rule inline — propose in chat, wait for a "yes add X," then install.

**How to apply:**
- The moment you see yourself about to add a dep — run an install command, recommend a package, scope one into a plan description, accept a review suggestion that would pull one in, or follow a tutorial that assumes one — STOP. Propose in chat with: package name, ecosystem, why you need it, what it replaces or enables, and what it pulls transitively. Wait for an explicit "yes add X."
- Applies to every package in any repo and every dep category: runtime, dev, build, test, transitive. `package.json` dependencies and devDependencies both count. `.csproj` PackageReference counts. Unity `manifest.json` entries count. `requirements.txt`, `Cargo.toml`, `go.mod`, `Gemfile` — all count.
- "Transitive" is not a loophole. If adding package A pulls in ten new packages as dependencies, that's eleven new deps, and Kyle needs to see the tree before you install.
- Dev agents on every plan must also respect this. Orchestrator briefings for dev-* agents must include the rule (or, in verletDev's case, a pointer to the `no-new-deps` skill) as part of Phase 1.5 kickoff.
- If an orchestrator has a procedural gate skill available (verletDev: `no-new-deps`), invoke it every time rather than relying on memory — the skill's ritual is harder to skip than a silent mental check. Orchestrators without such a skill should treat the propose-and-wait pattern as equally non-negotiable.
