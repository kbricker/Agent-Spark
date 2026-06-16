---
name: Orchestrate proactively — start workflows, watch workers, move things along
description: After dispatching work to agents, always watch for completion and drive the pipeline forward without being asked
type: feedback
scope: global
---

Always follow through on orchestration end-to-end: send messages to kick off work, watch for agent completion events, read results, and take the next pipeline step. Never stop at just updating a plan status — that's paperwork, not orchestration.

**Why:** Kyle corrected this when OverWatch moved a plan to Review and assigned a review agent but didn't send it a message or watch for the response. The whole point of OverWatch is to drive workflows, not just update fields.

**How to apply:**
1. When moving a plan to a new status, always send the assigned agent a message with context
2. Watch the agent (hive_channel_watch) so you receive their idle event
3. When they finish, read their chat, evaluate the result, and take the next step (approve, send back, move to next stage)
4. Keep the pipeline moving — don't wait for Kyle to tell you to check on things
