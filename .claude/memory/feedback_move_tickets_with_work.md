---
name: Move tickets when work starts
description: Always update plan status when spawning agents or starting work — don't leave tickets in Planning while agents are in Development
type: feedback
scope: global
---

When spawning a dev agent for a plan, IMMEDIATELY move the plan status through the pipeline (Planning → Review → Ready → Development). Don't wait until the agent finishes. Kyle has called this out multiple times.

**Why:** The dashboard is Kyle's view into what's happening. Tickets stuck in "Planning" while agents are actively coding is confusing and looks broken.

**How to apply:**
- When spawning a dev agent: move plan to Development in the SAME tool call batch
- When agent finishes: move to CodeReview immediately, don't batch with other work
- When merging: move to Completed immediately
- If the pipeline requires intermediate steps (Review, Ready), do them in sequence right away — don't defer
