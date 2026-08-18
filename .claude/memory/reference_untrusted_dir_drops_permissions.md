---
name: An untrusted project dir silently voids every allow rule
description: Allow rules inert? Read hasTrustDialogAccepted in ~/.claude.json first — untrusted dirs void .claude/settings.json
type: reference
scope: global
---

**A project directory that has never been trusted does not get its `.claude/settings.json` permissions applied at all.** Interactively you clear a "do you trust the files in this folder?" dialog; headless (`-p`) has no dialog to clear, so it fails **closed and silently**. Every project allow rule is inert — not mismatched, not overridden, simply never loaded.

## Why it costs hours instead of minutes

The denial names the tool:

```
Claude requested permissions to use mcp__hive__hive_plan_get, but you haven't granted it yet.
```

That reads as *"your rule for this tool is malformed"*. The truth is *"none of your rules loaded"*. Everything else looks healthy on the way past: the MCP server starts, tool schemas resolve, `/mcp` reports fine — because `/mcp` reads a different allowlist than the one gating delivery. So the evidence you naturally reach for all points away from the cause.

## The check, before anything else

One read of `~/.claude.json` — is there a `projects` entry for the workspace path, and does it have `hasTrustDialogAccepted: true`? Absent key or `false` is your answer, and it costs one grep against the most misleading symptom in the harness.

Two things that make it easy to misdiagnose even after checking:

- **The value is read at process start.** Correcting it changes nothing for a session already running — a fresh process is required. "I fixed it and it still fails" is expected, not a second bug.
- **A brand-new workspace is untrusted by definition**, so every newly provisioned agent hits this on its first run.

## Check and report — do not fix it yourself

Flipping the flag is a **provisioning act**, not a debugging step: it declares a directory trusted, and `~/.claude.json` is written by every live Claude session, so a careless whole-file rewrite clobbers concurrent updates. When you hit this, **report it** — name the workspace path and the flag state. Provisioning belongs to whoever stood the agent up; overwatch's `create-new-persistent-agent` skill carries the procedure and the file-safety rules for it.

## Evidence

Diagnosed 2026-08-10 standing up `hivedev01`, at a cost of three wrong-but-reasonable diagnoses, each killed by evidence before the trust flag was checked: (1) `.mcp.json` misconfigured — it was byte-identical to a working agent's; (2) allow-rule syntax wrong — `mcp__server__*` is confirmed supported by the docs; (3) the roster's `allowedTools` was missing `mcp__hive__*` — **genuinely missing, genuinely fixed, and it changed nothing**, because it was never the gate.

Number (3) is the shape worth remembering: a real defect, correctly fixed, with zero improvement. It feels like progress and it keeps a wrong diagnosis alive. When a fix that should have worked produces no change, suspect that you are treating a second-order problem.

## Related

The complement to this one is [[recall:reference_bash_permission_matching]] — rules that *are* loaded but fail to match. Same visible symptom, opposite cause, and the two are worth distinguishing before either is investigated: this memory is "no rules loaded", that one is "rules loaded, this call doesn't match". Reaching for the wrong one costs the hours described above.

See also [[feedback_check_what_overrides_the_file]] (the file you are editing is often not the authority), [[feedback_check_docs_on_harness_friction]] (read the current permission docs before theorising — semantics move between versions), and [[feedback_verify_your_own_harness_state]] (verify what your session can actually do rather than accepting an account of it).
