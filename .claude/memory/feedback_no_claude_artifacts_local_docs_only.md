---
name: No claude.ai Artifacts — deliverable docs land on local disk
description: Publishing a doc, report, chart, or dashboard as a claude.ai Artifact? Never — deliverables land on disk in the project
type: feedback
scope: global
---

Never host deliverables (reports, charts, dashboards, docs) as claude.ai Artifacts. ALL documents land in the project folder on local disk. Per Kyle 2026-07-22.

**Why:** Kyle wants his documents on his own disk, in the project tree — not on claude.ai hosting.

**How to apply:** Write reports/charts as standalone HTML/MD files under `C:\Projects\overwatch\reports\` (subfolder per plan, e.g. `reports/624-review-catch-mining/` with a `data/` subdir for raw datasets). Include `<!doctype html>` + `<meta charset="utf-8">` so they open cleanly from `file://`. Reference local paths in Hive plans/reports, never artifact URLs. Do not use the Artifact tool for deliverables at all.
