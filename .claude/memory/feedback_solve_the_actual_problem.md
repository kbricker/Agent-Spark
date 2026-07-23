---
name: Solve the actual problem, not the literal ask
description: Implementations must address the root problem — trace all affected paths, not just the obvious one
type: feedback
scope: global
---

Before implementing anything, map the FULL problem space. Don't just address the obvious technical surface.

**Why:** Repeated pattern of partial implementations that miss the intent. Example: watch list was built to filter `AgentUpdate` events but ignored `ChatMessage` events — the actual source of the cross-talk noise problem Kyle wanted solved. The fix addressed "filter by agent key" without asking "what are ALL the event types flowing through this bridge?"

**How to apply:**
1. When given a problem + solution direction, restate the underlying problem FIRST
2. Trace ALL paths affected — not just the one that's most obvious
3. Before sending work to a dev agent, enumerate every case the solution must handle
4. If a feature touches an event/message pipeline, list every event type and confirm which ones are in/out of scope
5. Ask "does this fully solve the problem Kyle described?" before shipping
6. When the ask has more than one reasonable interpretation, surface them — don't silently pick one and build it. State the interpretation you're running with and the assumption behind it out loud (in plan-review chat or the plan description), so a wrong guess is caught before code, not after. If something is genuinely unclear, stop and ask rather than guessing.
7. **Mechanical touched-surface audit (added from #624 mining, Kyle 2026-07-22):** "trace all paths" is not an intention — it's an artifact. When a plan generalizes or modifies an existing surface (function, field, config value, message type), the plan LISTS the enumerated consumers and siblings: grep the call sites, name the parallel/mirrored implementations (client vs server, CLI vs engine, the sibling code path), and mark each in-scope or explicitly out. ~150 review catches were fix-one-site-miss-the-sibling, diverging parallel bookkeeping, or refactors dropping wiring — all preventable by an enumerated list instead of a mental note.
