---
name: Never write function docstrings in any codebase
description: NEVER write function docstrings anywhere — 100% rule; don't sweep existing ones; ignore CodeRabbit docstring warnings
type: feedback
scope: global
---

Never write function docstrings, anywhere in any project. This is a 100% rule, not a style preference to weigh per-file.

**Why:** Kyle 2026-08-05: "doc string format is heavy and wasteful the vast majority of the time, I would prefer we never use them anywhere... i am saying 100% on that as a rule." Promoted from a 3dproppipeline-local memory after an audit found the local rule contradicted by 98/303 functions and Kyle reconfirmed it fleet-wide instead of retiring it.

**How to apply:** New and edited code gets no docstrings — a comment stating a constraint the code can't show is fine, the docstring format is not. Do NOT proactively strip existing docstrings ("Im not saying go back and clean anything up right now"); removing one you're already rewriting is fine. Never propose docstrings to satisfy CodeRabbit — skip/ignore its docstring-coverage warnings and pre-merge checks.

**Scope — functions, not a module docstring that IS user-facing output.** The rule targets the per-function block that restates a signature: that is the heavy, wasteful form Kyle named. A **module** docstring on a CLI entry point is different in kind, because Python surfaces `__doc__` as the tool's help text — rewriting it as `#` comments deletes it from what the user reads, which is a functional change, not a style one. Keep those. Everything else stays covered, including module docstrings on library modules that nothing prints. (Overwatch 2026-08-10, resolving an ambiguity between this file's title, which said "function docstrings", and this paragraph, which said "no docstrings" — raised by `tools/analyze_ui_asset.py`, whose module docstring carries the tool's five measured blind spots and prints with `--help`. Kyle set the 100%; if he meant it to cover this too, this paragraph is what to correct.)
