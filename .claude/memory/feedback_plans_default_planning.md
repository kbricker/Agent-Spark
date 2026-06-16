---
name: Plans default to Planning, not Backlog
description: Never file new Hive plans in Backlog by default — Planning is the default status; Backlog is Kyle's manual "get this out of my face" bucket
type: feedback
scope: global
---

When filing a new Hive plan (including parking-lot platform-improvement tickets that won't be worked on immediately), the default status is **Planning**, not Backlog.

**Why:** Kyle uses Backlog as a deliberate manual gesture — he moves plans there himself when he wants them out of the active view. Defaulting to Backlog is "hiding my own work from him," which defeats the purpose of filing the ticket in the first place. Learned on 2026-04-14 when I filed plans #183 (auto-watch on hive_send_message) and #184 (orphan auto-memory cleanup) in Backlog because Kyle had said "let's batch these as platform improvements later" — I interpreted that as "hide them from active view," but Kyle's reaction was "183 is what? you should never really file in backlog, I move stuff there manually from time to time to get it out of my face."

**How to apply:**
- New plans → always `Planning` status, even parking-lot tickets. They stay visible in Kyle's active view until he decides to hide them.
- If Kyle says "file this for later" or "batch it" or "not now," that's still Planning. The batching is a decision he'll make later; my job is to make the plan visible so it can be batched.
- Backlog is reserved for Kyle's own hand movement. I never file there and I don't move plans there without an explicit instruction that uses the word "backlog."
- Cancelled is still fine for genuinely abandoned/rerouted plans (like #182 when we moved the component-leaf rule out of the global template).
