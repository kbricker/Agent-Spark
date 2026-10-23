---
name: feedback_memory_name_matches_filename
description: "Writing a memory file? Its name: must equal the filename stem exactly — double-bracket links resolve by filename, so a kebab-case slug dangles"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 84adc340-1e66-4417-836e-fb7e06f4aae4
  modified: 2026-10-09T16:25:29.229Z
---

A memory's frontmatter `name:` must be identical to its filename stem, underscores and all. Double-bracket links resolve by filename, so a hyphenated or kebab-case slug, the harness's default, leaves the link dangling and fails overwatch's linkcheck.

**Why:** On 2026-10-09 overwatch's drift check caught a link to the tree-supports memory dangling. Both printing memories had hyphenated names while their files used underscores, and overwatch fixed them in place. The first draft of this rule then dangled four more times on 2026-10-10: it quoted the link syntax literally, and double brackets anywhere in a memory, backticks included, are read as links.

**How to apply:** Pick the filename first, then copy its stem into `name:` and into every link that points at it. Describe link syntax in words, never with the brackets themselves.
