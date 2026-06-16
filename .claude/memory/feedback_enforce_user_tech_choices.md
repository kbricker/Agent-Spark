---
name: Enforce user technology choices
description: When user specifies a technology stack, agents MUST follow it exactly — don't let agents substitute frameworks
type: feedback
scope: global
---

When the user specifies "pure TypeScript" or any specific technology choice, that is a hard requirement — not a suggestion. Dev agents must not substitute their own framework preferences (e.g., pulling in React when the user said TypeScript).

**Why:** Verlet editor was spec'd as "TypeScript throughout" but all 5 dev agents independently chose React, resulting in a full rewrite (Plan #111). OverWatch failed to catch this during review — the agents' output looked reasonable but violated the core constraint.

**How to apply:** 
- Include explicit technology constraints in every dev agent brief ("NO React, NO framework dependencies — pure TypeScript + DOM APIs")
- Review agent output for unauthorized dependency additions before checking off items
- When a review agent recommends a library (e.g., "use flexlayout-react"), verify it doesn't violate the user's stack constraints
- Negative constraints ("do NOT use X") are as important as positive ones ("use Y")
