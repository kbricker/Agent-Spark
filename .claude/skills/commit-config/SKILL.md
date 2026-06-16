---
name: commit-config
description: Commit and push changes to the current orchestrator's own config repo after edits — memory files, skills, hooks, MEMORY.md, settings, CLAUDE.md, .mcp.json. Use when Kyle says "commit your config" or after a batch of config edits. The skill auto-adapts to whichever orchestrator is running it (overwatch, verletDev, vaexdev).
scope: global
---

# Commit Orchestrator Config

Each virtual orchestrator has its own workspace repo that holds its `.claude/` directory, hooks, settings, and CLAUDE.md. When any of that changes, the repo should be committed and pushed so the config is version-controlled and Kyle's other hosts / fresh clones pick it up.

This skill runs in the **current orchestrator's** workspace. Which orchestrator that is depends on the session — use the dispatch table below to pick the right repo path, branch, and remote.

## Per-orchestrator dispatch table

| Orchestrator | Repo path | Default branch | Remote URL |
|---|---|---|---|
| overwatch | `C:\Projects\overwatch` | `master` | `git@github-second.com:WonderForge/overwatch.git` |
| verletDev | `C:\Projects\verletDev` | `main` | `git@github-third.com:kyle-gnl/verletdev.git` |
| vaexdev | `C:\Projects\vaexdev` | `master` | `git@github-second.com:WonderForge/vaexdev.git` |

When you run this skill, identify which orchestrator you are (from session context / agent key / the working directory you're in), then use the matching row's values everywhere the procedure references `<repo-path>`, `<branch>`, etc.

If you're running this skill and can't tell which orchestrator you are: stop, ask. Never guess — committing to the wrong repo can silently lose work.

## When to use

- Kyle says "commit your config," "push your repo," "sync [orchestrator]," or similar after you've edited memory/skills/hooks/settings.
- You just finished a batch of config edits (new memory, new skill, updated hook) and Kyle's rhythm is to keep the repo current.
- **Not** for one-off debug edits you're going to revert.
- **Not** for changes outside your own orchestrator's repo. Don't use this skill to commit wfa2, Verlet, VaEx, or another orchestrator's workspace.

## What's in scope

The orchestrator repo's tracked files are:

- `.claude/memory/*.md` — memory files
- `.claude/memory/MEMORY.md` — memory index
- `.claude/skills/<name>/SKILL.md` — skills
- `.claude/hooks/*.sh` — status hooks
- `.claude/settings.json`, `.claude/settings.local.json` — project settings
- `CLAUDE.md` — project instructions at repo root
- `.mcp.json` — MCP server configuration
- `.gitignore`

Anything outside these paths is out of scope. If `git status` shows untracked files in unexpected locations (stray `.log`, editor backups, test artifacts, loose Playwright scripts), **stop and ask Kyle before committing** — do not blanket-add the whole working tree.

## Workflow

### 1. Status check — know what you're about to commit

From `<repo-path>`, in parallel:

```bash
git -C <repo-path> status
git -C <repo-path> diff --stat
git -C <repo-path> log --oneline -5
```

Reconcile three questions:
- **What changed?** Read the full diff of modified files, not just `--stat`. Make sure every change is intentional and matches the work you just did.
- **What's untracked?** If it's a new memory file, new skill, new hook — good, stage it. If it's something unexpected, ask.
- **What's the commit style here?** Look at the last few commits to match the tone and subject-line pattern.

### 2. Stage specifically — never blanket-add

Use `git add <path>` for each intended change. **Do not** use `git add -A` or `git add .` — those scoop up anything stray, including unrelated drift from prior sessions.

```bash
git -C <repo-path> add .claude/memory/feedback_plans_default_planning.md
git -C <repo-path> add .claude/memory/MEMORY.md
git -C <repo-path> add .claude/skills/commit-config/SKILL.md
```

After staging, run `git status` once more to verify the staged set matches exactly what you meant to commit and nothing more.

### 3. Compose the commit message

- **Subject line:** short imperative, under 72 chars. Lead with the verb. Reference a plan number if applicable (`Plan #276: ...`).
- **Body:** only if the subject doesn't capture the "why." For memory additions, one sentence on the reason. For a new skill, one sentence on what it automates. Skip the body entirely for trivial changes.
- **Always use a HEREDOC** when passing the message to `git commit -m` so formatting survives.
- **Always include the Co-Authored-By trailer** per the global commit rules.

Example:

```bash
git -C <repo-path> commit -m "$(cat <<'EOF'
Plan #276: sync global memories from canonical source

Pulled 40 global memories from wfa2/orchestrator-shared/memory/ and
updated MEMORY.md index accordingly.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### 4. Push to origin

```bash
git -C <repo-path> push origin <branch>
```

Use the branch name from the dispatch table (overwatch: `master`, verletDev: `main`, vaexdev: `master`).

**Never** force-push. If the push is rejected because the remote is ahead, pull with `git pull --rebase origin <branch>`, resolve any conflicts, and push again. Do not `--force` or `--force-with-lease` unless Kyle explicitly says so.

### 5. Confirm to Kyle

One or two sentences: what committed, what the SHA is, and that it's pushed.

## Gotchas

- **Pre-commit hooks:** the global commit rules say never skip hooks. If a hook fails, fix the underlying issue and create a **new** commit — do not `--amend` the failing one.
- **Unrelated local changes:** if `git status` shows changes in files you didn't touch in this session (stale edits from a prior session, auto-generated files), don't silently include them. Ask Kyle whether to include them, stash them, or leave them unstaged. **Especially relevant for verletDev** — it tends to accumulate uncommitted session drift.
- **MEMORY.md drift:** whenever you add or rename a memory file, MEMORY.md needs to be updated in the same commit so the index stays accurate. Never commit a new memory file without also updating the index.
- **Wrong branch:** overwatch and vaexdev use `master`; verletDev uses `main`. The three-orchestrator dispatch table is canonical — if in doubt, run `git -C <repo-path> branch --show-current` to verify before pushing.
- **Wrong SSH alias:** WonderForge repos use `github-second.com`; kyle-gnl repos (verletDev) use `github-third.com`. Plain `github.com` is a different GitHub account. Check `git -C <repo-path> remote -v` if auth errors surface.
- **Secrets:** the `.gitignore` excludes secret files. If you ever see `secrets.json` or `appsettings.Development.json` staged, unstage immediately — something is broken.

## Do not

- Do not amend published commits.
- Do not force-push the default branch.
- Do not `git add -A` or `git add .`.
- Do not commit without the Co-Authored-By trailer.
- Do not commit to a repo other than the current orchestrator's workspace.
- Do not commit without running `git status` + `git diff` first and checking the full set of changes.
