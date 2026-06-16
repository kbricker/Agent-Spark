---
name: no-new-deps
description: Procedural gate that MUST be invoked before any new dependency is added to any package or project (runtime, dev, build, test, or transitive). Forces an explicit proposal-and-auth ritual. Applies to every orchestrator directly AND to every ephemeral dev agent during plan execution. Invoke whenever you're about to install, recommend, or scope-in a dependency the project doesn't already have.
scope: global
---

# No New Deps Without Express Auth

This skill is a **hard procedural gate**. You must run through it in order before any new dependency lands in any project. Do not skip steps. Do not silently bypass this skill because "it's a small one-liner helper" — those are the worst offenders because they justify themselves on the margin, and over years they become the accumulated framework creep Kyle is closing the gate on right now.

## When to invoke this skill

**Every single time you are about to add a new dependency, or recommend one, or scope one into a plan.** Specifically:

- Any install via the project's package manager (`npm install`, `pnpm add`, `yarn add`, `dotnet add package` / NuGet, `pip install`, `cargo add`, `gem install`, `go get`, Unity Package Manager add, etc.) of a package not currently in the project's manifest
- Any plan description that implies a new dep ("we'll use library X for this")
- Any dev-agent implementation moment that hits "this would be easy with Y"
- Any review or CodeRabbit suggestion of the form "consider using library Z"
- Any plan-review discovery that the work needs something new to succeed

If you're not sure whether it counts as a new dep, invoke this skill anyway. Cost of running it: 60 seconds. Cost of missing it: accumulated architectural debt Kyle has to push back on later.

## What counts as a "new dependency"

**COUNTS:**
- A top-level entry added to ANY project's package manifest (`package.json`, `*.csproj` PackageReference, `requirements.txt` / `pyproject.toml`, `Cargo.toml`, `Gemfile`, `go.mod`, Unity `manifest.json`, etc.) that wasn't there before
- A transitive dep pulled in by a new top-level entry — if package X brings in 50 transitives, all 50 count
- A dev-only, build-only, or test-only dep — same rule, no exemption
- Replacing an existing dep with a different one (you're adding the new one AND removing the old — both halves need auth)

**DOES NOT COUNT:**
- Upgrading an existing dep to a newer version (normal maintenance — but call out breaking-version jumps)
- Installing a currently-listed dep in a workspace/project that already has it listed elsewhere
- Using a stdlib module or built-in that ships with the language/runtime (e.g., Node's `fs`, `path`, `crypto`; .NET BCL; Python stdlib; Go stdlib)
- Using a utility already imported from an existing dep the project already depends on

## The gate — run through every step, in order

### Step 1: STOP

Do not touch any package manifest. Do not run an install command. Do not edit a lockfile. Hands off the tools until you've completed the rest of this skill.

### Step 2: Verify it's actually new

Search the relevant project's package manifest for the dep name. If it's already listed: this isn't a new dep, it's maintenance. Exit the skill, proceed normally.

If it's genuinely not listed: continue.

### Step 3: Compile the dep proposal

Produce the following as a single chat message to Kyle, in this exact shape:

**Proposed new dep:** `<package-name>@<version-range>` in `<project path>`

**What it does:** one-sentence description, plain language, no marketing speak

**What we need it for:** the specific work that's driving the request. Name the plan and the checklist item if applicable.

**Alternatives considered:**
1. **Write it ourselves** — what that would look like, how many lines of code, what tradeoffs
2. **Use an existing dep** — if any currently-listed dep covers 80% of the use case
3. **Skip the feature or work around it** — if the scope can shrink to avoid needing the dep at all

**Cost:**
- **Transitive fan-out:** exact count. Use the package manager's inspection command (`npm info <pkg>`, `pnpm info <pkg> dependencies`, `dotnet list package --include-transitive`, `pipdeptree`, `cargo tree`, etc.) if you don't know. If any transitives are surprising (large, abandoned, security-flagged), call them out by name.
- **License:** MIT / Apache / BSD / other. Flag anything non-permissive.
- **Platform coupling:** which runtimes/OSes? If this is for a project that currently runs cross-platform, flag any platform-specific native binding.
- **Bundle/binary size impact:** rough number if you can estimate it (for browser bundles, bundle size; for CLIs/servers, install-time footprint)
- **Maintenance status:** last published, maintainer activity, GitHub issue count if relevant

**Your recommendation:** "install" or "write it ourselves" or "skip the feature" — pick one, don't hedge.

### Step 4: Wait for Kyle's explicit yes

"Express authorization" means Kyle typed one of:

- "yes add X"
- "go ahead with Y"
- "approved"
- equivalent explicit green light

**NOT authorization:**
- Silence
- "hmm that's interesting"
- "sure I guess"
- "the plan implies it" — no plan implies it until Kyle says so explicitly
- An earlier session's approval for a DIFFERENT dep
- A review agent or CodeRabbit "suggests using X" — those are suggestions, not authorizations

If Kyle says no, or asks for more detail, or picks an alternative: respect the decision. Do not re-propose the same dep in the same session.

### Step 5: Install (only after explicit yes)

Install via the correct package manager for the project. Record the approval in the commit message or PR description: *"Adds `<pkg>` per Kyle authorization 2026-MM-DD."*

### Step 6: Verify the lockfile diff

Before committing, run `git diff` against the lockfile (`pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`, `packages.lock.json`, `Cargo.lock`, `Gemfile.lock`, `go.sum`, Unity `packages-lock.json`, etc.) and check the transitive fan-out matches what you disclosed in the proposal. If there's a surprise (significantly more transitives than you said, or transitives you didn't mention), STOP, revert the install, go back to Step 3 with the corrected disclosure, and get re-approval.

## Dev agents during plan execution

If you are a dev agent spawned on a plan and you hit a "I need library X for this" moment during implementation:

1. **Do not install.** Do not edit any package manifest. Do not experiment with install commands to "see if it works."
2. **Stop work.** Report via your own channel output (the orchestrator is subscribed) with the Step 3 proposal shape. Include: the plan ID, the checklist item you're working on, and a concrete "write it ourselves vs. install" tradeoff.
3. **Wait for the orchestrator to relay to Kyle and come back with an explicit yes/no.** Do NOT assume the implementation path requires the dep — if Kyle says no, rework the approach.
4. **Default to writing it yourself** if any ambiguity exists in whether you're authorized. The cost of hand-rolling a small utility is lower than the cost of accumulated framework debt.

## Escape hatches

**There are none.** No "tiny one-liner helper" exemption. No "everyone uses this one" exemption. No "it's just a dev dep" exemption. No "the standard library doesn't have X so we need Y" exemption without running through the proposal ritual.

If you find yourself wanting to skip this skill because "surely this one is fine," that's precisely the moment the skill exists for. Run it.

## What this skill implies for existing state

Everything currently listed in any project's package manifest is inherited state — not newly added. This skill does not retroactively challenge existing deps. Migrations off any of them (replatforming a CLI, replacing a UI framework, swapping file watchers, swapping an HTTP client) are separate architectural conversations that need their own scoped planning, not something a plan can silently implicate.

## Orchestrator responsibility

Every dev-agent kickoff briefing on every plan — via `run-plan-workflow` Phase 1.5 — MUST include a pointer to this skill with language like: *"Before adding any dependency during implementation, invoke the `no-new-deps` skill and follow its procedural gate. Do not install anything not currently in the project's package manifest without explicit Kyle authorization relayed through the orchestrator. Default to writing it yourself if in doubt."*
