# Spark Workspace Memory Index

Spark is the shared virtual orchestrator for Kyle's **small personal projects** (Orbital first). Read this index on startup; the memories it points to encode rules and facts that MUST be followed.

Sections: Spark-local **shared conventions**, then per-**project** sections, then the managed **GLOBAL** block at the bottom (synced from `wfa2/orchestrator-shared/` — do not hand-edit). This index must stay under 25,000 BYTES and 200 lines — bytes bind first; measured comment-stripped, and 25KB means 25,000 not 25,600 (plan 778.1); one line per entry.

## Shared conventions (Spark-local — apply to every small project)

- feedback_personal_repo_git_identity.md — Spark's projects are Kyle's PERSONAL repos — commit as Kyle Bricker <kyle.bricker@gmail.com>, never the WonderForge …
- user_printing_tree_supports.md — Kyle always 3D-prints with tree supports (PLA+ default) — prefers wasted material over failed prints; design CAD for …

## Orbital

- project_orbital.md — Orbital — gravity-slingshot puzzle game, Spark's first project; repo (github.com/kbricker/Orbital, personal SSH) + Hive …

## TendWright

- project_tendwright.md — TendWright — robotic CNC machine-tending cell (Hive app 8, epic #612, rungs #604–#610 in order); MuJoCo+mink+uv stack …
- feedback_bench_task_lists_are_dated.md — Bench task lists are DATED files — `docs/bench-tasks-YYYY-MM-DD.md`, one per session, never one rolling document that …
- reference_lab_control_authority.md — spark may actuate ONLY: cell1 wake (WoL from desk) + shutdown, mains, bench light, ARM POWER (default OFF, per-task; ON anywhere, OFF only from cell1) — powering the arm is mine, MOVING it unattended never is; check each gate first; topology: TendWright/docs/lab-inventory.md
- reference_cell1_operations.md — cell1 (TendWright hardware runtime, Minisforum UM350) — hardware identity, no BIOS update exists, MUJOCO_GL=egl …

## Camera host

- reference_camera_host.md — Camera host (GarageBox, `ssh camhost`, 192.168.86.142) — Dell 7070 SFF Frigate NVR; Docker ready, NO sudo grant, setup doc in CameraHost/

<!-- BEGIN GLOBAL SECTION (managed by propagate-shared-config — do not edit by hand) -->
## Global (managed by propagate-shared-config — copies of `wfa2/orchestrator-shared/memory/`; edit canonical, never these, the next sync reverts local edits silently)
- feedback_always_plan.md — Research and write a formal plan before building — never skip to code; only a true one-line obvious fix skips planning
- feedback_brief_subagents_with_recall.md — Brief a subagent to hive_recall its domain pack before it builds — prefab YAML, shaders and VaEx internals
- feedback_build_straight_through.md — Design locked, Kyle says build/proceed — run the whole plan end-to-end, don't stop to checkpoint after the foundation
- feedback_can_kill_processes.md — Kill only processes you started, by PID — NEVER taskkill //IM dotnet.exe or //IM claude.exe, they nuke Kyle's sessions
- feedback_check_docs_on_harness_friction.md — Read Claude Code docs when shaping any ticket about agent behaviour — docs first, before measuring, not just on friction
- feedback_check_for_an_existing_ticket_before_growing_scope.md — If Kyle has no context for the question you're about to ask, the scope is yours not his — search for an existing ticket
- feedback_check_what_overrides_the_file.md — The file you are about to edit is often not the authority — check for a generated block, fence comment, or .d/ drop-in
- feedback_checklist_items_phase_with_gates.md — Phase checklist items by status gate — anything at-or-after merge is VALIDATION; unchecked TASK items block CodeReview
- feedback_concise_docs_no_ascii.md — Compressing a deliverable doc is a correctness pass, not style — bullets over prose, never ASCII diagrams
- feedback_credentials_radioactive.md — Credentials are radioactive — only forge handles them; never touch a credential yourself, route credential work to forge
- feedback_define_done_by_user_visible_behavior.md — Done means the user can do the thing the plan promised — a correct on-disk shape with no working UI is NOT done
- feedback_dont_assume_staged_scope.md — Don't assume which staged/modified files belong in a commit/PR — if scope is ambiguous, ask Kyle
- feedback_dont_gate_on_manual_validation.md — Don't gate closure on Kyle-only manual or impossible checks — ship non-breaking work to real use, new ticket if wrong
- feedback_enforce_user_tech_choices.md — When user specifies a technology stack, agents MUST follow it exactly — don't let agents substitute frameworks
- feedback_fast_track_is_default.md — Fast-track is THE orchestration path on every plan for every agent — play dev + review inline, fan out to subagents
- feedback_fix_workflow_problems_when_found.md — Fix a workflow or process defect the moment you hit it, or file a ticket to circle back — breaking context is worth it
- feedback_kyle_reads_and_directs.md — Kyle reads and directs, never hands-on — CodeRabbit reviews PRs, agents edit tickets; don't build him hands-on controls
- feedback_kyle_sets_start_and_stop.md — Never suggest stopping/wrapping up, and never start work he hasn't greenlit — Kyle signals both go and stop explicitly
- feedback_log_review_findings.md — Every settled review (internal, subagent, CodeRabbit) logs surviving and skipped findings via hive_review_finding_add
- feedback_move_tickets_with_work.md — Ticket status tracks reality — first edit→Development, PR opened→CodeReview, merged+deployed→Completed; inline work too
- feedback_never_defer_scope.md — Do the scope Kyle named, exactly — never substitute, shift, or defer it; change scope only by convincing him first
- feedback_never_force_push_agent.md — Never force-push a branch from an agent-owned clone others commit to — cherry-pick or rebase instead
- feedback_never_kill_chrome.md — NEVER kill Chrome by any means — Kyle works on this machine and blanket kills destroy his open work
- feedback_no_assign_agent.md — Never set assignedAgent when Kyle is doing the work directly — it can trigger that agent to start working the plan
- feedback_no_claude_artifacts_local_docs_only.md — Never publish docs/reports/charts/dashboards as claude.ai Artifacts — deliverables land on disk in the project folder
- feedback_no_commits_in_agents_working_tree.md — Never commit in a repo checkout an agent is actively working in — check current branch first
- feedback_no_docstrings.md — NEVER write function docstrings anywhere — 100% rule; don't sweep existing ones; ignore CodeRabbit docstring warnings
- feedback_no_new_abstractions_over_canonical_primitives.md — Use the canonical primitive already in the codebase, compose inline — don't invent a parallel abstraction to satisfy DRY
- feedback_no_new_dependencies_without_auth.md — Add a dependency only with a damn-good reason and Kyle's explicit yes — no surprises; propose via the no-new-deps skill
- feedback_no_shims.md — Never leave a forwarder stub behind — delete the old location and update every caller in the same change
- feedback_no_shortcuts.md — No shortcuts — build Hive right the first time; sloppy architecture means endless upkeep that steals game-dev time
- feedback_no_unrequested_ux.md — Plan descriptions and checklists list only behaviors Kyle named — never ship an inferred UX affordance as authorized
- feedback_output_reaches_nobody.md — Virtual agents' terminal output goes only to Kyle's screen — reach any agent via hive_send_message / hive_respond
- feedback_plan_preconditions.md — Before dev, plans name each stateful surface's lifecycle and async flow's staleness/single-flight guard, or none touched
- feedback_plans_default_planning.md — On any new discovery — SEARCH for a home FIRST; a new ticket is the LAST resort; status = Planning, never Backlog
- feedback_prose_reference_is_not_a_link.md — Prose isn't a link — set questionId/index markers in the same edit; review reads prose only, missing links fail silently
- feedback_prove_the_check_ran.md — Prove the check ran before believing what it says — a verification that never applied is as green as correct code
- feedback_read_the_assembled_artifact.md — Read the assembled file in place — correct text goes false by adjacency and no diff shows it; worst when drafted blind
- feedback_record_as_you_shape.md — hive_plan_log_add every entry as it happens (shaping AND dev/review) — the WHY record; entry types in shaping-log skill
- feedback_refer_to_plans_by_display_number.md — Once a plan has a parent, call it by display number (664.1), not bare id (654); the bare id stays the API argument
- feedback_research_before_asking.md — Exhaust your own research before asking Kyle to gather info — never use him as a sensor for what's publicly documented
- feedback_review_vs_done.md — Review agents must not check off checklist items during review — checked means code is done, not validated
- feedback_solve_the_actual_problem.md — Implementations must address the root problem — trace all affected paths, not just the obvious one
- feedback_spawn_tools_retired.md — Never call hive_spawn_agent — the pipeline is retired though the tool still advertises it; fan out subagents instead
- feedback_stay_within_your_remit.md — Findings flow anywhere and are never outside remit; implementation stays within your composed roles in composition.json
- feedback_subagents_are_authorized.md — Adversarial review before any PR/CR is EXPECTED, not optional — EVERY agent may spawn subagents, no permission needed
- feedback_subscription_not_tokens.md — Never propose moving fleet work onto per-token API billing — rule those options out early rather than costing them
- feedback_verify_against_production_before_merging.md — If a change transforms data or adds an invariant, verify the RESULT against production BEFORE merging, not after
- feedback_verify_before_asserting.md — Verify claims against actual state before asserting — never assume; agreement or your own past words aren't verification
- feedback_verify_edit_before_commit.md — A failed Edit (string-not-found) leaves the file unchanged — run git diff before you claim a cleanup/removal landed
- feedback_verify_your_own_harness_state.md — Check the tool in question before accepting any claim about your own session — schema, restart, gating — as a gate
- reference_gh_cli_is_wonderforge_account.md — gh CLI is authenticated as kyle-wf (WonderForge) — it cannot create PRs on kbricker personal repos (Spark projects)
- reference_untrusted_dir_drops_permissions.md — Allow rules inert? Read hasTrustDialogAccepted in ~/.claude.json first — untrusted dirs void .claude/settings.json
<!-- END GLOBAL SECTION -->

<!-- BEGIN ROLE SECTION: orchestrator (managed by propagate-shared-config — do not edit by hand) -->
## Role: orchestrator (managed — byte-identical copies of `wfa2/orchestrator-shared/roles/orchestrator/memory/`; edit canonical, never these)
- feedback_agent_branch.md — Before any agent does work, first instruct it to checkout the correct branch — step 1 for all agents
- feedback_channel_handoff_continuity.md — Kyle's mid-stream switch between desk and Hive channel is the same conversation on a new transport, not a new request
- feedback_channel_rewatch_after_spawn.md — Check hive_channel_watching before calling silent agents stuck — process boundaries clear the process-local watch list
- feedback_hold_message_explicit_scope.md — Standing an agent down must name every forbidden surface — they still edit plan checklists and descriptions
- feedback_orchestrate_proactively.md — After dispatching work to agents, always watch for completion and drive the pipeline forward without being asked
- feedback_use_channel_events.md — Watch for agent_idle/agent_working events from hive-channel instead of blind sleeps when waiting for agent responses
- reference_channel_launch.md — Six VIRTUAL agents: .lnk launchers, plugin channel; hivedev01 has neither by design; read for claudeArgs or deaf agents
<!-- END ROLE SECTION: orchestrator -->

<!-- BEGIN RETRIEVAL SECTION (managed by propagate-shared-config — do not edit by hand) -->
## In retrieval — NOT loaded here; search with hive_recall
These topics were moved out of always-loaded memory. The facts are intact and searchable; only the text left this index. Behavioural rules are never in here.
- github ssh · plan state design intent · plan completion path · channels platform dependency · virtual orchestrators · 3dproppipeline agent · how to reach another agent · forge agent · bash permission matching
<!-- END RETRIEVAL SECTION -->
