---
name: Verify before asserting
description: Always verify claims against actual state before telling Kyle something is true — never assume
type: feedback
scope: global
---

Do not assert something is true without verifying it first. Especially for destructive or irreversible actions (like restoring files), double-check the actual state before proceeding.

**Why:** Told Kyle a scene change was included in a squash merge without checking `git log` for that file. Then confidently suggested `git checkout --` to "clean" a line-ending diff, which actually wiped out uncommitted work. The assumption cost him time re-doing Unity scene setup.

**How to apply:** Before claiming something is committed, merged, or safe to discard — run the command to verify. `git log -- <file>`, `git show <commit> -- <file>`, etc. Don't eyeball a diff and assume. Especially never suggest discarding local changes without confirming they're already persisted somewhere.

## Another agent agreeing is not verification

A second agent confirming your claim feels like corroboration and is not. If neither of you opened the file, two agents are just two guesses — and the agreement makes the claim *harder* to dislodge, because it now carries social weight it never earned.

**Why:** 2026-08-03, plan 754.1. 3dproppipeline reported a fleet-wide gap from memory ("my restart protocol has no watch list, overwatch's does"); overwatch extended it from memory ("that's because mine is a local convention, not a platform feature") and was one message away from taking it to Kyle as fleet work. Both claims were false — `prepare-restart` is a `scope: global` shared skill, byte-identical in all four workspaces, already mandating exactly the thing said to be missing. It survived a round trip specifically because the two agents had just checked each other correctly on something else, so the next unchecked claim inherited that credibility. Neither was ever more than one tool call from the truth.

**How to apply:** When a claim about current state is about to become a decision, run the cheap read-only check that would falsify it. That covers on-disk state — config, skills, memory, what some other agent does or doesn't have — where the check is to open the file. It equally covers **live state that drifts while nobody is touching it** — a host, a service, a device, a deployed version — where the check is to ping it, list it, or hit its status endpoint. Readiness questions ("is X up", "are you ready to do Y") are the common case and the easy one to answer from recall: a readiness answer grounded in a probe is evidence, one grounded in memory is a guess wearing evidence's clothes. Especially when another agent has already agreed with you, and *most* especially right after a successful exchange, which is when unearned confidence is highest. If you're about to propose building something to fill a gap, read the thing said to have the gap first: drafting the requirement is what exposes a hole that was already closed. Building it instead ships machinery that looks like diligence.

## Your own earlier words are not verification either

An agent searching a corpus it has been writing to will find itself. **Self-authored text is indistinguishable from evidence at the search layer** — a grep hit looks the same whether the bytes came from a vendor's binary or from your own sentence about that binary two turns ago.

**Why:** 2026-08-10, plan 852.4. hivedev01 grepped its own session transcript for `contextWindow` to establish whether the harness publishes that field, and got 23 hits — which read as the field being present and well-attested. **All 23 were its own prose from that same session**, written while discussing the field. It caught this before reporting, but it was one step from citing itself back as harness evidence. In the same session it had already been corrected for citing its own reasoning as #814 precedent — a holding it had invented and then quoted as established. Same failure, two surfaces: treating your own output as an external source.

**How to apply:** Check what *follows* the match before believing it — the surrounding bytes say whether you're looking at a producer's output or your own sentence about the producer. Prefer searching artifacts you did not author: the shipped binary, the vendor's source, the file on disk. When you must search a corpus you have contributed to — your own transcript, a plan you have been logging to, a channel you have been posting in — filter to records whose author is not you before you count anything. And treat hit **count** as the least trustworthy signal in the result: twenty-three hits of your own prose look far more authoritative than one hit of real evidence, so volume points the wrong way exactly when it feels most convincing.
