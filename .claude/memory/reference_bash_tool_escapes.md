---
name: Bash tool halves backslash pairs and chokes on long heredocs
description: Writing a script or long file through the Bash tool? Backslash pairs arrive halved, >8 KB heredocs fail — use Write
type: reference
scope: global
---

The Bash tool's transport halves backslash pairs before bash sees the command — `\\` arrives as `\`, `\\\\` as `\\` — while single escapes (`\n`, `\t`, `\r`) arrive literally. A quoted heredoc (`<<'EOF'`) does not protect you; the halving happens before the shell. Separately, commands carrying heredocs over ~8 KB fail outright with "unexpected EOF while looking for matching `'`" and run nothing.

Two independent hits, both silent until byte-level inspection:
- 2026-09-04 (overwatch, plan 999): `C:\\Projects\\...\\appsettings` inside a python heredoc became `C:\Projects\...`, which Python read as `\a` — a bell character written into a skill file. Measured with `printf | od -c`.
- 2026-09-12 (vaexdev2, plan 1032, finding 1854): a regex written as `\\b` through a python heredoc landed in a C# file as literal backspace bytes (`'X\\bY'` printed length 3 with 0x08). It compiled, matched nothing, and only review round 2 caught it.

**How to apply:** scripts, hook files and any content longer than a screen go through the Write tool (verbatim bytes, no transport), then run from Bash by path — the same hatch the retrieved note `reference_bash_permission_matching` (hive_recall it) uses for loop-shaped commands. Keep Bash commands short and free of doubled backslashes; when a literal backslash is unavoidable inline, build it with `chr(92)` or write it doubled, and after any scripted edit that involves escapes verify the bytes (`python -c "print(repr(open(p,'rb').read()))"` or `od -c`) before trusting the file.
