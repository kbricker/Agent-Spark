---
name: Why an allowed Bash command still prompts
description: A bare Bash allow rule does NOT match past a shell variable assignment — write literal commands, not VAR=... ones. Plus the other documented carve-outs that defeat allow rules.
type: reference
scope: global
---

Observed on Claude Code **v2.1.220**, 2026-08-03. Permission semantics move between versions — re-check `https://code.claude.com/docs/en/permissions` before trusting this, per [[feedback_check_docs_on_harness_friction]].

## The rule that bites us

> "An allow rule won't match past an assignment of any other variable."

**Any `VAR=value` in a Bash call defeats the allow rule — including a bare `Bash`.** Only a short built-in list of known-safe env vars (e.g. `NODE_ENV=test npm test`) is stripped before matching. Everything else prompts, and if you answer "yes, don't ask again" it mints a narrow `Bash(...)` rule into `.claude/settings.local.json`.

This is why blanket-allowing `Bash` does not eliminate prompts, and why deleting the accumulated narrow rules never sticks: the rules are a *symptom*. A command that prompts once prompts every time it runs, so anything in a startup path re-mints its rule on every session. Overwatch's restart-handoff claim did exactly this — `TS=$(date ...)` inside the claim sequence — regenerating the same two rules each launch and reading as unexplained "permission drift".

**The asymmetry is deliberate, and only allow rules are affected.** The very next line of the same doc paragraph:

> "A deny or ask rule matches past any leading assignment, so `Bash(rm *)` in deny still matches `FOO=bar rm -rf tmp/`."

So a deny rule **cannot** be evaded by prefixing an assignment — this is a safety design, not a matching bug. Do not generalise it to "assignments defeat rule matching"; that reads as a hole in deny rules, which would be exactly backwards. Allow loses the match, deny and ask keep it.

**So: write literal commands.** Need a computed value? Get it in a *separate* read-only call (`date`, `ls`, `git rev-parse`) and paste the literal into the next command. Two clean calls beat one convenient call plus a prompt.

## Other documented ways an allow rule fails to match

- **Compound commands are split** on `&&`, `||`, `;`, `|`, `|&`, `&` and newlines; **a rule must match every subcommand independently**. Approving a compound with "don't ask again" saves a separate rule per subcommand, up to 5.
- **Exec wrappers always prompt** and cannot be prefix-approved: `watch`, `setsid`, `ionice`, `flock`, and `find` with `-exec`/`-delete`.
- **Environment runners are not wrappers**: `npx`, `docker exec`, `direnv exec`, `mise exec`, `devbox run` are not stripped, so `Bash(devbox run *)` would allow anything after `run`. Write runner+inner-command rules instead.
- **Unparseable commands prompt**, as do commands over 10,000 characters.
- **Unquoted globs** prompt for commands with write- or exec-capable flags (`find`, `sort`, `sed`, `git`).
- **`cd` into a different directory combined with `git`** prompts, because the new directory's hooks could run.
- **Windows UNC paths** (`\\server\share`) always prompt — credential-leak guard.
- Evaluation order is **deny → ask → allow**, first match wins; specificity does not override order. A bare-name *deny* removes the tool from context entirely.

## What is stripped (so rules still match)

`timeout`, `time`, `nice`, `nohup`, `stdbuf`, the builtins `command` and `builtin`, zsh's `noglob`, and flagless `xargs`.

## Related

Keep bare `Bash` + `PowerShell` in the allow list ([[feedback_blanket_shell_allows]]) — it is still correct and still matches everything without an assignment. `.claude/settings.local.json` is machine-managed; treat mints as a signal that a command shape needs fixing, not as config to curate.
