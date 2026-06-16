---
name: Never merge without full review flow
description: Kyle requires CodeRabbit review AND all findings addressed before merging any PR
type: feedback
scope: global
---

NEVER merge a PR without the full review flow completing. Every PR must go through:
1. CodeRabbit review
2. All findings addressed
3. Kyle approves or explicitly says to merge

**Why:** Kyle caught me merging PR #11 (Hive Channel) after only review1's review, skipping CodeRabbit entirely. And earlier I merged PR #10 (Plan Tools v2) without waiting for rabbit at all.

**How to apply:** After pushing a PR, wait for BOTH CodeRabbit and any assigned review agent to complete. Fix all findings. Only merge when Kyle says to. Never self-merge just because it "looks ready."

Committing, pushing, deploying, and testing BEFORE merge is fine — that's the normal dev flow. The gate is on the final merge to main, not on deploys/testing.
