---
name: feedback_one_ticket_one_branch_pr
description: "One ticket = one branch + one PR. Don't fragment a single plan into per-sub-fix branches/PRs."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 66311e42-0c25-4d00-8ffb-b5da58106411
scope: global
---

A single ticket's work belongs on ONE branch and rolls into ONE PR — even when it spans several sub-fixes (e.g. HUD cleanup + combat + destruction within 37.11). Do not spin a new branch/PR for each small piece.

**Why:** Kyle pushed back twice on 2026-05-30 during 37.11 — first on PR-ceremony for prefab content, then on making "extra branches and PR these small things." Fragmenting one ticket into multiple branches/PRs creates review/merge overhead he doesn't want and obscures that it's all one deliverable.

**How to apply:**
- Open at most one PR per plan/ticket. Keep committing follow-on work to the same branch; the commits accumulate in that PR. Merge once when the whole ticket is done.
- Pure content/prefab/asset work skips the PR entirely — push to the branch, no PR (see [[feedback_content_branches_no_pr]]).
- Don't merge a sub-slice as its own PR and then open another for the next slice of the same ticket.
- Match ceremony to scope: small in-flight fixes within an active ticket are just commits, not new branches. Reserve a fresh branch for a genuinely new ticket.
