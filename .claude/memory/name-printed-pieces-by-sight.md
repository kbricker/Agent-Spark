---
name: name-printed-pieces-by-sight
description: "Writing Kyle a bench or fit-check doc for printed parts? Name each piece by what he sees (tall plate, small block), never by CAD role or file name"
source: spark/name-printed-pieces-by-sight@21
metadata:
  type: feedback
---

When a doc tells Kyle what to do with printed pieces, name each piece by what he can see in his hand: its size, its shape, a feature he can point at. Give the file it came from once, in the piece list. CAD role names ("motor end", "infeed end", "boss", "ear pocket", "inner wall") are jargon at the bench.

**Why:** 2026-09-30, the conveyor coupon fit check: *"some of these tests are hard to understand exactly. the coupons were 2 files that produced 3 parts."* He had to translate "the block's groove onto the infeed end's rail" into "the smallest piece sliding on the rail in the middle of the medium size piece". One file printing two pieces made file-based names worse.

**How to apply:** open the doc with a piece list by size and shape (tall plate, medium plate, small block, wedge). Say which file made which piece, and call out a file that prints two. Then use only those names in every step, and locate features by sight ("the rail across the middle", "either side of the big round hole"). Related: [[bench-task-lists-are-dated]], [[printing-tree-supports]].
