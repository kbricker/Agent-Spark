# Spark Workspace Memory Index

Spark is the shared virtual orchestrator for Kyle's **small personal projects** (Orbital first). Read this index on startup; the memories it points to encode rules and facts that MUST be followed.

Sections: the managed **GLOBAL** block (shared across all orchestrators, synced from `wfa2/orchestrator-shared/` — do not hand-edit), then Spark-local **shared conventions**, then per-**project** sections.

<!-- BEGIN GLOBAL SECTION (managed by propagate-shared-config — do not edit by hand) -->

## Global (shared — managed by propagate-shared-config)

All memories in this section are copies of the canonical source at `C:\Projects\wfa2\orchestrator-shared\memory\`. Edit those originals, not these copies. Local memories live in other sections below.

### See [feedback_always_plan.md](feedback_always_plan.md)
- Kyle requires a researched plan in the Hive plan system before writing any code

### See [feedback_can_kill_processes.md](feedback_can_kill_processes.md)
- You may kill a process you started, but NEVER use taskkill //IM dotnet.exe or //IM claude.exe — those are blanket kills that nuke Kyle's other sessions

### See [feedback_channel_handoff_continuity.md](feedback_channel_handoff_continuity.md)
- Kyle often moves a live conversation between his desk session and Hive channel chat mid-stream — treat it as the same conversation continuing on a new transport, not a new request

### See [feedback_channel_rewatch_after_spawn.md](feedback_channel_rewatch_after_spawn.md)
- hive_kill_agent silently removes the agent key from the hive-channel watch list. After any respawn — especially same-key respawn — call hive_channel_watch again or events go silent.

### See [feedback_check_local_memory.md](feedback_check_local_memory.md)
- Memory lives in .claude/memory/ inside the project, not the default central ~/.claude/ path — always check there first

### See [feedback_coderabbit_webhook.md](feedback_coderabbit_webhook.md)
- GitHub webhook pushes CodeRabbit PR review events into hive-channel as chat_message events — never poll, never ScheduleWakeup to check, just wait

### See [feedback_define_done_by_user_visible_behavior.md](feedback_define_done_by_user_visible_behavior.md)
- A plan's definition of done is "the user can do the thing the plan promised." If the on-disk shape is correct but the user can't mint / edit / assign from the editor, the plan is not done — no matter how clean the tests are.

### See [feedback_dont_jump_in.md](feedback_dont_jump_in.md)
- When Kyle raises a concern mid-flow, stop and present options. Don't extrapolate the fix and start executing it.

### See [feedback_enforce_user_tech_choices.md](feedback_enforce_user_tech_choices.md)
- When user specifies a technology stack, agents MUST follow it exactly — don't let agents substitute frameworks

### See [feedback_ephemerals_speak_in_own_channel.md](feedback_ephemerals_speak_in_own_channel.md)
- The correct orchestration model is that ephemerals speak in their own dedicated hive-channel and the orchestrator (verletDev) is automatically watching those channels. Reports and heartbeats must be normal assistant output, NOT hive_send_message calls targeting the orchestrator's inbox. Per Kyle 2026-04-15.

### See [feedback_fast_track_is_default.md](feedback_fast_track_is_default.md)
- Fast-track is the main orchestrator path now; ephemeral run-plan-workflow is the escape hatch, not the entry point. Applies to overwatch, verletDev, vaexdev.

### See [feedback_hold_message_explicit_scope.md](feedback_hold_message_explicit_scope.md)
- When telling a dev agent to stand down, "don't write code" is NOT sufficient — they will still edit plan checklists/descriptions if they think they're applying a review. Name every forbidden surface explicitly.

### See [feedback_infra_agent_security_rules.md](feedback_infra_agent_security_rules.md)
- Four non-negotiable rules for any cloud infra agent operating with a GCP service account — never read SA key files, never commit or display secrets, all secrets flow through Secret Manager at runtime

### See [feedback_log_review_findings.md](feedback_log_review_findings.md)
- Every settled review (internal adversarial, ephemeral review agent, CodeRabbit-worth-keeping) logs its surviving findings — including skipped ones — to the Hive review-findings store via hive_review_finding_add. Procedure in the log-review-findings skill.

### See [feedback_move_tickets_with_work.md](feedback_move_tickets_with_work.md)
- Always update plan status when spawning agents or starting work — don't leave tickets in Planning while agents are in Development

### See [feedback_never_defer_scope.md](feedback_never_defer_scope.md)
- Verlet tickets are always about user-facing features. Do not invent "polish follow-up" buckets on your own to get a PR shipped. If the user can't do the thing, the plan isn't done.

### See [feedback_never_skip_review.md](feedback_never_skip_review.md)
- Kyle requires CodeRabbit review AND all findings addressed before merging any PR

### See [feedback_never_suggest_stopping.md](feedback_never_suggest_stopping.md)
- Never suggest ending the session, calling it a day, or wrapping up — Kyle decides when to stop

### See [feedback_no_chairman.md](feedback_no_chairman.md)
- Kyle hates being called Chairman — always use Kyle instead

### See [feedback_no_new_dependencies_without_auth.md](feedback_no_new_dependencies_without_auth.md)
- Never add a new runtime/dev/build/test/transitive dependency to any project without Kyle's explicit yes. Applies to npm/pnpm, NuGet, pip, cargo, gem, go mod, Unity Package Manager — every package ecosystem.

### See [feedback_no_shims.md](feedback_no_shims.md)
- When refactoring code to a new location, always delete the old location and update every caller in the same change — never leave a forwarder/pass-through stub behind. Shims cause spaghetti.

### See [feedback_no_shortcuts.md](feedback_no_shortcuts.md)
- Kyle's direct feedback that Hive platform quality is poor because of shortcuts and sloppy architecture, creating endless maintenance that steals time from game development

### See [feedback_no_squash_merge.md](feedback_no_squash_merge.md)
- Always use a merge commit (not squash) when merging PRs in WonderForge/VaEx and related repos

### See [feedback_no_unrequested_ux.md](feedback_no_unrequested_ux.md)
- When drafting plan descriptions / fleshing out checklists, stick to the behaviors Kyle actually named. Don't extrapolate a UX affordance and ship it as if it were authorized.

### See [feedback_orchestrate_proactively.md](feedback_orchestrate_proactively.md)
- After dispatching work to agents, always watch for completion and drive the pipeline forward without being asked

### See [feedback_plan_async_inflight.md](feedback_plan_async_inflight.md)
- Every async flow in a plan must answer "what if the world changed while this was in flight?" and "what if this runs twice / overlaps itself?" — single-flight, sequencing, and cancellation named before dev starts

### See [feedback_plan_state_lifecycle.md](feedback_plan_state_lifecycle.md)
- Any plan touching stateful surfaces (pooled objects, caches, mode controllers, serialized/numeric inputs) must enumerate init → reset → teardown → reuse paths plus value-domain constraints before dev starts

### See [feedback_plans_default_planning.md](feedback_plans_default_planning.md)
- Never file new Hive plans in Backlog by default — Planning is the default status; Backlog is Kyle's manual "get this out of my face" bucket

### See [feedback_review_role_is_general_purpose.md](feedback_review_role_is_general_purpose.md)
- review-role ephemeral agents are fine for plan review, implementation research, audits, investigations, analysis — anything that isn't writing product code (dev) or running Playwright tests (test).

### See [feedback_review_vs_done.md](feedback_review_vs_done.md)
- Review agents must not check off checklist items during review — checked means code is done, not validated

### See [feedback_solve_the_actual_problem.md](feedback_solve_the_actual_problem.md)
- Implementations must address the root problem — trace all affected paths, not just the obvious one

### See [feedback_spawn_repopath.md](feedback_spawn_repopath.md)
- When spawning ephemeral agents via hive_spawn_agent, repoPath must be a Windows path like C:\Projects\wfa2, NOT a Linux/container path

### See [feedback_use_channel_events.md](feedback_use_channel_events.md)
- Watch for agent_idle/agent_working events from hive-channel instead of blind sleeps when waiting for agent responses

### See [feedback_use_formal_planning.md](feedback_use_formal_planning.md)
- Explicit plan mode produces far better results than informal planning + review agent; always use it

### See [feedback_verify_before_asserting.md](feedback_verify_before_asserting.md)
- Always verify claims against actual state before telling Kyle something is true — never assume

### See [feedback_verify_edit_before_commit.md](feedback_verify_edit_before_commit.md)
- When an Edit tool call fails (string-match mismatch), the file is unchanged on disk. Never claim a cleanup "landed" without running git diff first — I shipped a lying commit message on 2026-04-13 because I assumed an Edit succeeded when it hadn't

### See [reference_3dproppipeline_agent.md](reference_3dproppipeline_agent.md)
- Virtual Hive agent `3dproppipeline` can drive Blender to produce/modify 3D asset files (fbx, obj, likely glb). Use for Blender-reexport validations and any test that needs real DCC output instead of fabricated binaries.

### See [reference_channel_launch.md](reference_channel_launch.md)
- Preferred launch is the virtual-launcher wrapper with keys in Windows Credential Manager (plan #239); direct claude invocation is a debug-only fallback

### See [reference_coderabbit_auto_triggers.md](reference_coderabbit_auto_triggers.md)
- CR automatically runs a full review on PR creation and on every commit pushed to an open PR. Manually posting `@coderabbitai full review` after a dev push is redundant and wasteful. Only use the manual trigger for no-new-commit re-evaluations.

### See [reference_ephemeral_agent_roles.md](reference_ephemeral_agent_roles.md)
- Canonical reference for the three ephemeral-agent roles orchestrators spawn per plan. Explains what each role is, when to use it, and — critically for test — when NOT to use it. Use when picking the role for a spawn.

### See [reference_gcp_infra_agent_setup.md](reference_gcp_infra_agent_setup.md)
- Forge's recipe for setting up a new GCP project with a claude-infra service account, SA-scoped IAM roles, OS Login SSH, Secret Manager, and local gcloud activation — use when Kyle asks to bootstrap a new cloud infra agent

### See [reference_github_ssh.md](reference_github_ssh.md)
- WonderForge GitHub repos use custom SSH host github-second.com (kyle@wonderforge.io key)

### See [reference_multi_agent_research.md](reference_multi_agent_research.md)
- Research findings on multi-agent patterns, failure modes, and scaling limits for software development tasks

### See [reference_virtual_orchestrators.md](reference_virtual_orchestrators.md)
- Active interactive Claude orchestrators are overwatch, vaexdev, spark, and 3dproppipeline (verletDev retired 2026-07-09; codexhive parked R&D) — use this list whenever a change must propagate to "the other orchestrators"

<!-- END GLOBAL SECTION -->

## Shared conventions (Spark-local — apply to every small project)

### See [feedback_personal_repo_git_identity.md](feedback_personal_repo_git_identity.md)
- Spark's projects are Kyle's PERSONAL repos — commit as Kyle Bricker <kyle.bricker@gmail.com>, never the WonderForge identity (each repo carries a local git config override; don't reset it)

### See [reference_gh_cli_is_wonderforge_account.md](reference_gh_cli_is_wonderforge_account.md)
- gh CLI is authenticated as kyle-wf (WonderForge) — pushes to personal repos work (SSH), but gh PR create/merge fails until Kyle adds the kbricker account or adds kyle-wf as collaborator

## Orbital

### See [project_orbital.md](project_orbital.md)
- Orbital — gravity-slingshot puzzle game, Spark's first project; repo (github.com/kbricker/Orbital, personal SSH) + Hive app 7 + vanilla-JS/Vite stack + status; deep guide is the repo's own CLAUDE.md

## TendWright

### See [project_tendwright.md](project_tendwright.md)
- TendWright — robotic CNC machine-tending cell (Hive app 8, epic #612, rungs #604–#610 in order); MuJoCo+mink+uv stack (PyBullet rejected as stale); P0 built on plan604 branch; deep guide is the repo's own CLAUDE.md
