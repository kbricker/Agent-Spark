---
name: Never design for per-token API billing while subscriptions exist
description: Kyle's Max subscription is dramatically cheaper than metered API tokens — never propose an architecture that moves fleet work onto per-token billing, and rule those options out early rather than costing them
type: feedback
scope: global
---

**Do not propose, design toward, or spend research time on any architecture that moves our agent work onto per-token Claude API billing.** The Max subscription covers Claude Code sessions at a flat cost that is not close to metered token pricing at our volume.

Kyle, 2026-08-03: *"max sub is insanly cheap compared to tokens, im never going to tokens until they take away subs and I have a suger daddy."*

**Why:** we run four interactive orchestrators plus every ephemeral, at Opus tier, effectively continuously. Under the subscription that is a fixed monthly cost. Metered at API rates it is an open-ended bill scaling with how much work the fleet does — which is exactly the thing we want to increase. The economics do not merely disfavour the API path; they invert the incentive to use the platform at all.

**How to apply:**

- When evaluating a platform capability, **establish the billing model first** and drop the option immediately if it is per-token. Do not cost it out, benchmark it, or write a migration plan for it — that research is wasted before it starts.
- This rules out **Managed Agents** (Anthropic-hosted agent loop + sandbox, API-billed) and the **Claude Agent SDK** for fleet work, regardless of their technical merits. Both were assessed on 2026-08-03 against the channels dependency; both were rejected on billing alone, not capability. See plan #754.
- It does **not** rule out anything that keeps running under Claude Code — the supported `--channels` path, plugins, marketplaces, managed settings, hooks and MCP servers all stay on the subscription. Plan #773's migration is fine for exactly this reason.
- The trigger that would reopen this is Anthropic removing subscription access, not a capability we want appearing on the API side. Until then, "it's on the API" is a sufficient reason to stop evaluating.
- Small one-off API calls for a specific job are a different question from moving fleet workloads; if one ever seems warranted, ask rather than assuming this rule blocks it.

**Consequence worth stating plainly:** it means some platform risks are accepted rather than mitigated, because the only mitigation available is an API-billed rearchitecture. The right response is to make the acceptance explicit and make the failure fast to diagnose — see [[recall:reference_channels_platform_dependency]], where `tengu_harbor` is exactly that case.

Related: [[feedback_no_new_dependencies_without_auth]], [[feedback_research_before_asking]].
