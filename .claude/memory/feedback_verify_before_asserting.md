---
name: Verify before asserting
description: Verify claims against actual state before asserting — never assume; agreement or your own past words aren't verification
type: feedback
scope: global
---

Don't assert something is true without verifying it first — most of all before a destructive or irreversible action. Run the cheap read-only check that would falsify the claim before it becomes a decision: `git log -- <file>`, `git show <commit>`, open the file, or — for live state that drifts while nobody's touching it — ping the host, list it, hit its status endpoint. Readiness answers especially ("is X up?", "are you ready?"): a probe is evidence, recall is a guess wearing evidence's clothes. Don't eyeball a diff and assume.

*Cost of the base case:* told Kyle a scene change was in a squash merge without checking; then suggested `git checkout --` to "clean" a diff, which wiped uncommitted Unity work.

Four traps make an unverified claim *feel* verified:

**1. A second agent agreeing is not verification.** If neither of you opened the file, two agents are two guesses — and the agreement gives the claim social weight it never earned, making it harder to dislodge.
*754.1:* 3dproppipeline and overwatch both "confirmed" from memory that prepare-restart has no watch list. It's a `scope: global` skill mandating exactly that. Both were one tool call from the truth — and had just checked each other correctly on something else, so the next unchecked claim inherited the credibility. → Before proposing to *build* something that fills a gap, read the thing said to have the gap; drafting the requirement is what exposes a hole already closed.

**2. Your own earlier words are not verification.** Self-authored text is indistinguishable from evidence at the search layer — a grep hit reads the same whether the bytes are a vendor's or your own sentence two turns ago.
*852.4:* hivedev01 grepped its transcript for `contextWindow`, got 23 hits, read it as the field being well-attested. All 23 were its own prose. → Check what *follows* the match; prefer artifacts you didn't author; when searching a corpus you've written to, filter to records you didn't author. Hit *count* is the least trustworthy signal — volume points the wrong way exactly when it feels convincing.

**3. Your own claim reflected off a subagent is not corroboration.** A downstream agent repeats your premises because you stated them, not because it checked them. A briefing is necessarily declarative, so briefing strips the uncertainty markers off your claims exactly as they start propagating — the fix lives where you cite the answer back, not in how you brief.
*VaEx4:* vaexdev collapsed "unbound roster" into "dead clone," briefed forge as fact; forge filed #865 with "the VaEx4 clone is dead." A true measurement (434 commits behind) sat beside the false inference and laundered it. It produced a wrong *action* — running the promotion against Kyle's live working clone. → Trace a claim to its origin, not its most recent appearance. When you brief an agent on something load-bearing you haven't verified, say so in one clause so the relay carries the uncertainty. A true number next to an untrue inference launders it; a premise on a ticket reads as documented fact.

**4. A handoff you wrote yourself is a briefing too** — a restart handoff, plan description, or summary for future-you, read later as fact by someone who can't see which parts were checked.
*Restart resume:* overwatch polled live state (caught hivedev01 idle, not working — good), then took the prose "forge refused to push" at face value. forge had refused nothing. → Poll structured state, but hold any claim about **what someone did, decided, or refused** as unverified until they confirm. Never upgrade a hedge in transit ("flagged it, unresolved" ≠ "refused to"). Simplest form: **if you're about to tell an agent what it did, ask it instead.**

Be most suspicious when a claim arrives **flattering or confirming what you already believe** — that's when you won't look. Detectability is a property of the topic, not the receiver's diligence: when the subject is something the far end can't see, the whole load is on you.

Related: [[feedback_verify_your_own_harness_state]] (what you ACCEPT about yourself), [[feedback_prove_the_check_ran]] (a check that ran but never applied), [[feedback_read_the_assembled_artifact]] (false-by-adjacency).
