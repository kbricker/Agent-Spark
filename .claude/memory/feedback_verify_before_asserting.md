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

## A claim you put into a briefing is not evidence when it comes back

An agent you tasked will repeat your premises in its own report, its tickets and its commit messages — not because it checked them, but because you stated them. **Your assertion reflected off a subagent looks exactly like independent corroboration**, and the reflection is invisible from both ends: you see your claim confirmed, and it sees a given.

This is not the same as "another agent agreeing." There, two agents each contribute an unchecked claim. Here the downstream agent contributes *nothing* — it is relaying, and it has no way to know your premise was unverified, because a briefing is necessarily written in the declarative. That is the trap's engine: you cannot hedge every premise in a briefing without making it unusable, so **the act of briefing strips the uncertainty markers off your own claims at exactly the moment they start propagating.** The fix therefore cannot live in how you brief. It has to live at the point where you cite the answer back.

**Why:** 2026-08-10, VaEx 0.8.67 promotion. vaexdev read "`VaEx3`/`VaEx4` are unbound, from a roster that never ran a turn" and collapsed *unbound roster* into *dead clone* — one word doing work it was not entitled to. It then briefed forge with that as fact: *"VaEx4 is a dead clone… nothing works in it, nothing pulls it."* Forge had independently measured the clone at 434 commits behind — true, and consistent with both "dead" and "fine, just stale." It filed plan #865 with *"the VaEx4 clone is dead"* in the description. The claim now sat on three surfaces — the ticket, forge's report, vaexdev's own messages — all sourced from one unchecked inference, with a real measurement beside it lending credibility it had not earned. Kyle corrected it in five words: *"its a valid clone we can use tho, just needs a pull."*

It produced a wrong **action**, not just wrong prose: believing VaEx4 unusable, vaexdev overrode the `-ProjectDir` default and ran the promotion against Kyle's live working clone, pushing a version-bump commit into a checkout he had open minutes earlier. The default pointed at VaEx4 precisely so the bump lands where nobody is editing.

**How to apply:** Before citing something a downstream agent told you, **ask whether you are the one who told them.** Trace the claim to its origin, not to its most recent appearance. Watch for two amplifiers specifically: a true measurement sitting next to an untrue inference will launder it, because checking the number feels like checking the claim; and once a premise reaches a ticket it reads as documented fact, outliving the conversation that produced it and arriving at the next reader with no author attached. When you brief an agent on something load-bearing that you have not personally verified, say so in the briefing — one clause — so the relay carries the uncertainty instead of laundering it.

### A handoff you wrote yourself is a briefing too

A restart handoff, a plan description, a summary left for your future self — all written in the same declarative voice, all consumed later as fact by a reader who cannot see which parts were checked. Here the author and the relay are the same agent, so there is no second party to catch it.

**Why:** 2026-08-10, overwatch resuming from a restart handoff. The protocol it follows already mandates re-polling every watched agent's live state after a restart, and it did that — which caught one stale claim at once (the handoff said hivedev01 was working; it was idle). It then took the handoff's *prose* at face value: "forge flagged the coupling for Kyle and it is unresolved" became "forge correctly refused to push," asserted back to forge as a statement about forge's own conduct. forge had refused nothing — it simply had not reached the push yet — and it checked rather than accepting the flattering account. **The machine-readable state got verified and the narrative did not.**

**How to apply:** Treat a handoff's structured claims and its prose as two different reliability classes. Poll the state; that part is usually already in the protocol. Then re-read the narrative specifically for claims about **what someone did, decided, or refused**, and hold those as unverified until that party confirms. Never upgrade a hedge in transit — "flagged it, unresolved" is not "refused to," and the gap between them is where the fabrication enters. Be most suspicious when the claim flatters someone or confirms what you already believe, because that is when you will not look. Simplest form of the rule: **if you are about to tell an agent what it did, ask it instead.**
