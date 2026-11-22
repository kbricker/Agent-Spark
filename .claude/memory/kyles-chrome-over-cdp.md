---
name: kyles-chrome-over-cdp
description: "Need a page or file behind Kyle's login? Playwright over CDP into his signed-in Chrome: ws URL from DevToolsActivePort (http 404s), he clicks Allow when it waits, so one job per connection"
source: spark/kyles-chrome-over-cdp@19
metadata:
  type: reference
---

Kyle's everyday Chrome has remote debugging switched on in its own settings, not by a `--remote-debugging-port` flag, so Playwright can drive it with his sign-ins (Kyle 2026-11-22: "you should be able to playwright to it").

- Connect with `chromium.connectOverCDP('ws://127.0.0.1:<port><path>')`. The port is line 1 and the path line 2 of `%LOCALAPPDATA%\Google\Chrome\User Data\DevToolsActivePort`. The HTTP endpoints such as `/json/version` answer 404, so an `http://` connect fails.
- A new connection waits on an Allow prompt in Chrome until Kyle clicks it: on 2026-11-22 two unattended tries timed out at 3 and 30 minutes, and later runs waited 4 and 26 minutes for him. So start only when he says he's at the PC, tell him to click Allow, and do the whole job in one connection.
- Playwright is installed globally; require it from `%APPDATA%\npm\node_modules\playwright`.
- Work in a new page and close only that page: never `browser.close()`, never kill Chrome ([[never-kill-chrome]]). Download with `context.request.get`, which sends his cookies without anyone reading them ([[credentials-radioactive]]), and print URLs without their query strings, which can carry order keys and tokens.
- Downloads go in a new empty folder, outside every repo.
