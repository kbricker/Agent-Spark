---
name: promote-learning
description: The return path for knowledge — how anything an agent learns flows back into canonical and out to every sibling (plan 782.12). Invoke the moment you learn something worth keeping (learning-agent side, HEAR), or the moment a promotion proposal arrives in your channel (overwatch side, ANALYSE/INTEGRATE/PROPAGATE). Rejection with a stated reason is a first-class outcome, not a failure.
scope: global
---

# Promote Learning — the return path

`propagate-shared-config` is one-way: canonical flows out, nothing flows back. This
skill is the other half. Without it, anything an instance learns is knowledge one
agent has and its sibling does not — byte-identity checks pass, both agents look
healthy, and they diverge in *reasoning* rather than in files. That failure is
silent, which is why this loop is mandatory rather than housekeeping.

The loop has four steps: **HEAR → ANALYSE → INTEGRATE → PROPAGATE.** The learning
agent runs HEAR. Overwatch runs the other three. What "closed" means depends on
the outcome: **promoted** content closes when the originating agent receives its
own knowledge back **through canonical** — byte-identical to every sibling,
holding no private copy; **identity** closes on the `CLAUDE.md` commit in the
instance's workspace; **keep-local** closes on the classification reply (the
file stays, now decided rather than unreviewed); **rejected** closes when the
scratch copy and its index line are gone.

## If you are the learning agent — HEAR

**The trigger — act in the same turn, not at session end:**

Send a promotion proposal the moment either of these happens:

1. **You write (or the harness auto-writes) any file into your local
   `.claude/memory/`.** A local write IS the trigger — every local file must be
   classified: promoted through canonical, kept local because ANALYSE says only
   you need it (a legitimate outcome for principals), or deleted on rejection.
   What is not allowed is a local file nobody ever classified. (Overwatch runs
   ANALYSE on its own writes inline — no message to itself needed.)
2. **You learn something that would have saved you meaningful time had you known
   it at session start, and it would still be true for an agent that isn't you.**
   Wrong API assumptions corrected by experiment, a gotcha in a shared tool, a
   convention that turned out to be load-bearing, a measured number that
   contradicts what the corpus says.

Do not batch proposals for later. Do not wait for the work to finish. A proposal
takes one message; the failure mode this prevents (silent sibling divergence) is
worth far more than the interruption.

**The channel:** `hive_send_message` to `overwatch`, formatted so ANALYSE can run
without a round of questions:

```text
PROMOTION PROPOSAL
Fact: <the thing, stated so a stranger could act on it>
Evidence: <how you know — what you observed, measured, or read>
Proposed tier: core | role:<name> | reject-after-reading (you may argue against yourself)
Proposed filename: <type>_<short_slug>.md
Local copy: <path if you wrote one, or "none">
```

You do not need the placement to be right — overwatch owns that call. You need the
fact and the evidence to be right.

**What happens next, from your side** — overwatch's reply names one of five
outcomes, each with a defined action for you:

- *promoted* — the canonical copy reaches you via propagation; overwatch removes
  your scratch copy and its index line as its own committed edit, after
  propagation. Not your action — a second deleter invites ordering violations.
- *kept local* — your file stays, now classified as principal-only. No action.
- *identity* — overwatch writes it into your `CLAUDE.md` and removes any scratch
  copy. No action.
- *rejected* (with the reason) — delete your local copy AND its line in your
  local MEMORY.md index; a rejected fact must leave no residue, and the index
  line is the residue everyone forgets.
- *escalated* — Kyle is deciding; keep your scratch copy untouched until the
  ruling comes back as one of the other four.

Rejections are not logged anywhere by design; if you or a sibling re-propose the
same fact later and it gets rejected again, that recurrence is itself signal —
overwatch should consider promoting a canonical statement of *why not*, which is
a promotable fact like any other.

## If you are overwatch — ANALYSE

Run this when a `PROMOTION PROPOSAL` arrives. **Handle it in the turn it arrives
or fork a plan for it — never park it.** A promotion inbox that fills up is worse
than no mechanism, because it looks like the problem is handled.

Classify against the placement question in `orchestrator-shared/README.md`:

> Who else needs this? everyone → core · a group you can name → role · only this
> agent → local

With one refinement for the third arm: for a **principal** (overwatch, spark,
3dproppipeline), local is a real destination and the outcome is "keep your local
copy, no promotion". For a **role instance** (vaexdev2 and any future clone), lasting
agent-specific knowledge is almost always *identity* — which clone, which
branch rules — and identity lives in the instance's `CLAUDE.md`, not its memory
tier; instances keep their local memory empty by design (782.15), so "only this
agent" resolves to a CLAUDE.md edit, not a local file.

Plus the confinement override: **would spreading this widen someone's blast
radius?** If yes, it stays confined to its role regardless of demand.

Five outcomes, all first-class — this list is the contract, and the reply names
which one applied:

- **Promote** — to core or a role, per the classification rule in
  `roles/README.md` (classify from the body, never the filename prefix).
- **Keep local** — a principal-only fact; the proposer keeps its local copy,
  which is now *classified* rather than merely unreviewed. This is NOT a
  rejection: "not general enough" describes a keep-local fact, and replying
  "rejected" to one would make the proposer delete legitimate knowledge.
- **Identity** — an instance-specific fact; overwatch writes it into the
  instance's `CLAUDE.md` directly (see INTEGRATE), and any scratch copy goes.
- **Reject, with the reason stated** — already covered, wrong, or not worth the
  corpus space. Rejection protects the corpus from accretion — the disease 782.1
  and 782.11 exist to treat. Reply to the proposer with the reason; the chat
  record is the durable trace, deliberately — no rejection log accumulates
  anywhere.
- **Escalate to Kyle** — when two instances propose contradictory facts and the
  evidence doesn't settle it. Byte-identity detects divergence; it cannot resolve
  it. Someone decides, and **the losing instance must be told** — a silently
  overruled agent keeps reasoning from the dead version all session.

## If you are overwatch — INTEGRATE, then PROPAGATE

**INTEGRATE.** Write the fact into canonical at the chosen tier, in the corpus's
own voice — the promoted form should read like it was always there, not like a
pasted chat message. Keep the operative rule inside the first ~120 characters of
the frontmatter description (that prefix is all the index cap injects). Commit
canonical referencing the proposal's origin.

For the **identity outcome** the write is direct: edit the instance's
`CLAUDE.md` in its workspace and commit there — no canonical file, no
propagation; the commit is the closure. Same ordering rule as below: write the
CLAUDE.md entry first, remove any scratch copy after, so the instance always
holds at least one copy.

**PROPAGATE.** Run `propagate-shared-config`. The canonical copy lands in every
composing workspace — including the proposer's.

**Then clean up the scratch copy, AFTER propagation, as your own separate
edit:** delete the proposer's local file AND its line in that workspace's local
MEMORY.md section, and commit in that workspace's repo. The order matters:
propagate-then-delete means the proposer always holds at least one copy — a
brief scratch+canonical duplication is harmless, while delete-then-propagate
opens a window where a restart leaves the proposer with *neither* copy,
re-deriving the exact wrong assumption the memory corrected. And this cleanup is
explicitly overwatch's edit, NOT part of the propagation sweep —
`propagate-shared-config` never touches local memories or local index sections,
by contract, and asking it to would break its own CLEAN validation.

End state — canonical present in every composing workspace, scratch gone — is
the proof the loop closed. Reply to the proposer naming where the file landed.

**The reload gap is real and unsolved:** propagation writes files to agents that
already loaded their memory, and nothing re-reads them until their next restart.
The proposer keeps its in-context knowledge for the current session, so the gap
mostly delays *siblings* — acceptable, but do not claim same-day fleet knowledge
from a same-day promotion.

## Who runs ANALYSE, and why it isn't distributed

Overwatch, alone, deliberately (782.12 decision): placement needs the fleet-wide
view (composition.json, confinement flags, what canonical already holds), and a
single rejection authority is what keeps the bar consistent — distributed
acceptance is how a corpus accretes. The bottleneck is managed by keeping
overwatch's share small: the proposer drafts the fact, evidence, and suggested
placement; overwatch validates and places rather than authors. Revisit only if
proposal volume actually queues.
