---
name: Infra agent hard security rules (SA keys, secrets, commits)
description: Four non-negotiable rules for any cloud infra agent operating with a GCP service account — never read SA key files, never commit or display secrets, all secrets flow through Secret Manager at runtime
type: feedback
scope: global
---

When Kyle has you drive a cloud infra agent (GCP or equivalent), these four rules are **non-negotiable** and must be encoded in the agent's own memory, not derived from conversation context or code. They came from Forge's bootstrap brief on 2026-04-13.

1. **NEVER read or display the SA key file.** Not via `Read`, not via `cat`, not via "just checking it exists". The key is write-only from the moment `gcloud iam service-accounts keys create` emits it. If you need to know whether it exists, use a filesystem check that doesn't read contents (`test -f`, stat, etc.).
2. **NEVER commit credentials, keys, or secret values to git.** Service account keys, API keys, OAuth secrets, Mongo URIs, TLS private keys — all forbidden from the repo. Add patterns to `.gitignore` before the first `git add`.
3. **NEVER output Mongo URIs, API keys, or OAuth secrets in chat.** Not in summaries, not in logs, not in "let me just confirm the connection string". If a tool call returns one, redact before echoing.
4. **All secrets live in Secret Manager** (or equivalent cloud vault) and are pulled at runtime. Never `.env` files. Never hardcoded constants. Never "temporary" file writes.

**Why:** the blast radius of a leaked GCP SA key is catastrophic — compute instance admin + secret access + storage write means full project takeover. Unlike a Verlet code bug, there's no "fix forward" after a credential leak; the key has to be revoked and every secret behind it rotated. The asymmetry is extreme: the cost of being paranoid is almost zero, the cost of a leak is a full incident.

**How to apply:**
- When bootstrapping any new infra agent, write these four rules into its `feedback_security_rules.md` memory before doing anything else — do not rely on a README or a conversation preamble
- If Kyle asks you to read a key file to verify something, refuse and propose a non-read check instead (filesystem existence, `gcloud auth list` for active account, etc.)
- When pulling secrets from Secret Manager for a deploy, stream them directly into the target process's environment — never intermediate them through a file or a shell variable that shows up in `set`/`env` dumps
- If you're about to commit and the diff contains any long alphanumeric string near the word `KEY`, `TOKEN`, `SECRET`, `URI`, `PASSWORD`, or `_SA_`, stop and verify it's not a credential
