# Spark Workspace Memory Index

Spark is the shared virtual orchestrator for Kyle's **small personal projects** (Orbital first). Read this index on startup; the memories it points to encode rules and facts that MUST be followed.

Sections: Spark-local **shared conventions**, then per-**project** sections, then the managed **GLOBAL** block at the bottom (synced from `wfa2/orchestrator-shared/` — do not hand-edit). This index must stay under 25,000 BYTES and 200 lines — bytes bind first; measured comment-stripped, and 25KB means 25,000 not 25,600 (plan 778.1); one line per entry.

## Shared conventions (Spark-local — apply to every small project)

- feedback_personal_repo_git_identity.md — Committing in a Spark project? Kyle's PERSONAL repo — commit as Kyle Bricker <kyle.bricker@gmail.com>, never WonderForge
- user_printing_tree_supports.md — Designing a part for 3D print? Kyle always uses tree supports — don't contort CAD toward support-free geometry

## Orbital

- project_orbital.md — Orbital — gravity-slingshot puzzle game, Spark's first project; repo (github.com/kbricker/Orbital, personal SSH) + Hive …

## TendWright

- project_tendwright.md — TendWright — robotic CNC machine-tending cell (Hive app 8, epic #612, rungs #604–#610 in order); MuJoCo+mink+uv stack …
- feedback_bench_task_lists_are_dated.md — Writing a TendWright bench task list? Dated file docs/bench-tasks-YYYY-MM-DD.md, one per session — never one rolling doc
- reference_lab_control_authority.md — spark may actuate ONLY: cell1 wake (WoL from desk) + shutdown, mains, bench light, ARM POWER (default OFF, per-task; ON anywhere, OFF only from cell1) — powering the arm is mine, MOVING it unattended never is; check each gate first; topology: TendWright/docs/lab-inventory.md
- reference_cell1_operations.md — cell1 (TendWright hardware runtime, Minisforum UM350) — hardware identity, no BIOS update exists, MUJOCO_GL=egl …

## Camera host

- reference_camera_host.md — Camera host (GarageBox, `ssh camhost`, 192.168.86.142) — Dell 7070 SFF Frigate NVR; NOPASSWD sudo, BIOS needs USB flash not fwupd, setup doc in CameraHost/

<!-- BEGIN GLOBAL SECTION (managed by propagate-shared-config — do not edit by hand) -->
## Global (managed by propagate-shared-config — copies of `wfa2/orchestrator-shared/memory/`; edit canonical, never these, the next sync reverts local edits silently)
- feedback_always_plan.md — Reaching for the editor before a plan exists? Only a true one-line obvious fix skips planning — write the plan first
- feedback_anchor_propagation_checks_on_the_commit.md — Checking a propagation landed? A clean tree is success, not absence — verify with git log against the commit you knew
- feedback_brief_subagents_with_recall.md — Spawning a subagent on domain work? Tell it to hive_recall its pack first — prefab YAML, shaders, VaEx internals
- feedback_build_straight_through.md — Design locked, Kyle says build/proceed — run the whole plan end-to-end, don't stop to checkpoint after the foundation
- feedback_can_kill_processes.md — Reaching for taskkill? Kill only what you started, by PID — image-name kills are denied and provenance is still on you
- feedback_check_docs_on_harness_friction.md — Read Claude Code docs when shaping any ticket about agent behaviour — docs first, before measuring, not just on friction
- feedback_check_for_an_existing_ticket_before_growing_scope.md — If Kyle has no context for the question you're about to ask, the scope is yours not his — search for an existing ticket
- feedback_check_what_overrides_the_file.md — About to edit a config/memory/index file? Ask what ASSEMBLES it first — a generated block or .d/ drop-in silently wins
- feedback_checklist_items_phase_with_gates.md — Writing a plan's checklist? Phase by status gate — at-or-after-merge is VALIDATION; unchecked TASKs block CodeReview
- feedback_concise_docs_no_ascii.md — Writing or compressing a doc for Kyle? It's a correctness pass, not style — bullets over prose, never ASCII diagrams
- feedback_correct_the_assertions_not_just_the_log.md — Logged a change to a plan? A reader acts on its description and checklist — a log entry does not update those
- feedback_credentials_radioactive.md — Task would have you read, paste, or handle a key or token? Stop — credentials are radioactive, route it to forge
- feedback_define_done_by_user_visible_behavior.md — Marking done because the on-disk shape is right? Not done until the user can actually do the thing the plan promised
- feedback_delegation_boundary.md — Handing work off or spawning an agent? Inline for tight loops, subagent by default, named agent only if it earns it
- feedback_dont_assume_staged_scope.md — About to commit the staged/modified files? Don't assume they're all yours — if the scope is ambiguous, ask Kyle
- feedback_dont_gate_on_manual_validation.md — Closure blocked on a check only Kyle can run, or that can't happen? Ship non-breaking work to use; new ticket if wrong
- feedback_enforce_user_tech_choices.md — When user specifies a technology stack, agents MUST follow it exactly — don't let agents substitute frameworks
- feedback_fast_track_is_default.md — Starting any plan? Fast-track is the path — play dev + review inline, fan out to subagents; there is no other pipeline
- feedback_fix_workflow_problems_when_found.md — Hit a workflow or process defect mid-task? Fix it now or ticket it — breaking context is worth it; don't just note it
- feedback_harness_index_size_nag_is_advisory.md — 'Compact MEMORY.md to under 17.1KB' after an edit? Harness 70% warning; the fleet limit is 25,000 bytes — do not compact
- feedback_kyle_reads_and_directs.md — About to build Kyle a button or hands-on control? Don't — he reads and directs; CodeRabbit reviews, agents edit tickets
- feedback_kyle_sets_start_and_stop.md — About to suggest wrapping up, or start the next thing unprompted? Kyle signals go and stop explicitly — wait for both
- feedback_log_review_findings.md — A review just settled? Not finished until surviving AND skipped findings are in the store via hive_review_finding_add
- feedback_move_tickets_with_work.md — Started or stopped a ticket? Move it (Development/CodeReview/Completed) and declare it: hive_set_status planId or ""
- feedback_never_defer_scope.md — About to trim, shift, or defer what Kyle named? Don't — do the scope exactly; change it only by convincing him first
- feedback_never_force_push_agent.md — About to force-push from an agent-owned clone others commit to? Don't — cherry-pick or rebase instead
- feedback_never_kill_chrome.md — Reaching to kill Chrome — even by PID, even a wedged tab? Never; only scoped CDP Browser.close (kill-guard blocks names)
- feedback_no_assign_agent.md — Setting assignedAgent on a plan Kyle is working himself? Don't — it can wake that agent to start working the plan
- feedback_no_claude_artifacts_local_docs_only.md — Publishing a doc, report, chart, or dashboard as a claude.ai Artifact? Never — deliverables land on disk in the project
- feedback_no_commits_in_agents_working_tree.md — About to commit in a clone an agent works in? Check the current branch first — never commit into its working tree
- feedback_no_docstrings.md — Adding a function docstring, or CodeRabbit wants one? Never — 100% rule; ignore the warning, don't sweep existing ones
- feedback_no_new_abstractions_over_canonical_primitives.md — Tempted to wrap repetition in a new helper for DRY? Use the canonical primitive already there, compose inline instead
- feedback_no_new_dependencies_without_auth.md — Adding a package or dependency? Only with a damn-good reason and Kyle's explicit yes — propose via the no-new-deps skill
- feedback_no_shims.md — Moving or renaming code? Delete the old location and update every caller in the same change — no forwarder stub
- feedback_no_shortcuts.md — The quick way tempting? Build Hive right the first time — sloppy architecture means upkeep that steals game-dev time
- feedback_no_unrequested_ux.md — An obvious UX nicety feels implied? Not authorized — plans list only behaviors Kyle named; never ship inferred ones
- feedback_output_reaches_nobody.md — Reply meant for another agent? From a primary session it reaches only Kyle — use hive_send_message / hive_respond
- feedback_pair_directive_briefs_with_dissent.md — Writing a confident technical claim into a subagent brief? Pair it with an explicit invitation to contradict it
- feedback_plan_preconditions.md — Moving a plan past Planning? Name each stateful surface's lifecycle and each async flow's staleness/single-flight guard
- feedback_plans_default_planning.md — New discovery or finding? SEARCH for a home first — a new ticket is the last resort; status Planning, never Backlog
- feedback_prose_reference_is_not_a_link.md — Wrote 'see the X above'? Prose isn't a link — set the questionId/index marker in the same edit or it fails silently
- feedback_prove_the_check_ran.md — A check came back green? Prove it actually ran — a verification that never applied looks identical to correct code
- feedback_read_the_assembled_artifact.md — Your diff looks right? Read the assembled file in place — correct text goes false by adjacency and no diff shows it
- feedback_record_as_you_shape.md — A question, answer, or decision just happened? hive_plan_log_add it now, not later — batching loses the WHY record
- feedback_refer_to_plans_by_display_number.md — Naming a parented plan to a reader? Use its display number (664.1), not the bare id (654) — bare id stays the API arg
- feedback_research_before_asking.md — Think 'only Kyle can know this'? Usually wrong — a model or version number means it's documented. Search before you ask
- feedback_review_vs_done.md — Reviewing and tempted to tick checklist items? Don't — checked means the code is done, not that review validated it
- feedback_solve_the_actual_problem.md — Fixing the obvious path? Trace every affected path first — address the root problem, not just the literal ask
- feedback_spawn_tools_retired.md — hive_spawn_agent still shows in the tool list? It's retired — never call it; fan out subagents instead
- feedback_stay_within_your_remit.md — A finding outside your area feels 'not my remit'? Report it — findings flow anywhere; only IMPLEMENTATION stays in roles
- feedback_subagents_are_authorized.md — Need permission to spawn a reviewer, or the diff too small? No — adversarial review before any PR/CR is expected
- feedback_subscription_not_tokens.md — Weighing an option that bills per-token API? Rule it out early — fleet work stays on the subscription, don't cost it
- feedback_test_everything_mechanically_testable.md — Handing Kyle something to try? Run every machine-runnable check yourself first — his time is for eye/flow/UX/gameplay
- feedback_verify_against_production_before_merging.md — Change transforms data or adds an invariant? Verify the RESULT against production BEFORE merging, not after
- feedback_verify_before_asserting.md — Stating as fact something unchecked this turn? Verify — another agent agreeing, or your own past words, isn't proof
- feedback_verify_edit_before_commit.md — Claiming a cleanup or removal landed? git diff first — a failed Edit (string-not-found) leaves the file unchanged
- feedback_verify_your_own_harness_state.md — A claim about your own session — restarted, gated, schema changed? Check the tool itself before you accept it
- reference_gh_cli_is_wonderforge_account.md — Using gh on a kbricker personal repo (Spark)? It's authed as kyle-wf (WonderForge) and can't create PRs there
- reference_untrusted_dir_drops_permissions.md — Allow rules inert? Read hasTrustDialogAccepted in ~/.claude.json first — untrusted dirs void .claude/settings.json
<!-- END GLOBAL SECTION -->

<!-- BEGIN ROLE SECTION: orchestrator (managed by propagate-shared-config — do not edit by hand) -->
## Role: orchestrator (managed — byte-identical copies of `wfa2/orchestrator-shared/roles/orchestrator/memory/`; edit canonical, never these)
- feedback_agent_branch.md — Before any agent does work, first instruct it to checkout the correct branch — step 1 for all agents
- feedback_channel_handoff_continuity.md — Kyle messages from the Hive channel mid-task? Same conversation on a new transport — not a new request, don't restart
- feedback_channel_rewatch_after_spawn.md — An agent gone silent — stuck, or unwatched? Check hive_channel_watching first; any process boundary clears that list
- feedback_hold_message_explicit_scope.md — Standing an agent down? Name every forbidden surface — a plain HOLD still lets it edit plan checklists and descriptions
- feedback_orchestrate_proactively.md — After dispatching work to agents, always watch for completion and drive the pipeline forward without being asked
- feedback_use_channel_events.md — Waiting on an agent's response? Watch for agent_idle/agent_working channel events — never a blind sleep
- reference_channel_launch.md — Five PRIMARY agents: .lnk launchers, plugin channel; 3dpp is RemoteAgent-hosted; read for claudeArgs or deaf agents
<!-- END ROLE SECTION: orchestrator -->

<!-- BEGIN RETRIEVAL SECTION (managed by propagate-shared-config — do not edit by hand) -->
## In retrieval — NOT loaded here; search with hive_recall
These topics were moved out of always-loaded memory. The facts are intact and searchable; only the text left this index. Behavioural rules are never in here.
- github ssh · plan state design intent · plan completion path · channels platform dependency · primary agents · 3dproppipeline agent · how to reach another agent · forge agent · bash permission matching
<!-- END RETRIEVAL SECTION -->
