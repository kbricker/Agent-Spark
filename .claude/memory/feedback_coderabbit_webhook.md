---
name: CodeRabbit reviews arrive via webhook — don't poll, don't ScheduleWakeup
description: GitHub webhook pushes CodeRabbit PR review events into hive-channel as chat_message events — never poll, never ScheduleWakeup to check, just wait
type: feedback
scope: global
originSessionId: 06a2d173-b00c-491d-84d9-213f71598ead
---
CodeRabbit review notifications arrive via GitHub webhook into the hive-channel as chat_message events. Do NOT poll `gh api` / `gh pr view` for review status, do NOT manually trigger `@coderabbitai review`, and do NOT ScheduleWakeup to "check CR status later" — the webhook is the notification. Just wait for the channel event.

**Why:** Kyle has corrected this behavior multiple times (2026-03 polling, 2026-04-18 ScheduleWakeup to poll PR #69). Polling wastes agent turns, the wakeup burns cache, and the system is already event-driven. The memory existed but I kept defaulting to poll-style "check back in N minutes" patterns.

**How to apply:** After a PR is created or updated, do NOTHING. Do not schedule a wakeup. Do not check back. The channel will deliver a chat_message when CodeRabbit posts its review. If Kyle asks about status, then and only then call `gh pr view` once — but don't schedule it proactively. Only intervene by polling if the webhook hasn't fired after an unusually long time AND Kyle asks you to investigate.
