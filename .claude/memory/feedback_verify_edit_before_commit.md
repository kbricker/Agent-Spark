---
name: Verify Edit success before committing and claiming cleanup landed
description: When an Edit tool call fails (string-match mismatch), the file is unchanged on disk. Never claim a cleanup "landed" without running git diff first — I shipped a lying commit message on 2026-04-13 because I assumed an Edit succeeded when it hadn't
type: feedback
scope: global
---

If an Edit tool call returns `String to replace not found in file`, the file on disk is **unchanged**. It is NOT a retry hint or a partial success — the edit simply did not apply.

**Why:** On 2026-04-13, during plan #171 gameplay polish, I added diagnostic `console.log` scaffolding to `GameManager.ts` across multiple Edit calls while debugging a win-condition overlay bug. When Kyle reported "it works!", I ran a final Edit to strip the diagnostics. That Edit FAILED with a string-match error (because intermediate edits had shifted the content), but I didn't check — I immediately ran `git add` + commit + push with a message claiming the diagnostics were stripped. The file was committed AS-IS with the full `PRE-SET/POST-SET/T+500ms/T+1000ms/WINMARKER-LOOK-FOR-THIS` instrumentation still in place. Kyle caught it when his next test logged the `gameOver` diagnostic. I had to push a second "actually strip for real this time" commit with an embarrassing message.

**How to apply:**
- After any Edit call that's meant to REMOVE code (especially debug/diagnostic code), **run `git diff <file>` BEFORE `git add`**. Verify the diff shows the intended removal.
- Treat "String to replace not found" as a hard failure, not a retry hint. Either (a) re-read the file to see current state and write a new Edit, or (b) use Write to replace the whole file. Never assume the edit "probably worked".
- Never write a commit message that claims a cleanup landed unless you've personally confirmed the removal via `git diff --cached` or equivalent.
- For debug instrumentation specifically: prefer a single big temporary block you can strip with ONE Edit, so there's one thing to remove and one diff to verify. Avoid accreting scattered console.logs across many Edit calls — each one is a new opportunity for the stripping Edit to miss content.
- Bonus rule: if your commit message ever contains "strip" or "remove" or "clean up", the pre-commit mental checklist should include "did I actually verify the removal with git diff?"

**What this is NOT saying:** don't fear Edit. It's still the right tool for most file modifications. The rule is narrow: verify removals before claiming them.
