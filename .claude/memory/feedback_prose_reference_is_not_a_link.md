---
name: A prose reference is not a link — the machine-readable half is the half review cannot see
description: Prose isn't a link — set questionId/index markers in the same edit; review reads prose only, missing links fail silently
type: feedback
scope: global
---

**Where an artifact carries both a human-readable form and a machine-readable one, they are two separate claims and only one of them is reviewed.** Writing "this answers question X" in prose does not answer question X. Writing the right heading does not create the marker. Quoting a description does not keep it current. The tool reads the link; the reviewer reads the text; nothing compares them.

The failure mode is specific and nasty: **the artifact looks correct to every human who reads it, and is wrong only to the tool that consumes it.** So it passes review, and the defect surfaces later as the tool "misbehaving".

## Why — three instances in one day, three unrelated surfaces

2026-08-10, none of them found by a check, all found incidentally:

1. **A shaping-log decision that settled an open question.** Entry `8777b01a` on plan #842 names question `34b49573` by id in its own first paragraph and says in plain words that it reverses it. But it was typed `decision`, not `answer` with a `questionId`, and `BuildAnsweredIndex` keys on the link. The corpus reported the question open for a day while the text said otherwise.
2. **A hand-built `MEMORY.md`.** hivedev01's index carried the managed `## Global` / `## Role:` headings but none of the `<!-- BEGIN/END -->` marker comments. Those headings are decoration the generator never reads; the markers are the whole locating mechanism. On the next run it would have found no managed region, taken the first-time path, and appended a second complete copy of every block — 32,112 bytes against a 25,000 cap, growing on every run after.
3. **A memory's index hook.** A canonical memory's `description` was edited and the file propagated to six workspaces without regenerating the indexes that quote it. Every workspace pointed at that memory with a hook that no longer matched it — and the hook is the part loaded into context.

## How to apply

- **When you write the prose, write the link in the same edit.** An entry that settles a question sets `questionId`. A file that supersedes another sets the pointer. Not "and I'll link it after".
- **Reproducing a generated artifact by hand means reproducing its machine-readable parts, not its appearance.** If you cannot state which bytes the tool keys on, do not hand-build it — run the generator.
- **Test idempotence, because that is the check that sees this class.** Re-run the generator and diff: a correctly-formed artifact reproduces byte for byte. That one line would have caught instance 2 immediately, and nothing else did.
- **When you edit a field something else copies, regenerate the copies in the same commit.** The source and the quote drift silently and the quote is usually the one that gets read.

Related: [[feedback_check_what_overrides_the_file]] — the same class one step over, where the thing you edited is regenerated out from under you. Both come from an artifact having a second author you did not think about: there, a generator; here, a parser.
