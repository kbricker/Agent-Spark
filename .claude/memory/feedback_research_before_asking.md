---
name: Research it yourself before asking Kyle to go look
description: Exhaust your own research before asking Kyle to gather info — never use him as a sensor for what's publicly documented
type: feedback
scope: global
---

Before asking Kyle to go look at something, photograph something, or hunt through a menu, ask: **could I resolve this myself with a search?** If the thing has a model number, a package name, a version string, or a vendor — it is documented somewhere and the answer is a web search away. Do that first.

**Why:** 2026-07-28, the cell1 BIOS (spark, on TendWright). Kyle, afterwards: *"the key knowldge here that we want to capture is that you had enoguh info to look online and figure all this stuff out and I had to volly things with you a few times and expressly tell you to go do more research you could have done already."*

The sequence, which is the damning part:

1. Wrote a BIOS settings table from general desktop-motherboard knowledge. Never searched. Nothing in it matched his screen.
2. He said it matched nothing. It was retracted — **and still nothing was searched.** He was asked for photographs instead.
3. He sent them. That gave the exact board (Minisforum UM350), BIOS build (AF5PL01, Aptio 2.20.1274), CPU (Ryzen 5 3550H) and the full Advanced menu listing. All of it was read — and then he was told to go photograph a *different* menu.
4. He searched that menu thoroughly, found nothing, and had to explicitly say *"please try to find online refs for this bios management and this hardware."*
5. The search happened. Two queries. Under a minute. The setting was under `Advanced → AMD CBS`, listed **in the photograph from step 3**, and hidden until a prerequisite dropdown is changed — which is why no amount of looking would have found it.

Three rounds of his time, and the resolving action was available at step 1.

**The failure is not being wrong. It is treating Kyle as an I/O device** for information that was public. A search costs seconds; walking to a machine, navigating firmware, photographing it and coming back costs him minutes and a context switch — repeated, because each round only produced another guess.

**How to apply:**

- **The retraction IS the trigger.** The moment you say "I wrote that from general knowledge and it was wrong," the next action is to go get specific knowledge — not to ask Kyle to supply it. Retracting and then delegating the correction is the exact anti-pattern.
- **Identifiers are permission to search.** A model number, package name, driver, or version string means the thing is documented. "I don't know the specifics of this particular X" plus "X has a model number" equals *search*, not *ask*.
- **Check what you were already given.** In step 3 the answer was on screen and went unconsulted, because the question of where it lived had already been decided. Having evidence is not the same as reading it.
- **When you do ask him for something physical, say what you already ruled out.** If a search genuinely could not answer it, show that — so the request reads as the remaining gap rather than the first thing you tried.
- Asking is right when the answer is *specific to his hardware, his room, or his preference* — what's plugged in, what the arm did, which option he wants. It is wrong for anything a vendor, package or driver documents.

Related: [[feedback_verify_before_asserting]] is the local-state sibling — verify against the machine before asserting. This one is about the outside world: research before delegating the lookup to a human. Both failed the same day and for the same underlying reason, which is answering from recall when the real answer was cheaply obtainable.
