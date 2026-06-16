---
name: GitHub SSH alias for WonderForge
description: WonderForge GitHub repos use custom SSH host github-second.com (kyle@wonderforge.io key)
type: reference
scope: global
---

WonderForge GitHub repos must use `github-second.com` as the SSH host, not `github.com`.

- SSH config alias: `github-second.com` → `github.com` with `~/.ssh/id_ed25519_wf`
- Example remote URL: `git@github-second.com:WonderForge/overwatch.git`
- The default `github.com` host uses a different key and won't authenticate to WonderForge repos
