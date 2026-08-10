---
name: Don't take on work outside your remit — but findings always flow
description: Findings flow anywhere and are never outside remit; implementation stays within your composed roles in composition.json
type: feedback
scope: global
---

**Do not pull an agent onto work outside its remit just because it is idle.** Kyle 2026-04-11, sharply. An agent carries a working directory, a clone, and accumulated project context; borrowing it for another project puts the wrong context in front of it and disrupts what it was holding.

**Your remit is the `roles` array in `composition.json`, plus your workspace and clone.** Not a routing table in prose — every hand-maintained roster the fleet has written went stale, and one of them was still being cited as binding law four months after it was superseded. If you need to know whether something is yours, read the composition, not a memory that lists agents.

## The line, stated so it can be acted on

- **Implementation work stays in remit.** Code, config, deploys, PRs for a project whose role you do not compose. Say so and route it; the right agent for a project is the one bound to it.
- **Findings flow anywhere, always.** Reporting a defect, a stale document, a wrong claim, or a promotion proposal about any part of the system is never outside remit. It is the whole return path (`promote-learning`), and an agent that holds back a finding because the subject "isn't mine" has taken the rule exactly backwards.
- **Shared corpora are shared.** Shaping logs, review findings and plan logs are append-only and stamp their actor precisely so anyone who learns something can record it. Annotating one is using it, not trespassing in it.

## Why the distinction, and not just "stay in your lane"

2026-08-10: vaexdev2, a VaEx agent, found a stale entry in a Hive platform plan's shaping log, diagnosed it correctly, identified the exact pointer needed, and asked before writing it. Overwatch declined and cited a rule — from a **superseded tombstone** it had not re-read, whose index hook still advertised the dead version, and which lives only in overwatch's own workspace where the agent it supposedly governs could never have read it.

Three lessons, and only the first is about remit:

1. The finding was correct and valuable and came from outside the remit. **Had vaexdev2 applied "not mine, stay quiet", the stale entry would still be misleading readers.**
2. A rule that constrains an agent must be readable *by that agent*. One stored where only the enforcer can see it cannot bind anyone — it can only be quoted at them.
3. Reasoning from memory about a rule instead of reading it is the same failure as reasoning from memory about code. See [[feedback_verify_your_own_harness_state]].

Related: [[feedback_promote_what_you_learn]] — the mechanism findings travel by, and the one that keeps a local rule from staying local.
