---
name: feedback_check_for_an_existing_ticket_before_growing_scope
description: Before adding a section of scope to a plan you're writing, search for an existing ticket that already owns that problem — and if Kyle has no context for a question you're about to ask him, the scope is yours, not his
metadata:
  type: feedback
scope: global
---

When shaping a plan, do not grow a new area of scope inside it because a doc or a review sentence made the area feel urgent. **First search the plan list for a ticket that already owns that problem.** If one exists, the work belongs there and the new plan links to it.

Kyle, 2026-08-02, on plan #754: *"stop asking about this shit, geez. we have other tickets already that deal with this problem, why are you hyperventilating on this has NOTHING to do with the ticket we're closing out"* and *"why is it even tied to 754??? it HAS NOTHING to do with this change"*.

**What happened.** He raised #754 as a *vendor risk* worry: the whole fleet's inbound event pipeline rides on `--dangerously-load-development-channels`, a flag on an unstable preview contract, and if Anthropic changes it every orchestrator goes deaf. While writing the plan I read one line in Anthropic's channels docs — "an ungated channel is a prompt injection vector" — and grew an entire webhook-auth security audit inside it. Six of the plan's eight checklist items were that audit. None of it was asked for, and #722, #730 and #680 already owned the authority model. Then I compounded it by putting auth-model policy questions in front of Kyle, who answered *"I have no idea what you are talking about"* — because it was never his thread.

**Why it matters.** Scope grown this way is invisible: it looks like diligence, it passes review, and it buries the one or two things the person actually asked for. It also splits a problem across two tickets so neither is the real home, and it burns Kyle's attention on decisions he never opened.

**How to apply:**
- Before writing a scope section into a plan, run `hive_plan_list` (or `search`) for the problem area. An existing ticket is the default home.
- **The clearest tell that scope is yours and not his: you are about to ask him a question he has no context for.** If explaining the question requires first explaining why it's on this ticket, it isn't. Stop and check for the real owner before asking.
- Re-read what the person actually said when they raised the plan. #754's origin was "what if this flag breaks" — a version/pinning question. Nothing in it was about attackers.
- Re-homing is cheap and non-destructive: land real checklist items on the owning ticket first, then remove them from the wrong one, then record the disposition in both shaping logs so citations stay resolvable. Never just delete.
- A "not in scope" section naming where the work went, with item ids, stops the next session pulling it back in.

Related: [[feedback_no_unrequested_ux]], [[feedback_dont_jump_in]], [[feedback_never_defer_scope]], and the `manage-scope-creep` skill (which covers dev/review-time creep; this one is about creep at *shaping* time, which the skill does not catch).
