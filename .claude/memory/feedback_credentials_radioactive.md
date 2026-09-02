---
name: Credentials are radioactive — only forge handles them
description: Task would have you read, paste, or handle a key or token? Stop — credentials are radioactive, route it to forge
type: feedback
scope: global
---

**Access credentials are radioactive, and only forge has the gloves.** For every project we run, credential-level work — SA keys, API keys, OAuth secrets, database URIs, tokens, TLS private keys — is forge's exclusively. Kyle 2026-08-14: *"only forge should ever mess with credential level anything for all project we do... access credentials are radioactive and only forge has the gloves to handle."*

**If you are not forge:**
- Never read or display a credential file — not `Read`, not `cat`, not "just checking it exists."
- Never commit, write, hardcode, or echo a secret (chat, log, and summary all count).
- If a task needs credential-level work — creating or rotating a key, wiring a secret, reading a connection string — STOP and route it to forge. Not yourself, not once, not "temporarily."

forge holds the detailed operating rules in its own memory; this is the fleet guardrail that keeps everyone else's hands off. The asymmetry is the point: routing to forge costs a message; a leaked credential is a full incident with no fix-forward — the key is revoked and every secret behind it rotated.

Related: [[recall:reference_forge_agent]] (how to reach and wake forge).
