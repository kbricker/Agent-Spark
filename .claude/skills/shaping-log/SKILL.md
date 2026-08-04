---
name: shaping-log
description: How to capture decisions, questions and deferrals in Hive plan shaping logs. Invoke whenever a choice gets made, a question gets raised or answered, or scope moves — during shaping AND during dev and review. This is the corpus agents mine to become more autonomous; coverage must be 100%.
scope: global
---

# Shaping Log Discipline

**Hive plan shaping logs are the system of record for WHY.** Not commit
messages, not a markdown file in a repo, not chat history. Kyle 2026-07-27:
*"the handling of tickets and shaping logs needs to be 100%, its the basis for
our 'meta work' with the hive so agents can learn from things and become more
autonomous."*

That last clause is the whole point and it changes the standard. A log entry is
not paperwork for a human to read later — it is **the corpus every future agent
mines to understand why the system is the way it is.** Patchy logs mean every
agent re-derives from scratch, re-proposes rejected options, and re-litigates
settled calls. Complete logs are how an agent picks up a three-week-old project
and acts instead of asking.

## Invoke this skill when

- A choice gets made, however small it feels at the time
- A question is raised that you cannot answer yet
- A question gets answered — link it to the question
- Scope moves to another plan, or gets cut
- A check, assumption or earlier decision turns out to be **wrong**
- You are about to write a good commit message about a decision. Log it first;
  the commit message is a summary of the log entry, never a replacement for it.

**Log AS IT HAPPENS, not in a sweep at the end.** A sweep only happens if
someone asks, and by then the reasoning has decayed to its conclusion. The
reasoning is the valuable part; the conclusion is already in the code.

## Entry types, and what each is for

`hive_plan_log_add` takes: `question`, `answer`, `decision`, `deferral`, `note`.

- **decision** — a choice was made. The default and most common.
- **question** — raised, not yet resolved. Stays `open=true` until answered.
- **answer** — resolves a question; pass `questionId` to link it. An unlinked
  answer leaves the question open forever.

  **A question raised in the plan's DESCRIPTION has no id, so its answer cannot
  be logged directly** — `hive_plan_log_add` returns `400: Answer entries
  require questionId`. This is common: plans routinely raise open questions in
  their prose ("open art call for Kyle: 4K or 1K?") long before anyone answers
  them. Log a `question` entry first, capturing it verbatim from the
  description, then log the `answer` against that id. Two calls, not one.

  Do this rather than downgrading the answer to a `note`. A note records what
  was decided but leaves nothing marked as having been open, so the plan reads
  as though the question was never asked — and the open-question sweep in the
  review pass has nothing to close. (Found by vaexdev2 on #794, 2026-08-04.)
- **deferral** — scope moved. Requires `disposition`: `PREREQUISITE` (must
  happen first), `FOLLOW_UP` (later), `PRECLUDED` (will not happen). Pass
  `linkedPlanId` when it landed somewhere.
- **note** — context that is not a choice: research findings, a correction, a
  process observation.

Entries are **immutable**. A correction is a new entry, never an edit. That is
deliberate — being able to see that a decision was reversed, and why, is more
valuable than a tidy history.

## Scope splits go through `hive_plan_fork`, never hand-rolled

When work moves to a new plan, **fork it** — `hive_plan_fork`, not
`hive_plan_create`. Fork stamps lineage on both ends and auto-appends a linked
deferral on the parent from its reason field. A hand-rolled create gives you two
plans with no relationship, and the connection then lives only in whatever prose
someone remembered to write.

The ordering that follows from that:

- Target plan **already exists** → log the deferral with `linkedPlanId`.
- Target plan **does not exist yet** → log the deferral unlinked, then fork. The
  fork completes the link itself; do not pre-empt it.
- Target plan was created **outside** fork → append a manual linking entry. A new
  entry, never an edit to the original.

### A new finding is not a split — use `create`, and record the provenance

Fork is for scope **leaving** a plan. It appends a *deferral* to the parent, and a
deferral asserts that scope which was in that plan is now somewhere else.

Work that was never in the parent's scope has nothing to defer. A finding
discovered *while doing* a plan's work — a bug the bench run surfaced, a gap the
tooling exposed — is a **new plan**, created with `hive_plan_create`. Forking it
would stamp a lineage that does not exist and tell a later reader the parent shed
scope it never had.

But the relationship is real, so record it. It is **provenance, not scope**:

- a **note** on the originating plan — *"this work surfaced #708"*
- a **note** on the new plan — where it came from and what was being done at the
  time

That keeps the trail an agent needs (what were we doing when we found this?)
without falsifying what the parent ever promised.

The test: **did this scope ever belong to the parent?** Yes → fork. No, we merely
found it there → create, and note it at both ends.

*(spark 2026-07-28, on #708/#709: "neither was scope moving off an existing plan;
both were new findings from bench work ... flagging it in case you intended fork
to cover new-discovery tickets too, since the lineage argument would apply there
as well." The lineage argument does apply — it just wants a note, not a deferral.)*

## Capture does not stop when dev starts

Kyle 2026-07-23: *"this whole system is about traceability."* Shaping-time
capture is the obvious half; the half people drop is everything that happens
after the plan leaves Planning.

- **A scope deferral discovered DURING review** — a skipped finding pushing work
  to another plan — gets a linked deferral entry, exactly as one discovered
  during shaping. Where you noticed it does not change what it is.
- **When a review-driven change alters what the plan text promises**, that is a
  *contract change*: the finding records the catch AND a decision entry records
  the contract change. A later reader sees plan text that no longer matches
  shipped behaviour, and the shaping log is where they look for why.
- **In-scope implementation fixes stay findings-only.** No double-logging.

**"Contract" means operator-visible promises only** (Kyle 2026-07-24): what the
tool or feature promises its user — inputs required, what flags mean, refusal
conditions. Internal architecture or topology diverging from the plan text does
NOT qualify.

> #643 — plan promised "requires all six joints"; the refusal condition changed.
> That is a contract change and gets a decision entry.
>
> #645 — plan said "capture thread", implementation deliberately runs capture on
> the main thread. Internal topology. Findings-only, no log entry.

## What a good entry contains

A bare outcome is nearly worthless. Every entry should carry:

1. **The decision, stated plainly** in the first line so it is scannable.
2. **The reasoning** — what made this the answer.
3. **The rejected alternative and why.** This is the single highest-value part.
   A future agent that cannot see what was rejected will propose it again.
4. **The number that settled it**, if there was one. `R0=150mm needs 274.4° of
   270°` beats "the layout did not close".
5. **Kyle's own words, verbatim**, when the decision came from him. Most
   corrections start with him looking at something and saying it does not make
   sense — that phrasing is what is still legible weeks later, and it carries
   intent that a paraphrase loses.
6. **What is still unresolved** — an entry that implies more certainty than
   exists is worse than no entry.

Length is not a virtue but neither is brevity. Write what a competent stranger
needs to not redo the work.

### Two shapes worth copying

**When a check or assumption was wrong** — record the miss as carefully as the
fix, and name the root cause, not just the symptom:

> UNCHECKING the collision item. It was ticked on the strength of two studies,
> neither of which tests collision. ROOT CAUSE: every geom carries
> `contype="0"` — contacts are disabled for render speed, so bodies pass
> through each other silently. The word "collision" appeared in a checklist
> item, a study name and a commit message and was never computed anywhere.

**When the user's framing beat yours** — say so plainly, quote them, and record
what your framing got wrong. This is the most useful entry type for training a
successor, and the least comfortable to write:

> Kyle: *"those are late milestone stations I think everything is based on."*
> He is right and it was a real structural error. Press-first ordering is
> correct for the finished machine, but applying it to the Phase 1 gate meant
> S1/S2/S3 were blocked on hardware they never touch.

## What does NOT go in the shaping log

Deliverables stay in the repo: specs, cut sheets, BOMs, runbooks, generated
drawings, READMEs. **A summary doc in the project is fine** (Kyle 2026-07-27:
*"I dont mind having a summry doc in the project"*) — what is not fine is that
doc being the only place the reasoning lives, or being richer than the ticket.

The test: if a new agent had only Hive and no repo, could it understand why?
If not, the log is incomplete.

## Verification — coverage is a claim, so check it

Before saying a session is captured, actually look:

```
hive_plan_log(id=<plan>)                    # read it back
hive_plan_log(id=<plan>, type="decision")   # decisions only
git log --oneline --since=<start>           # compare against commits
```

**Rule of thumb: every commit that changed a design should map to a log entry.**
A day with 16 commits and 2 entries is not covered, whatever it feels like.
That exact gap is why this skill exists.

Also check for **open questions that were silently answered** — a question left
`open=true` after it was resolved is a trap for the next agent, who will either
re-ask it or treat a settled thing as unsettled.

## Which plan does an entry belong to?

The plan whose work produced it. If a decision spans plans, log it on the one it
constrains most and add a short pointer entry on the other. Do not duplicate the
full text — two copies drift, and the drift is invisible.

If no plan fits, that is usually a signal the work is untracked. File the ticket
first, then log against it.

## Why this is meta-work, not bookkeeping

Kyle's framing: these logs are how agents **learn from things and become more
autonomous.** Concretely, a well-logged plan lets a future agent:

- Skip re-proposing an option that was already priced and rejected
- Inherit the constraint that drove a choice, not just the choice
- See which numbers are measured, which are estimated, and which are guesses
  someone is about to trust
- Recognise a mistake it is about to repeat, because the last one was recorded
  with its root cause

Every entry written well is one less question a future agent has to ask, and one
less wrong turn it has to take. That compounds — which is exactly why coverage
has to be 100% rather than "pretty good".

## Provenance

The shaping-log platform is #620/#621; adoption across agents is #629. The
mining side — which is what makes coverage worth enforcing — is #623 (task
ripeness) and #624, and #641 (Earned Autonomy) consumes the result. #624 could
only recover what was durably recorded at the time, which is the whole argument
for capture-at-the-moment over end-of-session summaries: a summary flattens the
decision sequence into its conclusion, and the sequence is the part with
information in it.

This skill is the canonical statement of the discipline. The always-loaded
memory `feedback_record_as_you_shape` is a pointer to it, deliberately short —
if the two ever disagree, this file wins and the memory is stale.
