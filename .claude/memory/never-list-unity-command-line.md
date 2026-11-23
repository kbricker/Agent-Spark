---
name: never-list-unity-command-line
description: "Listing processes? Id/Name/Title only; Kyle's Unity args carry an access token"
source: core/never-list-unity-command-line@88
metadata:
  type: feedback
---

A process listing that included command lines (plan 1106, 2026-10-06) printed the access token in Kyle's Unity editor launch arguments into the transcript.

**Why:** credentials are radioactive ([[credentials-radioactive]]) — once a token is in a transcript, brief or plan it is in the record for good, and nothing downstream can un-see it.

**How to apply:** when you need a PID, or to know whether Unity is running, select `Id`, `ProcessName`, `StartTime`, `MainWindowTitle` only — never `CommandLine`, never `wmic process`, never `ps -f`. To know which clone a Unity holds, pull the `-projectPath` value out inside the script and print only that and the PID (kits/highlight-art/run-1280.sh does this). Never paste any process listing into a brief, plan, report or Slack message. If a token does slip into a tool result, do not repeat it anywhere, and say so to Kyle in one line without quoting it.

**In briefs:** any brief that touches processes carries this sentence: "Never print a process command line; to learn which clone a Unity holds, extract the -projectPath value inside the script and print only that and the PID." A subagent printed the Hub token this way on 2026-11-20 (vaexdev2's finding, relayed by overwatch); the guard is ticketed as 796.18.
