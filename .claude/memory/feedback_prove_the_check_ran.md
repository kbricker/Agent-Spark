---
name: A check that silently did not run looks exactly like a check that passed
description: A check came back green? Prove it actually ran — a verification that never applied looks identical to correct code
type: feedback
scope: global
---

**The most dangerous test result is a pass produced by a test that never executed against the thing it names.** Same output, same exit code, same green. Nothing in the result distinguishes *the code is correct* from *the check silently did not apply*, so the verification you added to catch a defect becomes the reason you stop looking for it.

This is not the same as [[feedback_verify_before_asserting]]. There the failure is not checking. Here you **did** check, carefully, and the check evaporated in transit.

**Why:** 2026-08-11, epic #852 and PR #128 — **five instances in one night**, five different mechanisms, one shape:

- A `python` heredoc wrote a fixture to a path that did not exist because the Bash tool's cwd had drifted from an earlier `cd`. The suite then ran green **against unmodified code**. Caught by a `grep -c` guard on the injection, not by the suite.
- A repo-wide scan returned "no sidechain records anywhere." The glob was `*/*.jsonl`, which cannot reach one level deeper than the records live. **A negative result from a search that could not have found the thing reads identically to a real absence.**
- Two probe negatives where a silent failure to connect and a genuine "unsupported" were the same empty output — one of which was *one of the two answers the probe existed to distinguish*.
- A proof written to `/tmp`, which node resolved to a nonexistent `C:\tmp`. It returned empty for **both** the pre-fix and post-fix versions. It surfaced only because the author expected the pre-fix run to differ and it didn't.

The sixth was caught before it happened: overwatch specified a pinning test that would have passed on a branch where no production path could ever set the field it asserted — **a fixture proving the mapping on plumbing that did not exist.** It was specified *because* of the five above, in a form that would have produced a sixth. Watching for a failure mode at one level while writing it in at the level above is exactly how it survives.

**How to apply — make the check prove itself before you read its verdict:**

- **Assert the injection landed.** Before trusting a run, confirm the file changed, the fixture exists, the path resolved. `grep -c` on the modified line costs one command.
- **Prove a negative could have been positive.** Send something you know succeeds first. A probe that cannot demonstrate its own reachability reports "unsupported" and "unreachable" identically.
- **Revert and watch it fail.** A regression test that is green both with and without your change tests nothing. Disable the fix, confirm exactly the expected test fails, restore. This is the strongest form and it is cheap.
- **Check the plumbing, not only the logic.** A hand-built fixture satisfying a mapping says nothing about whether any production path computes the input. Ask: *what sets this field in the real system, and did my test exercise it?*
- **Distrust a result that agrees with you too easily** — especially an empty one. Absence is the output of both success-at-finding-nothing and never-having-looked.

**The tell is expectation.** Every instance above was caught by someone who expected a *difference* and saw none. If two runs that should differ produce identical output, the check is the suspect before the code is.
