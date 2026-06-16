---
name: feedback_personal_repo_git_identity
description: Spark's projects are Kyle's PERSONAL repos — commit as Kyle Bricker <kyle.bricker@gmail.com>, never the WonderForge identity
type: feedback
---

Spark hosts Kyle's PERSONAL projects, not WonderForge work. Commits in any Spark project MUST use his personal identity — `Kyle Bricker <kyle.bricker@gmail.com>` — never the global WonderForge identity `kyle-wf <kyle@wonderforge.io>`.

**Why:** the machine's GLOBAL git config is the WonderForge identity (correct for wfa2 / VaEx / Hive / the other orchestrators). On 2026-06-15 the WonderForge email leaked into 10 Orbital commits; the history had to be rewritten and force-pushed to purge it, and Kyle explicitly asked it never happen again. Spark exists partly so personal-project config stops mixing with the WonderForge orchestrators.

**How to apply:** every Spark project repo carries a LOCAL git config override (`git config user.name "Kyle Bricker"; git config user.email "kyle.bricker@gmail.com"`) that wins over the global — set it the moment a new personal repo is created, and never reset or clear it. Don't pass `--author` with the WonderForge identity, and don't enable WonderForge commit signing in these repos. Pushes go over Kyle's personal GitHub SSH (host `github.com`). See [[project_orbital]] for the first project this applies to.
