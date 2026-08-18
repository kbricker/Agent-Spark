---
name: Check which config layer wins before you edit
description: The file you are about to edit is often not the authority — check for a generated block, fence comment, or .d/ drop-in
type: feedback
scope: global
---

Configuration is layered more often than it looks. Before editing any index, config, or generated file, establish **which layer actually wins** — read the file's header, look for a fence comment, and check for a sibling `.d/` directory. An edit to a non-authoritative layer does not error. It succeeds, changes nothing, and leaves no trace explaining why.

**Why:** two instances on 2026-07-28, hours apart, both by spark on TendWright, both caught by Kyle rather than by the agent.

**1. A managed block in a file the agent was already reading.** A new memory was appended to spark's `.claude/memory/MEMORY.md` at line 100 — inside the block fenced by `<!-- BEGIN GLOBAL SECTION (managed by propagate-shared-config — do not edit by hand) -->`, whose own body reads *"All memories in this section are copies of the canonical source... Edit those originals, not these copies."* The local section did not start until line 159. The next propagate run would have erased the index line and orphaned the file, and a memory marked `scope: global` living in one workspace is not global. Kyle: *"wait u edited the canonical agent setup ?"*

**2. A drop-in directory on cell1.** To reclaim 512 MB from a `crashkernel=` reservation, the agent told Kyle to edit `GRUB_CMDLINE_LINUX` in `/etc/default/grub`. That file was stock. The reservation came from `/etc/default/grub.d/kdump-tools.cfg`, a package-shipped drop-in — and `grub-mkconfig` sources `/etc/default/grub.d/*.cfg` **after** `/etc/default/grub`, so the drop-in always wins. He would have made the edit, run `update-grub`, rebooted, and found the memory unchanged with nothing to point at. Caught only because he remarked the setting was probably old cruft, which prompted checking where it came from.

Same shape both times: **the agent knew the file's conventional role and therefore did not read the specific instance.** In case 1 the disclaimer was three lines from the fence, in the file being edited. In case 2 one `ls /etc/default/grub.d/` would have shown it.

**How to apply:**

- **Before editing a config file, ask what assembles it.** Look for a fence or `DO NOT EDIT` comment, a `.d/` sibling directory, a template it is generated from, or a sync/propagate step that rewrites it. Two commands, and it decides whether the edit is real.
- **Later layers win.** `*.d/` drop-ins are sourced after the base file; generators overwrite hand edits wholesale. Editing the base and hoping is not a plan.
- **The failure is silent, which is what makes it expensive.** A rejected edit teaches you something. An edit that applies cleanly and has no effect sends someone to reboot a machine and come back confused.
- **Generated fields have one source.** If a value appears in two places — an index hook and a frontmatter field, a summary and its origin — find out which is generated. Editing the generated copy is the same mistake in miniature.
- When the authoritative layer is outside your charter (canonical shared config, another agent's repo), propose the change to its owner rather than editing your synced copy.

Related: [[feedback_verify_before_asserting]] and [[feedback_research_before_asking]] are the same underlying habit — acting on how something usually works instead of checking this instance. Those two are about knowledge; this one is about the artifact directly under your hands, which is why it stings more.
