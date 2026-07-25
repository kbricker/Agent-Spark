---
name: feedback_dependency_messy-test
description: Kyle's bar for approving a new dependency — it must do something messy we don't want to get distracted on; convenience wrappers around clean problems don't pass
metadata:
  type: feedback
---

When Kyle approved `bambulabs_api` for TendWright plan #655 (2026-07-25) he named his criterion: "this is the 'it does something messy that we don't want to get distracted on' test."

**Why:** The dependency absorbed a reverse-engineered MQTT protocol — brittle, undocumented, firmware-version-sensitive. Hand-rolling it would steal time from the actual project. That's the shape of a dependency that earns its place; a wrapper around something clean (an FSM, a small utility) does not — Kyle hand-rolls those ("usually the libraries are nasty").

**How to apply:** When compiling a [[feedback_no_new_dependencies_without_auth]] / no-new-deps proposal, frame the recommendation around this test: what exactly is the messy thing the package absorbs, and would hand-rolling it distract from the project's real goal? If there's no messy core, recommend writing it ourselves.
