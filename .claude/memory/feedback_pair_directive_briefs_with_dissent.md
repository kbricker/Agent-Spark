---
name: Pair a directive brief with an explicit invitation to contradict it
description: Writing a confident technical claim into a subagent brief? Pair it with an explicit invitation to contradict it
type: feedback
scope: global
---

When you brief a subagent, anything you state as technical fact carries your authority. If it is wrong, the subagent implements the bug — it has no standing to argue unless you give it some. So every brief that makes confident assertions must ALSO explicitly invite contradiction, and the invitation has to be real: ask what was wrong, missing, or stale in the briefing, and say that friction is a first-class result rather than a complaint.

**Why:** Plan #975, 2026-08-31. overwatch briefed a hive-dev subagent with "two escaping traps go away — make sure you actually remove them, not port them," having read the code and believed it. Half of it was false: cron's `%`-means-newline trap does not vanish under systemd, it transmutes — `%` opens a specifier in a unit file, and since systemd v247 an unknown specifier is a *load error*. Following the instruction literally would have produced units that silently fail to load, i.e. scheduled jobs that stop running with no error anywhere. The subagent caught it and said so. Its own closing observation is the rule: *"'Two escaping traps go away' is a technical assertion, and taken literally it was a bug. It worked out because the same brief asked for friction back, which left me room to contradict it. Worth keeping that pairing deliberate."* Kyle, same day: **"keep pairing deliberate."**

**How to apply:** State your assertions — vague briefs are worse, and naming the traps is exactly what made this subagent look hard enough to find the bug. But close every directive brief with a standing request for what you got wrong, and treat the answer as part of the deliverable, not as pushback to be managed. The same holds in reverse: when you are the subagent, a confident claim in your briefing is a claim to verify, not a fact to build on. See [[feedback_brief_subagents_with_recall]], [[feedback_verify_before_asserting]], [[feedback_subagents_are_authorized]].
