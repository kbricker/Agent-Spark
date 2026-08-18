---
name: Brief subagents to recall their domain pack
description: Brief a subagent to hive_recall its domain pack before it builds — prefab YAML, shaders and VaEx internals
type: feedback
scope: global
---

**When you spawn a subagent for domain-specific work, the brief must tell it to `hive_recall` that domain first.** Name the topic in the brief — "recall the prefab YAML conventions before you author anything", "recall the Synty vegetation shader teardown" — rather than assuming it will occur to the subagent mid-task.

**Why:** the knowledge is no longer always-loaded. Plan 782.21 moved the prefab-YAML, shader and VaEx-internals packs into the retrieved tier, which is the whole reason a task-specific subagent is viable at all — it composes no role and pays nothing when idle, and Kyle's framing was exactly that: *"task specific dev sub agents, if they can use the RAG to load the block of memories specific to the thing they will be building like a prefab (yaml) or a shader (HLSL) thats perfect."*

But retrieval only fires when someone searches, and **an agent does not search for knowledge it does not know exists.** That is the same trigger problem 782.7 is about, and it is what turns a migration into a deletion. The subagent will not feel the gap: it will confidently hand-write a prefab with 19-digit fileIDs, or a shader that ignores the vertex-colour channel convention, and report success.

**How to apply:**

- Naming the topic beats naming the tool. "Search the corpus" is ignorable; "recall the prefab YAML conventions, then author the file" is an instruction.
- The pack is reachable **without composing anything** — retrieval is fleet-wide and is not filtered by the caller's composition (verified in `RecallStore.Query`, which takes no agent or scope parameter). A subagent needs no role to reach it, which is the property the whole design rests on. If anyone ever adds scope filtering there, this breaks silently.
- An **empty** result is a real answer meaning the corpus has nothing, not a failure. Read `nearestMiss` to tell a near-miss from a blank before rephrasing, and rephrase at most once. A hit is a candidate, not an answer — read it and confirm it answers what was asked; `unknownTerms` lists identifier-like names in the query (CamelCase, short acronyms, capitalised names — not ordinary words) that the corpus has never mentioned, and no hit can be about those.
- Behavioural rules are NOT in retrieval and never will be — they stay always-loaded precisely because you cannot search for a rule you have not met. If a subagent needs a guardrail, put it in the brief.

Related: [[feedback_subagents_are_authorized]] (spawning them is expected, not optional).
