---
name: A zero turn count does not mean an agent key is unused
description: Before treating an agent key as fresh, dormant, or safe to repurpose — read its chat history, because the turn and token counters are per-session and reset, so a key with a real past reports zeros
type: reference
scope: global
---

**`totalTurns: 0` and `totalTokens: 0` on a roster record prove nothing about whether that key has been used.** Those counters are **per-session** — derived from the current session's transcript — so they reset whenever the session is replaced. A key that did months of real work reports zeros the moment it is not running.

**The chat history is the authority.** `hive_read_chat({agentKey})` returns the full record of what a key has done, across every life it has had. Read it before concluding a key is fresh.

## How this bit

Plan 782.2 described `vaexdev2`, `vaexdev3` and `vaexserverdev` as having *"zero turns and zero tokens ever recorded"*, and reasoned from that to "dormant records, safe to repurpose". The counters said so.

`vaexdev2`'s chat history says otherwise: **plan #452, PR #298, four CodeRabbit review rounds, in May 2026**, working from clone `C:\Projects\Unity\VaEx3`. It had a whole working life. Only the counter had reset.

The repurposing decision happened to be right anyway — but it was made on evidence that did not support it.

## Why it matters beyond bookkeeping

**A reused key carries its old channel forward.** vaexdev2's channel still holds detailed, well-formed instructions from vaexdev naming a branch and a clone that belong to a previous life. Nothing in that text marks it expired, and the sender is trusted.

The hazard is not an agent idly scrolling its own history. It is **anything that reconstructs context from the channel** — compaction, a restart handoff, an activity summariser — surfacing those instructions as current. That path reaches "working in another instance's clone" without anyone consciously breaking a rule.

**So when a key is reused, say so explicitly to the agent taking it over**, and state that its own binding beats anything older in the channel. Do not assume it will infer the boundary from dates.

## The check

- Reusing a key? `hive_read_chat` first, and tell the new occupant what it will find there.
- Retiring a key as "never used"? The counter is not evidence. Check the history.
- Seeing zeros on a live agent? That is a fresh session, not an idle agent — see [[reference_how_to_reach_another_agent]] for the related trap of reading status fields that do not mean what they appear to.

---

*Promoted from vaexdev2's local memory, 2026-08-04. Written by the agent that discovered it about itself.*
