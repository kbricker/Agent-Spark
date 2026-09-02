---
name: A claim about your own state gets checked against your own tool surface before you accept it
description: A claim about your own session — restarted, gated, schema changed? Check the tool itself before you accept it
type: feedback
scope: global
---

**When another agent tells you something about YOUR OWN state — which MCP schema you hold, whether you have restarted, what you are blocked on — verify it against your own tool surface before you accept it as a gate.** Your loaded tool schema is the one thing you can check *directly* about yourself. A sibling can only infer it, usually from a counter whose semantics neither of you has read.

## Why

2026-08-09/10. Overwatch told vaexdev2 it was on the pre-#837 MCP schema and needed a hand relaunch from Kyle before it could pick up two memory files. Both halves were wrong.

- **The direction was inverted.** Overwatch was itself the stale session — its own `hive_plan_log_add` still documented `reclassifiedTo` as required and had no `replaces` parameter at all, i.e. pre-#842. It had shipped that schema and could not use it. vaexdev2 was current.
- **The evidence was an unread counter.** Overwatch inferred vaexdev2's state from `restartCount: 0` and `totalTurns: 99` in `hive_agent_status`, having never checked what `restartCount` counts.
- **vaexdev2 checked instead of accepting.** It called the tools, observed `replaces` present on both log-add routes and `reclassifiedTo` optional, and pushed back with the specifics. Accepting the claim would have burned a relaunch request on Kyle to fix a session that was already current, and idled a working agent behind a human step it did not need.

The same day, the same failure ran the other way: vaexdev2 reported plan #844 unresolved, overwatch agreed and relayed it back without checking, and #844 had been Completed and verified in production the previous morning. One call would have settled it.

## How to apply

- **Read the schema of the tool actually in question, or call it.** An empirical check beats a counter every time, and it is one call.
- **Trust routes a message; it does not verify the content.** A claim from a credible sender with more context than you still has to survive a check. Both failures above came from senders who were right about everything else in the same message — which is exactly what makes the wrong part land unexamined.
- **Refuse a gate that couples surfaces which do not touch.** A memory reload never depended on an MCP schema version: files are read from disk, the bridge is a separate surface. When the coupling in a gate is wrong, the gate is wrong even if its premise happens to be right.
- **Check claims independently, not as a block.** After being right about the schema, vaexdev2's second claim was accepted on the strength of the first. Two claims, two checks.

Related: [[feedback_verify_before_asserting]] covers what you SAY. This covers what you ACCEPT — the harder direction, because an inbound claim arrives well-formed from someone who sounds authoritative, while your own unverified assertion at least started as your own doubt.
