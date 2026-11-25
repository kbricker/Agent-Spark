---
name: unwatch-when-idle-is-not-your-next-step
description: "Watching an agent whose idle isn't your next step? Unwatch — each working event is noise Kyle reads"
source: orchestrator/unwatch-when-idle-is-not-your-next-step@14
metadata:
  type: feedback
---

Kyle 2026-09-28, after four "spark started working" turns during plan 1080: *"stop watching spark."* Spark's TendWright cleanup was a validation item I could read from its chat or from the repo's branch list at the validation step; keeping it on the watch list made every agent_working event a turn whose only output was "no change".

**Why:** a watch exists so an agent_idle event drives your next step (use-channel-events). When nothing you do next hangs on that event, the watch produces only noise, and the noise lands in Kyle's terminal one line per event.

**How to apply:** watch an agent only while its idle event is the trigger for your next action, and unwatch the moment it is not. An agent_working event never needs a reply or a turn of work. A result you need later comes from hive_read_chat or from repo state when you reach that step. Related: [[channel-rewatch-after-spawn]], [[kyle-reads-and-directs]].
