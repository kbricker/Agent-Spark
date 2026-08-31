---
name: Logging a change does not correct what the plan asserts
description: A plan's description and checklist are assertions a reader acts on — a shaping-log entry does not update them
type: feedback
scope: global
---

When a fact changes mid-plan, logging it is half the job. The **shaping log is history**; the **description and checklist are assertions**, and the assertions are what the next reader acts on. Correct both, in the same edit.

The failure has a distinctive shape: the plan does not merely go vague, it **actively instructs the wrong thing**. A checklist item that still reads "the first thing here that needs sudo, and there is no NOPASSWD grant on this box" marks an unstarted item as blocked on a grant that now exists. A description section headed "the admin password is still blank", telling the reader not to guess a protocol msgid, warns them off work that was finished two days earlier. Both were true when written; the log recorded the change; nobody went back.

**Why:** spark, 2026-08-31, after four instances in one plan (#951): *"Root cause was the same in all four. The facts changed in the shaping log; the description and checklist kept the old wording. Logging a change isn't correcting what the plan assumes, and the assertions are what a reader acts on."* The same class of defect appeared four separate ways across the fleet that night — a documented server config that had never matched the live host, a committed unit file missing a line production depended on, and two memory files whose stated rules had been false since an earlier plan. In every case something was recorded correctly somewhere while the thing people actually read stayed wrong.

**How to apply:**

- After writing a shaping-log entry that changes a fact, immediately re-read the description and checklist for sentences that entry just falsified. Search for the old claim, not just the new one.
- Pay particular attention to text that **prohibits or gates** — "do not", "needs X first", "blocked on", "there is no". A stale permission is mildly confusing; a stale prohibition stops real work.
- A checklist item's text is an instruction to whoever picks it up. Editing it preserves the item id, so citations survive — there is no reason to leave stale wording in place.
- This is the plan-surface case of a general rule: verify what a reader will act on, not what you remember writing. See [[feedback_record_as_you_shape]] and [[feedback_verify_before_asserting]].
