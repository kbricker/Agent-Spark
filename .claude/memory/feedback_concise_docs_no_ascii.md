---
name: Docs for Kyle are scannable bullet lists — no ASCII diagrams, no walls of prose
description: Deliverable docs are reference material Kyle scans under time pressure — bullets over prose, no ASCII/box-drawing diagrams in markdown because they do not render, and compression is a correctness pass rather than a style one
type: feedback
scope: global
---

Documents written for Kyle are **reference material he scans**, not essays he reads. Kyle 2026-08-10, on a conveyor BOM: *"your bom doc is a confusing wall of text. stop using the ascii framing that does not work in the md files. just make clean bullet lists. learn to be super concise, I dont have all day to parse your walls of gibberish."*

Two hard rules and one bar:

- **No ASCII art or box-drawing diagrams in `.md` files.** They do not render as diagrams in the dashboard, on GitHub, or in most previews, so a layout drawn in `|`, `─` and `└` is strictly worse than the bullet list it replaced. If a picture is genuinely needed, write an SVG alongside and link it.
- **Bullet lists over prose.** Tables are fine where the data is actually tabular (qty / price / spec). Multi-paragraph justification is not — that belongs in the plan's shaping log, which exists to hold WHY.
- **Be ruthlessly short.** Ask what the reader *does* with the doc and cut everything that does not serve that.

## Compression is a correctness pass, not a style pass

This is the part that earns the rule independent of anyone's patience. Cutting the conveyor BOM from 290 lines to 145 **exposed four stale claims the prose had been hiding**: a motor face-mount pattern superseded weeks earlier, fastener hardware specified for that dead pattern, an instruction to measure a bearing fit after bearings had been dropped from the design, and one safety margin quoted as both 5–7× and 3.5× *in the same document*.

Long prose documents rot silently because nobody re-reads them end to end — including their author. Length is where contradictions hide, so shortening is how you find them. Treat a doc that has grown as a doc that needs auditing, not merely trimming.

The reasoning that makes a decision defensible is not the same content as the decision someone needs to act on. Inlining all of it stops the doc being the thing it was written to be: a BOM you order from, a build guide you work from.

Related: [[feedback_record_as_you_shape]] — the shaping log is where the long WHY goes, which is what makes cutting it from the deliverable safe rather than lossy. Also [[feedback_no_unrequested_ux]] and [[feedback_kyle_does_not_edit_tickets]].
