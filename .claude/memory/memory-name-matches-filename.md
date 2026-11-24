---
name: memory-name-matches-filename
description: "Writing a memory file? Its name: must equal the filename stem exactly — double-bracket links resolve by filename, a kebab-case slug dangles"
source: spark/memory-name-matches-filename@22
metadata:
  type: feedback
---

A memory's frontmatter `name:` must be identical to its filename stem, underscores and all. Double-bracket links resolve by filename, so a hyphenated or kebab-case slug, the harness's default, leaves the link dangling, and nothing checks for it.

**Why:** On 2026-10-09 overwatch's drift check caught a link to the tree-supports memory dangling. Both printing memories had hyphenated names while their files used underscores, and overwatch fixed them in place. The first draft of this rule then dangled four more times on 2026-10-10: it quoted the link syntax literally, and double brackets anywhere in a memory, backticks included, are read as links.

**How to apply:** Pick the filename first, then copy its stem into `name:` and into every link that points at it. Describe link syntax in words, never with the brackets themselves.
