---
name: GCP infra agent bootstrap recipe (from Forge)
description: Forge's recipe for setting up a new GCP project with a claude-infra service account, SA-scoped IAM roles, OS Login SSH, Secret Manager, and local gcloud activation — use when Kyle asks to bootstrap a new cloud infra agent
type: reference
scope: global
---

Canonical bootstrap recipe from Forge (2026-04-13) for spinning up a GCP project that a Claude infra agent can drive. Use this as the starting template when Kyle asks to set up cloud-based infra agents or extend existing ones onto GCP.

## Phase 1 — GCP project setup

1. Create project, link billing, note project ID.
2. Enable required APIs in one call:
   ```bash
   gcloud services enable \
     compute.googleapis.com iam.googleapis.com iamcredentials.googleapis.com \
     secretmanager.googleapis.com iap.googleapis.com storage.googleapis.com \
     logging.googleapis.com cloudresourcemanager.googleapis.com
   ```
3. Create the agent service account:
   ```bash
   gcloud iam service-accounts create claude-infra \
     --display-name="Claude Infra Agent"
   ```
4. Grant **minimum** roles (project-scoped unless otherwise noted):
   - `roles/compute.instanceAdmin.v1` — VM lifecycle + SSH metadata
   - `roles/iap.tunnelResourceAccessor` — SSH over IAP so VMs don't need public IPs
   - `roles/compute.osLogin` — SSH as the SA via OS Login
   - `roles/secretmanager.secretAccessor` — pull deploy-time secrets
   - `roles/storage.objectAdmin` — **scope to backup bucket(s) only**, NOT project-wide
   - `roles/logging.viewer` — read VM logs
   - `roles/serviceusage.serviceUsageConsumer` — required for many API calls
5. Enable project-level OS Login:
   ```bash
   gcloud compute project-info add-metadata --metadata enable-oslogin=TRUE
   ```
6. Generate and download the SA JSON key:
   ```bash
   gcloud iam service-accounts keys create claude-sa-key.json \
     --iam-account=claude-infra@<project>.iam.gserviceaccount.com
   ```
   Store OUTSIDE git. Add to `.gitignore`. Treat as a secret — never read or display contents.

## Phase 2 — Local agent workstation

7. Install gcloud CLI. Activate the SA:
   ```bash
   gcloud auth activate-service-account --key-file=<path>/claude-sa-key.json
   gcloud config set project <project-id>
   ```
8. Create the agent workspace folder. Inside it, mirror the verletDev / overwatch structure:
   - `CLAUDE.md` — role, collaborators, hard security rules, list of skills
   - `.claude/memory/MEMORY.md` — memory index
   - `.claude/memory/reference_gcp_project.md` — project ID, SA email, gcloud path, activation command
   - `.claude/memory/reference_vm_inventory.md` — VMs, IPs, zones, service names, deploy scripts
   - `.claude/memory/reference_ssh_and_dns.md` — DNS records, SSH conventions, third-party allowlists (e.g. Mongo Atlas)
   - `.claude/memory/feedback_security_rules.md` — links to the hard security rules below
   - `.claude/skills/` — runbooks for deploy, backup/restore, ssh ops

## Phase 3 — Hard security rules (MUST be in the new agent's memory, not derived from code)

- **NEVER read or display the SA key file** — not even to confirm it exists via Read
- **NEVER commit credentials, keys, or secret values to git**
- **NEVER output Mongo URIs, API keys, OAuth secrets in chat** (even to Kyle)
- **All secrets live in Secret Manager** and are pulled at runtime — not stored in `.env`

## Phase 4 — Recommended extras

- Dedicated GCS bucket for backups with a lifecycle rule (e.g. delete after 30 days)
- Secret Manager entries for every deploy-time config value
- A separate low-privilege read-only SA for ad-hoc inspection if multiple agents share the project
- Audit logging enabled on the SA so every action is traceable

## What Forge needs to auto-bootstrap

To generate a one-shot bootstrap script, Forge needs: **project ID**, **billing account**, **intended VM list** (name/zone/purpose), and **bucket names**. Forge will produce a script that creates the SA, grants the roles, enables APIs, and emits the key.

## How to apply

- Use this as the playbook when Kyle says "set up a new infra agent", "bootstrap a GCP agent", or similar
- Don't improvise role grants — use the minimum set above unless Kyle explicitly asks for more
- The service account key file is the most sensitive artifact in this whole flow; treat it as write-only and never read-back
- When filling in `reference_gcp_project.md` for a new agent, the SA email pattern is always `claude-infra@<project>.iam.gserviceaccount.com`
