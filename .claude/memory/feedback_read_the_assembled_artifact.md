---
name: Read the assembled artifact, not just your diff
description: "Before committing text you drafted for a file you couldn't fully read, read the assembled file in place — correct text goes false by adjacency, and the diff never shows it"
type: feedback
scope: global
---

**Text drafted blind can be transcribed perfectly and still be wrong in situ.** Two accurate pieces of text become a false statement by sitting next to each other, and verifying each part in isolation cannot catch it — because neither part is wrong.

This is not the relay failure in [[feedback_verify_before_asserting]]. Nothing there is unverified and nothing degrades in transmission. The defect is **compositional**: it exists only in the adjacency, and it is created by the edit without appearing anywhere in the edit.

**Why:** 2026-08-10, plan #865. forge had no write access under `.claude/` (see #868), so it drafted runbook prose from memory of a file it could not open, and another agent typed it in. Placement was faithful — every block landed exactly where specified. It was still wrong: forge's new line *"Being in sync with origin is NOT one-time"* landed six lines beneath an existing heading reading *"Prerequisites (all one-time, already in place)."* A reader who trusted the heading and skimmed got precisely the belief the edit existed to destroy — that a clone 435 commits behind is dead rather than unpulled. forge's block was correct. The transcription was correct. The old heading was correct when it was written. The diff showed none of it, because **the defect lived in the unchanged context around the change.**

**How to apply:** When you author text for a file you have not read end to end — or when someone else's hands typed it — **read the assembled file in place before committing, at the altitude of the reader who will skim it.** Headings, opening lines, and list preambles matter most: they are what a hurried reader takes as the summary of everything beneath them, so a stale one silently relabels correct new text. Reviewing the diff is not sufficient and never will be, because the diff shows what you changed and this defect is made of what you didn't.

The check is cheap and the trigger is broad. It applies to any blind or partial authorship: runbook sections, config fragments, memory files, a checklist item pasted into an existing plan, a paragraph added to a plan description someone else wrote. Whenever your words will be read next to words you did not write, the assembled artifact is the thing to verify — not your contribution to it.
