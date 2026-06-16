---
name: Don't invent UX surfaces Kyle didn't ask for
description: When drafting plan descriptions / fleshing out checklists, stick to the behaviors Kyle actually named. Don't extrapolate a UX affordance and ship it as if it were authorized.
type: feedback
scope: global
---

When the plan-writing phase produces an "obvious" UX affordance that Kyle didn't actually ask for — call it out explicitly and get approval before shipping it. Don't treat "I wrote it in the plan description I just drafted" as authorization.

**Why:** During plan #177 reframe (2026-04-19), Kyle's stated ask was: "bind gameobjects mesh renders to a submesh, asset browser exposes contents and makes them assignable." He approved the Unity-mimic direction in chat. I drafted the plan description with a "Primitives pseudo-folder" in the AssetBrowser (D6) and shipped it. On smoke test Kyle said "I dont want or need a primitives folder, didnt ask for that." Fair — he never named that surface. I extrapolated.

**How to apply:** Before adding a user-facing affordance to a plan checklist, ask: did Kyle explicitly name this, or did I infer it? If inferred, either drop it or flag it in the plan-review chat with "do you want X?" Example: for #177 I should have asked "drag-drop geometry slot — do you want a Primitives folder for discoverability, or is the dropdown alone enough?" instead of folding it in silently.

This applies even when the parent spec "reasonably implies" the affordance. Kyle's plan-review approvals are on the behaviors he named, not the secondary surfaces an AI would naturally derive.
