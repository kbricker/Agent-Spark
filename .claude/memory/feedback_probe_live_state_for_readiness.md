---
name: feedback_probe_live_state_for_readiness
description: "Answer \"are you ready / is X up\" questions from a live probe, not from memory or docs — state drifts, and a confident stale answer is worse than a probe that takes ten seconds."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 11c17a47-4933-4687-abab-e2d1fdc5c628
  modified: 2026-08-08T17:15:38.347Z
---

When Kyle asks whether something is ready, up, or possible ("if I ask you to boot the cell, are you ready?"), run the cheap read-only probe before answering — ping the host, list the outlets, hit the status endpoint. On 2026-08-06 the ready-check answer was only trustworthy because a live probe showed cell1 down and every relevant outlet off; memory and docs alone would have produced a plausible answer about a lab in an unknown state.

**Why:** documented state and remembered state both drift silently; hardware especially. A readiness answer grounded in a probe is evidence, one grounded in recall is a guess wearing evidence's clothes.

**How to apply:** before asserting readiness or current state to Kyle, spend the ten seconds on the read-only check that would falsify the answer. Reads are always authorized ([[reference_lab_control_authority]]), so there is no permission cost — only the discipline.
