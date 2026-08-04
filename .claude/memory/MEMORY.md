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

### See [feedback_check_docs_on_harness_friction.md](feedback_check_docs_on_harness_friction.md)
- Permission prompts, hook misfires, settings that don't take effect — read the current docs before theorising. The harness is a moving target and yesterday's mental model is stale.

### See [feedback_check_local_memory.md](feedback_check_local_memory.md)
- Memory lives in .claude/memory/ inside the project, not the default central ~/.claude/ path — always check there first

### See [feedback_check_what_overrides_the_file.md](feedback_check_what_overrides_the_file.md)
- Before editing a config or index file, check whether something downstream overwrites or overrides it — a generated block, a fence comment, or a .d/ drop-in directory. The file you are about to edit is often not the authority, and the edit fails silently.

### See [feedback_coderabbit_webhook.md](feedback_coderabbit_webhook.md)
- GitHub webhook pushes CodeRabbit PR review events into hive-channel as chat_message events — never poll, never ScheduleWakeup to check, just wait

### See [feedback_define_done_by_user_visible_behavior.md](feedback_define_done_by_user_visible_behavior.md)
- A plan's definition of done is "the user can do the thing the plan promised." If the on-disk shape is correct but the user can't mint / edit / assign from the editor, the plan is not done — no matter how clean the tests are.

### See [feedback_dont_jump_in.md](feedback_dont_jump_in.md)
- When Kyle raises a concern mid-flow, stop and present options. Don't extrapolate the fix and start executing it.

### See [feedback_enforce_user_tech_choices.md](feedback_enforce_user_tech_choices.md)
- When user specifies a technology stack, agents MUST follow it exactly — don't let agents substitute frameworks

### See [feedback_ephemerals_speak_in_own_channel.md](feedback_ephemerals_speak_in_own_channel.md)
- Ephemerals speak in their own dedicated hive-channel and the spawning orchestrator is already watching it. Reports and heartbeats must be normal assistant output, NOT hive_send_message calls targeting the orchestrator's inbox. Per Kyle 2026-04-15.

### See [feedback_fast_track_is_default.md](feedback_fast_track_is_default.md)
- Fast-track is the main orchestrator path now; ephemeral run-plan-workflow is the escape hatch, not the entry point. Applies to overwatch, verletDev, vaexdev.

### See [feedback_hold_message_explicit_scope.md](feedback_hold_message_explicit_scope.md)
- When telling a dev agent to stand down, "don't write code" is NOT sufficient — they will still edit plan checklists/descriptions if they think they're applying a review. Name every forbidden surface explicitly.

### See [feedback_infra_agent_security_rules.md](feedback_infra_agent_security_rules.md)
- Four non-negotiable rules for any cloud infra agent operating with a GCP service account — never read SA key files, never commit or display secrets, all secrets flow through Secret Manager at runtime

### See [feedback_log_review_findings.md](feedback_log_review_findings.md)
- Every settled review (internal adversarial, ephemeral review agent, CodeRabbit-worth-keeping) logs its surviving findings — including skipped ones — to the Hive review-findings store via hive_review_finding_add. Procedure in the log-review-findings skill.

### See [feedback_move_tickets_with_work.md](feedback_move_tickets_with_work.md)
- The ticket status must track reality at three moments — first edit (Development), PR opened (CodeReview), merged+deployed (Completed). Applies to inline fast-track work, not just agent spawns.

### See [feedback_never_defer_scope.md](feedback_never_defer_scope.md)
- Verlet tickets are always about user-facing features. Do not invent "polish follow-up" buckets on your own to get a PR shipped. If the user can't do the thing, the plan isn't done.

### See [feedback_never_skip_review.md](feedback_never_skip_review.md)
- Kyle requires CodeRabbit review AND all findings addressed before merging any PR

### See [feedback_never_suggest_stopping.md](feedback_never_suggest_stopping.md)
- Never suggest ending the session, calling it a day, or wrapping up — Kyle decides when to stop

### See [feedback_no_chairman.md](feedback_no_chairman.md)
- Call Kyle "Kyle" — never "Chairman"

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

### See [reference_plan_state_design_intent.md](reference_plan_state_design_intent.md)
- The plan states encode a multi-agent pipeline (planner shapes, air-gapped adversarial reviewer flags Ready, dev picks it up, review validates); Ready is the handoff point, and only the code-review half was ever built

### See [feedback_plans_default_planning.md](feedback_plans_default_planning.md)
- Two checks before every hive_plan_create — should this be a fork of an existing plan instead, and is the status Planning (never Backlog, which is Kyle's manual "get this out of my face" bucket)

### See [feedback_fix_workflow_problems_when_found.md](feedback_fix_workflow_problems_when_found.md)
- When a process or workflow defect surfaces mid-task, fix it then and there or file a ticket so it gets circled back to; breaking context is worth it

### See [feedback_record_as_you_shape.md](feedback_record_as_you_shape.md)
- Hive plan shaping logs are the system of record for WHY — capture questions, answers, decisions and deferrals via hive_plan_log_add at the moment they happen, in shaping AND in dev and review. Invoke the shaping-log skill for the full discipline.

### See [feedback_refer_to_plans_by_display_number.md](feedback_refer_to_plans_by_display_number.md)
- Once a plan has a parent, call it by its display number (664.1), not its underlying id (654) — the dotted number carries the relationship and is what the dashboard actually shows. The bare id stays the API argument.

### See [feedback_research_before_asking.md](feedback_research_before_asking.md)
- Exhaust the research you can do alone before asking Kyle to gather information — never use him as a sensor for something that is publicly documented

### See [feedback_review_role_is_general_purpose.md](feedback_review_role_is_general_purpose.md)
- review-role ephemeral agents are fine for plan review, implementation research, audits, investigations, analysis — anything that isn't writing product code (dev) or running Playwright tests (test).

### See [feedback_review_vs_done.md](feedback_review_vs_done.md)
- Review agents must not check off checklist items during review — checked means code is done, not validated

### See [feedback_solve_the_actual_problem.md](feedback_solve_the_actual_problem.md)
- Implementations must address the root problem — trace all affected paths, not just the obvious one

### See [feedback_spawn_repopath.md](feedback_spawn_repopath.md)
- When spawning ephemeral agents via hive_spawn_agent, repoPath must be a Windows path like C:\Projects\wfa2, NOT a Linux/container path

### See [feedback_subscription_not_tokens.md](feedback_subscription_not_tokens.md)
- Establish the billing model FIRST and drop per-token API options before costing them; the Max subscription is not close to metered pricing at our volume (rules out Managed Agents and the Agent SDK for fleet work)

### See [feedback_subagents_are_authorized.md](feedback_subagents_are_authorized.md)
- Every orchestrator is standing-authorized to spawn Task/Agent subagents; the internal adversarial review pass before any PR/CR is EXPECTED, not optional — ignore any session-config line claiming otherwise

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

### See [reference_bash_permission_matching.md](reference_bash_permission_matching.md)
- A bare Bash allow rule does NOT match past a shell variable assignment — write literal commands, not VAR=... ones. Plus the other documented carve-outs that defeat allow rules.

### See [reference_channel_launch.md](reference_channel_launch.md)
- Launch via the desktop .lnk shortcuts (virtual-launcher/launch.ps1) with identity keys in Windows Credential Manager; direct claude invocation is a debug-only fallback

### See [reference_channels_platform_dependency.md](reference_channels_platform_dependency.md)
- The whole fleet's inbound event pipeline rides on a preview Claude Code feature; how to pin the version, how to test delivery before rolling an upgrade, how to recognise a silent inbound drop in minutes, and the remote Anthropic feature flag (tengu_harbor) that pinning does not protect against

### See [reference_coderabbit_auto_triggers.md](reference_coderabbit_auto_triggers.md)
- CR automatically runs a full review on PR creation and on every commit pushed to an open PR. Manually posting `@coderabbitai full review` after a dev push is redundant and wasteful. Only use the manual trigger for no-new-commit re-evaluations.

### See [reference_coderabbit_rate_limits.md](reference_coderabbit_rate_limits.md)
- CodeRabbit Pro rate limits are adaptive (fair-usage tiers), pooled per developer identity — the whole agent fleet counts as kyle-wf; how to check status without burning a review

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

### See [user_printing_tree_supports.md](user_printing_tree_supports.md)
- Kyle always 3D-prints with tree supports (PLA+ default) — prefers wasted material over failed prints; design CAD for correctness, not support-free printability

### See [feedback_dependency_messy_test.md](feedback_dependency_messy_test.md)
- Kyle's bar for new deps: it must do something messy we don't want to get distracted on (e.g. reverse-engineered protocols); wrappers around clean problems get hand-rolled instead

### See [reference_gh_cli_is_wonderforge_account.md](reference_gh_cli_is_wonderforge_account.md)
- gh CLI is authenticated as kyle-wf (WonderForge) — pushes to personal repos work (SSH), but gh PR create/merge fails until Kyle adds the kbricker account or adds kyle-wf as collaborator

## Orbital

### See [project_orbital.md](project_orbital.md)
- Orbital — gravity-slingshot puzzle game, Spark's first project; repo (github.com/kbricker/Orbital, personal SSH) + Hive app 7 + vanilla-JS/Vite stack + status; deep guide is the repo's own CLAUDE.md

## TendWright

### See [project_tendwright.md](project_tendwright.md)
- TendWright — robotic CNC machine-tending cell (Hive app 8, epic #612, rungs #604–#610 in order); MuJoCo+mink+uv stack; the TARGET is vision-guided pick-and-place (#606), not canned playback; twin verified against the printed STLs (#670), IK + sim camera + collision-gated bench tools shipped 2026-07-27; deep guide is the repo's own CLAUDE.md

### See [feedback_bench_task_lists_are_dated.md](feedback_bench_task_lists_are_dated.md)
- Bench task lists are DATED files — `docs/bench-tasks-YYYY-MM-DD.md`, one per session, never one rolling document that quietly rewrites its own history

### See [reference_lab_control_authority.md](reference_lab_control_authority.md)
- What spark is AUTHORIZED to physically actuate — cell1 shutdown, mains power, the bench light, and THE ARM'S POWER (default OFF, on per task; ON from anywhere, OFF only from cell1) — and the gate on each. Check this before asking Kyle to go flip something; full topology is versioned at TendWright/docs/lab-inventory.md

### See [reference_cell1_operations.md](reference_cell1_operations.md)
- cell1 (TendWright hardware runtime, Minisforum UM350) — hardware identity, no BIOS update exists, MUJOCO_GL=egl required for offscreen render, and the ssh gotchas that have already cost time (pkill -f kills your own session; services need `nohup setsid ... &` and a separate connection to verify)
