---
name: Verify against production before merging
description: Change transforms data or adds an invariant? Verify the RESULT against production BEFORE merging, not after
type: feedback
scope: global
---

Kyle, 2026-08-09, after plan #842 shipped a shaping-log feature across two PRs and roughly seven CodeRabbit review runs: *"it's a ton of cycling for an iteration on the shaping logs it feels inefficient."*

**The rule: if a change transforms data or introduces an invariant, verify the RESULT against production before you merge the change that produced it.** Not after deploy, not after merge. Before.

## Why, from the case that produced it

Plan #842 was merged on a green suite, deployed, and used to backfill 42 pointer edges. Verifying those edges against the live API *afterward* immediately found a defect: every annotation was publishing as a duplicate end of the edge it recorded. Real, worth finding, and it would have shipped.

But finding it in that order cost a second PR, a fresh opening review, and a rate-limit stall that blocked the close-out entirely. Found before the merge, it was one more commit inside a review cycle already in flight.

**The tests could not have caught it, and that is the point.** Every assertion checked the edge was PRESENT — `.Contains(expected)`, `!= null` — and none checked it was ALONE. A duplicate satisfies "present" perfectly. A green suite is evidence about the cases you thought of; production is evidence about the ones you did not.

## How to apply

- **Land the change on a branch, deploy or exercise it against real data, verify the result, and only then merge.** For a Hive change that means a real API call against the live corpus, not a fixture.
- **Assert shape, not just presence.** Count, uniqueness and absence are all separate claims. "The edge exists" and "the edge exists once" fail differently, and only one of them is usually tested.
- **A follow-up fix belongs in the original PR while it is still open.** But do not mistake this for the main lever — merging two PRs into one saves a single review run out of seven. The count of times you push is the whole cost; the ticket boundary is noise.

## What actually burns cycles

Every push is a review. So everything that could change the diff must happen *before* it:

1. **Read the full review body, not the relayed summary.** CodeRabbit hides nitpicks inside `<details>` blocks that the webhook relay strips — a review reported as "3 findings" carried two more. Fixing the three, pushing, then discovering the nits cost an entire cycle.
2. **Run the internal adversarial pass before pushing, not after.** On #842 the pass found a real defect — a branch that returned early and skipped its sibling guard — one commit too late. In the stated order it rides the same push.
3. **Verify against production before merging** (this memory).

All three were already written down. Doing them out of order is what cost the runs, not doing them at all.

Agents composing `role:pr-workflow` hold two related rules: one on batching pushes because every push is a review run, and one requiring review before merge. Named rather than wikilinked on purpose — this file is CORE and applies to every agent, including those that never open a PR, so linking into a role bundle would dangle for them. (It did: linkcheck caught exactly that for spark and 3dproppipeline, which is what the tier rule is for.)
