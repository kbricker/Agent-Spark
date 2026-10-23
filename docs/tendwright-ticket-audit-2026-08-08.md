# TendWright open-ticket audit — 2026-08-08

Requested by overwatch on Kyle's behalf. Scope: all 38 open plans in Hive app 8
(TendWright). Analysis only — nothing was changed, forked, cancelled or moved.
Sibling audits: vaexdev2 on VaEx, overwatch on Studio.

Method: full `hive_plan_get` on all 38 (description + checklist + branch/PR),
plus the repo itself — `git log`, `git branch -vv`, and direct reads of
`sim/twin.py`, `hardware/bench/cammanager.py`, `cameras.json`, `cell.json` and
`docs/bench-tasks-2026-07-31.md` to settle every MISLABELLED / PARKED call
against on-disk reality rather than against ticket text.

---

## The headline: Kyle's hypothesis is confirmed, and low by about half

> *"I suspect 25% or more of our planning tickets might be considered Ready if
> we really look hard."*

**42.9% (12 of 28)** of TendWright's Planning-status tickets are READY —
research done, no open question, a dev could start tomorrow.

Exclude the 7 module epics, which are permanent charter documents that can
never leave Planning because they will never complete, and the real figure is
**57.1% (12 of 21)**.

Either number confirms the hypothesis. The status field is carrying almost no
information: of 28 Planning tickets, 7 are containers that will sit there
forever, 12 are fully shaped and buildable, and only 8 are genuinely still
being figured out.

## Verdict distribution

| verdict | count | share |
|---|---|---|
| READY | 15 | 39% |
| PLANNING | 8 | 21% |
| EPIC | 7 | 18% |
| MISLABELLED | 6 | 16% |
| PARKED | 1 | 3% |
| DUPLICATE | 1 | 3% |
| STALE | **0** | 0% |

(READY is 15 across all 38; 12 of those sit in Planning status. The other three
are 715.3, already correctly flagged Ready, and 717.4 / 716.3, both parked in
Backlog by Kyle's explicit deferral.)

---

## What I actually learned

### 1. There is almost no PARKED work, and no stale branches holding any

**One PARKED ticket** (712.11), against overwatch's prediction of "fewer than
VaEx/Studio". The reason is structural rather than cultural: TendWright commits
**straight to main** and works one ticket at a time inline via fast-track. There
is no PR queue to abandon things in.

The repo carries 13 local plan branches and 6 pushed ones, which looks like
parked work and is not. **Every one belongs to a Completed plan** (604, 605,
618, 619, 631, 643, 645, 647, 648, 651, 653, 656). They are uncleaned debris
from the earlier branch-per-plan era, not stalled work. Safe to delete; worth
doing so, because they currently read as abandoned effort to anyone scanning.

### 2. Zero STALE — and that is a real result, not a soft grade

overwatch predicted TendWright might carry more STALE tickets, on the theory
that early tickets predate a settled direction. It did have a direction change:
on 2026-07-28 the whole module taxonomy was rewritten, because modules had been
named after ladder rungs rather than parts of the system, and `Hardware` had
absorbed 23 of 41 plans.

**That restructure was absorbed rather than left behind.** The epic was
rewritten (fork rev 2), six new module epics were authored fresh, and 612.3 was
rewritten from its 2026-07-15 draft. Nothing survives from before the change in
a form that contradicts it. No ticket on this board describes something that no
longer exists.

### 3. But staleness is real — it is *inside* live tickets, not *of* them

This is the finding the per-ticket vocabulary cannot express, and it is the one
I would act on first.

Several correctly-live tickets carry **dead prerequisites in their text** —
blockers that have since cleared, and nobody swept the description:

- **713.10** is held in Planning by one stated sequencing rule: *"SEQUENCE THIS
  AFTER 713.5, because the detector is a prime suspect in an active native
  leak."* 713.5 closed **2026-07-30**, nine days ago. The ticket is READY and
  reads as blocked.
- **713.7** carries a checklist item that must run *"BEFORE fixing"* — stop the
  side stream, re-measure the 713.5 leak. The fix shipped on 07-28. The
  experiment is now impossible, and the leak ticket it served closed anyway on
  07-30. A shipped fix is being held open by a validation its own shipping
  destroyed.
- **729** lists three blockers (713.5, 713.6, 713.7). Two are Completed and the
  third's code is merged.
- **713.9** has four of eight items done or overtaken by 716.4, 713.11 and
  716.5 — including "establish a real reach envelope", which 716.5 delivered
  (`sim/reach.py`, ring 83–277 mm, arc 205.4°). All four still read unchecked.
- **`cell.json` contradicts `cameras.json`.** The registry records the `low`
  camera as *"MOUNTED 2026-07-28: printed edge stand (717.5)"*; the cell model
  still says *"It has NO MOUNT AT ALL (717.5) and is currently offline"* and
  *"NAME AND ROLE ARE STILL PROVISIONAL"*. Both cameras remain `planned: true`.

A ticket-status audit cannot catch any of this, because every one of those
tickets has the *right* status. The rot is one level down. If there is a
recurring hygiene job worth adding, it is **sweeping the text of tickets whose
dependencies just closed** — at the moment a plan completes, re-read everything
that named it.

### 4. The dominant blocker is Kyle's hands, and the CONTAINMENT scale has no word for it

The scale offers `contained` (buildable as written), `needs-a-call` (specific
decisions), and `needs-shaping` (open-ended judgement). All three are about
**attention and judgement**. TendWright's actual bottleneck is neither:

- stick three AprilTags on the arm and measure their offsets (713.8, 716.4)
- focus two camera barrels on a grub screw and mark them (713.11)
- tape-measure two lens heights and standoffs (713.11)
- be physically present while the arm is powered (715.2, 716.6, 716.7, 712.5)
- stand at a BIOS screen prepared to clear CMOS (716.3)
- push-test a printed stand (717.5)

These tickets are **perfectly shaped, zero open questions, and still not
buildable**, because a person has to go into the room. That is a fourth
containment value — call it **needs-hands** — and on this board it is more
common than `needs-a-call`. It is also qualitatively different for roadmapping:
`needs-shaping` costs Kyle thought at his desk and can happen any time;
`needs-hands` costs him a bench session and can be **batched**, which is exactly
what `docs/bench-tasks-2026-07-31.md` already does informally.

Recommend #817 carry it as a distinct value. Rating it `contained` (true — the
ticket is complete) or `needs-a-call` (false — there is no decision) both lose
the real information.

### 5. Six MISLABELLED, and five of the six lean the same way

Every mislabelled ticket except one is **further along than its status claims**:

- **714.6** — merged to main (9ba1c6f), 6 of 7 items done, sitting in CodeReview
- **713.7** — fix verified live in `cammanager.py:461-467`, sitting in Development
- **717.5** — the stand is printed *and bolted to the table*, sitting in Development
- **713.9** — half its checklist delivered elsewhere, sitting in Ready
- **612.3** — a milestone gate sitting in Development while its real work forked
  out to 713.8 / 714.4 / 713.4 / 714.5

The single exception runs the other way: **716.5 is in Review with dev work
outstanding.** Its unchecked item is a `Fix` — replace the twin's infinite table
plane with bounded extents — and I verified it is genuinely not done
(`sim/twin.py:431-432` still builds the infinite plane). Review means dev is
complete. It isn't.

The pattern behind the five: **work finishes, and the last thing standing
between the ticket and Completed is a validation only Kyle can perform by
hand.** Nobody moves the status, because moving it would be a lie in the other
direction. So finished work accumulates in Development.

This is `feedback_dont_gate_on_manual_validation` firing across five tickets at
once. 714.6 is the clearest case — one bench check, everything else merged and
validated, held open eight days.

### 6. Forking inherits the parent's module, and nobody re-files

The 1:1 module↔epic rule was set on 2026-07-28 and is already being broken by
the fork mechanism itself. Three of the four live children of **716 (Cell)** are
not Cell work:

| plan | module | what it actually touches | belongs under |
|---|---|---|---|
| 716.5 | Cell | `sim/twin.py`, `sim/reach.py`, `bench_scene` | **714 Sim** |
| 716.6 | Cell | model masses, `qfrc_bias`, `sim/reach.py` | **714 Sim** |
| 716.7 | Cell | `sim/twin.py`, `runner.py`, `jog.py` | **714 Sim / 712 Motion** |

All three were forked from Cell tickets and kept the module. 714's charter
explicitly claims *"Gravity, payload, torque margin, and any servo model"* —
which is 716.6's entire content.

Separately, **three top-level plans carry a module but no parent**, which the
rule says is a mechanically detectable error: 729 (`Vision` → 713), 744 (`Cell`
→ 716), 751 (`Sim` → 714).

### 7. One genuine duplicate, found by concept and not by keyword

**714.5** ("Gravity and payload in the sim") and **716.6** ("The arm's static
holding envelope") share no significant vocabulary — "torque margin" versus
"holding envelope" — and neither references the other. They specify the *same
computation*: `mj_forward` at zero velocity, read `qfrc_bias`, report gravity
hold torque per joint against the 3.35 N·m actuator limit. 714.5 calls it Stage
1; 716.6 calls it item 1.

714.5 was written 2026-07-27; 716.6 on 07-31, four days later, re-deriving it
from scratch. Recommendation is a boundary, not a cancel: 716.6 keeps the bench
load-register calibration and the reach-zone bound (both unique, both tied to a
live incident), 714.5 narrows to Stages 2–3 and payload, and one of them owns
the torque function.

### 8. The board froze on 2026-07-31

Every commit in the repo stops on 2026-07-31 except one docs commit on 08-06.
Eleven of the fourteen most recent commits are 716.5 work. Every "Development"
ticket is an accurate snapshot of where work stopped, not drift — but that also
means **nothing on this board has moved in eight days**, and the ranking
question Kyle is asking is being asked at a natural restart point. The last
bench session's own task list opens by admitting the section below its divider
*"predates the build and needs a status sweep"*.

### 9. What I would pick up first, if it helps

Not asked for, but it falls out of the data. The critical path is short and
currently unowned:

**713.11 → 713.8 → 612.3.** Stabilise and measure the cameras (needs Kyle's
hands, one bench hour), then intrinsics + hand-eye (Stage 1 needs nobody), then
vision-guided picking — which is the thing Kyle actually said he wants. 713.8 is
named as a prerequisite by three separate tickets and sits in Planning at
READY.

Two safety items are also sitting at READY and outrank the roadmap: **716.7**
(the arm fell on 07-31 and took five attempts to recover; today the only escape
is disabling the gate) and **715.2** (j4 arrives at 8× commanded speed).

---

## The table

Verdicts use the fixed vocabulary. IMPACT answers "if we never do this, what
hurts". CONTAINMENT is Kyle's attention before it can be built — with
`needs-hands` used where the scale has no word (see finding 4); those are
otherwise fully contained.

| # | Plan | Status | Verdict | Impact | Containment | Note |
|---|---|---|---|---|---|---|
| 612 | TendWright epic | Planning | EPIC | high | contained | 5 live rung children (612.3–612.7). Vision doc; will never close |
| 712 | Motion | Planning | EPIC | high | contained | 5 live children |
| 713 | Vision | Planning | EPIC | high | contained | 6 live children |
| 714 | Sim | Planning | EPIC | high | contained | 3 live children |
| 715 | Hardware | Planning | EPIC | med | contained | 2 live children |
| 716 | Cell | Planning | EPIC | high | contained | 4 live children, 3 of them misfiled (finding 6) |
| 717 | Build | Planning | EPIC | med | contained | 3 live children |
| 612.3 | P2 vision pick-and-place | Development | MISLABELLED | high | needs-shaping | → Planning. A milestone gate in Development; real work forked out to 713.8/714.4/713.4/714.5. Its items are tasks, not acceptance criteria — contradicting 612's own stated rule for rungs |
| 612.4 | P3 quality inspection ML | Planning | PLANNING | low | needs-a-call | Open Q: no part and no defect taxonomy exist yet. torch-vs-scikit-learn is an unauthorized new dep |
| 612.5 | P4 mini-MES | Planning | PLANNING | low | needs-a-call | Open Q: FastAPI + Streamlit + SQLite/Postgres are all unauthorized new deps |
| 612.6 | P5 telemetry | Planning | PLANNING | low | needs-a-call | Open Q: asyncua/MTConnect, pandas, Grafana — all unauthorized new deps |
| 612.7 | P6 capstone | Planning | PLANNING | med | needs-a-call | Open Q: does Kyle buy the 3018 GRBL CNC (~$120–200). Nothing starts until he does |
| 712.4 | bus.py serial identity | Planning | **READY** | med | contained | Live hazard on cell1: unplug the adapter with the Pico attached and tools talk Feetech at the microcontroller. Design settled both platforms |
| 712.5 | Calibrate centering + continuous j5 | Planning | **READY** | med | needs-a-call | Named call: authorize the `Homing_Offset` EEPROM write on j5. Motion's charter requires explicit consent. j5 cannot be calibrated at all today |
| 712.11 | Batch bench runs | Development | **PARKED** | med | needs-a-call | Code merged (0af16df), 7/11 checked, stopped 07-28. Derailed by two things: an unattended-operation authorization only Kyle can give, and a summary item depending on 715.2, which never ran. That authorization should not gate this plan |
| 712.13 | Gate fidelity under load | Planning | PLANNING | high | needs-a-call | Open Q: cap the profile / model lag in the twin / widen the margin. The tradeoff is cycle time vs fidelity vs reachable set — genuinely Kyle's. Safety-relevant: the arm passes through configurations the gate never checked |
| 712.14 | Trace records a cal PATH | Planning | **READY** | med | contained | Cleanest READY on the board — precise fix shape, 3 items, hours of work |
| 713.4 | Vision checkpoints | Planning | **READY** | high | contained | Stage 1 buildable today against recorded frames with the arm and cameras powered down. Enables "I can just sit here" |
| 713.7 | camserve ignores fps | Development | MISLABELLED | med | contained | → CodeReview/Completed. Fix verified live at `cammanager.py:461-467`. Held open by a pre-fix experiment the fix made impossible, serving a leak ticket (713.5) that closed 07-30. Drop the dead item |
| 713.8 | Intrinsics + hand-eye | Planning | **READY** | high | contained | THE missing link between seeing and moving; named as prerequisite by 612.3, 713.4, 713.3. Its self-declared "open question" is a schema-location coin flip the dev settles and records. Stage 1 needs no arm |
| 713.9 | Camera coverage | Ready | MISLABELLED | med | contained | 4 of 8 items done or overtaken by 716.4 / 713.11 / 716.5 and never swept — including the reach envelope, which 716.5 delivered. Live remainder is the occlusion test, which has never been done and is the only thing that justifies a 4th camera |
| 713.10 | Cheap detection: lock + downscale | Planning | **READY** | med | contained | Its only stated blocker — "sequence after 713.5" — closed 2026-07-30. Text never swept. Needed before two cameras can detect concurrently (713.4, 612.3) |
| 713.11 | Stabilise the camera setup | Planning | **READY** | high | needs-hands | Critical path. Gates 713.8 Stage 2, which gates everything downstream. Focus two barrels, tape-measure two poses, drop `planned: true`. ~1 bench hour |
| 714.4 | Fixtures in the gate | Planning | **READY** | high | needs-hands | The gate's world is 13 arm geoms and one ground plane; it clears paths straight through a part bay. 612.3 calls it "effectively a prerequisite". Machinery is buildable now; real fixtures are input Kyle supplies |
| 714.5 | Gravity + payload in sim | Planning | **DUPLICATE** | med | contained | Stage 1 (static torque via `qfrc_bias`) is the same computation as 716.6 item 1 — see finding 7. Recommend narrowing to Stages 2–3 + payload rather than cancelling; 716.6 owns the torque function |
| 714.6 | Twin's j1 is mirrored | CodeReview | MISLABELLED | high | needs-hands | → Completed. Merged (9ba1c6f), 6/7 done, held eight days by one bench check. Textbook `dont_gate_on_manual_validation`. The defect it fixed silently mirrored every lateral coordinate — IK, hand-eye, fixtures |
| 715.2 | j4 overhauls under gravity | Planning | **READY** | high | needs-hands | Safety. Arrives at 140°/s where 18°/s was commanded — ~60× the intended kinetic energy, and worse with a payload. Four investigation directions named, acceptance stated |
| 715.3 | Servo analog transients | Ready | **READY** | med | contained | Correctly labelled — one of only two Ready on the board. Three concrete experiments, script already drafted, mitigation already shipped |
| 716.3 | cell1 iGPU reservation | Backlog | **READY** | low | needs-hands | Fully researched down to the BIOS path. Deferred by Kyle. Rationale is now weaker than when written — the leak that motivated wanting the RAM (713.5) is fixed. Vendor warns it can break wake-on-LAN |
| 716.5 | Functional reach zone | Review | MISLABELLED | high | contained | → Development. Verified: `sim/twin.py:431-432` still builds the infinite plane, so the unchecked `Fix` item is genuinely outstanding. Review means dev is done; it is not. (Its own text also concedes six shipped checks that could not fail) |
| 716.6 | Static holding envelope | Planning | **READY** | high | needs-hands | Tied to a live incident — j2 hit 80% load and the arm fell on 07-31. The reach zone currently declares reachable a band the arm may not be able to hold. Misfiled under Cell; content is Sim per 714's charter |
| 716.7 | Recovering a fallen arm | Planning | **READY** | high | contained | The gate refuses every move *out* of a contact state, so recovery took five attempts and the only escape is disabling the gate entirely. Design constraint (not an override flag) is settled; the entry-point shape is a dev choice. Misfiled under Cell |
| 717.3 | Print pipeline → Bambu A1 | Planning | PLANNING | low | needs-a-call | Open Q: LAN Developer Mode yes/no, and `bambulabs_api` dependency authorization. **Phase A is independently READY and zero-dep** — clean fork candidate |
| 717.4 | Wrist camera mount | Backlog | **READY** | low | contained | Research complete, 14 concrete items, published `.step` identified. Deferred by Kyle ("seems like a side project") — correctly in Backlog. Most of the real work is twin geometry and re-deriving `HOLD_SAG_TOL_TICKS`, not CAD |
| 717.5 | Stand for the side camera | Development | MISLABELLED | med | needs-hands | → Review. The stand is printed *and bolted to the table* per `cameras.json`. Two bench checks remain and both are already on Kyle's 07-31 task list |
| 729 | Camserve as a standalone product | Planning | PLANNING | low | needs-a-call | Open Q: own Hive app vs a TendWright module — the ticket names it and defers to Kyle. Its three blockers are now 2/3 closed. Top-level with a module and no parent |
| 744 | cell1 as cattle | Planning | PLANNING | med | needs-a-call | Open Q: what the `spark` account may do unattended, and where the off-box audit lands. **Piece 1 is independently READY and is a live gap** — camserve is hand-launched with `nohup setsid` and does not survive a reboot. Top-level, no parent |
| 751 | JSON locale encoding | Planning | **READY** | med | contained | Exhaustively specified down to file:line, with the half-swept regression already recorded. Latent crash on Windows the moment a character outside cp1252 lands in a JSON file. Top-level with module `Sim`; belongs under 714 |

---

## Recommendations (not applied — Kyle rules, then we act)

Ordered by how much board-truth they buy per unit of effort.

1. **Close 714.6.** Merged, reviewed, one hands-on check outstanding. Convert
   the check to a bench-task item and mark the plan Completed.
2. **Close 713.7.** Delete the dead pre-fix experiment (its parent ticket closed
   without it), confirm the fps-matches-profile check, close.
3. **Move 716.5 back to Development.** It has outstanding `Fix` work, verified
   on disk.
4. **Move 717.5 to Review**, 612.3 to Planning.
5. **Sweep the text of 713.9, 713.10, 729 and `cell.json`** — all carry
   prerequisites that have since closed or been delivered elsewhere.
6. **Re-file 716.5, 716.6, 716.7 under 714**, and give 729 / 744 / 751 their
   parent epics.
7. **Draw the 714.5 ↔ 716.6 boundary** before either is picked up.
8. **Delete the 13 stale local branches and 6 remote ones** — all belong to
   Completed plans. **⚠ IRREVERSIBLE, AND THE ONLY ITEM IN THIS LIST THAT IS.**
   Remote branch deletion especially. This needs Kyle's separate explicit yes
   and must NOT be folded into a general approval of the rest — flagged by
   overwatch 2026-08-08. Everything else here is recoverable.
9. **Fork 717.3 Phase A** (zero-dep slicing) out from behind the LAN-mode gate,
   and **fork 744's provisioning script** out from behind the admin-account
   question — camserve not surviving a reboot is a live operational gap.

For #817, the two calibration findings that matter: **`needs-hands` deserves to
be a first-class containment value**, and **whole-ticket STALE misses the
staleness that actually accumulates**, which lives inside otherwise-healthy
tickets whose dependencies closed underneath them.

---

# APPLIED — 2026-08-08, same day

Kyle partially lifted the freeze: *"I think its fine to take a beat and have
everyone do the OBVIOUS ticket updates."* Recommendations 1–5 were applied;
6–9 were held back as roadmapping or irreversible.

| status | before | after |
|---|---|---|
| Planning | 28 | **17** |
| Ready | 2 | **14** |
| Review | 1 | 0 |
| Development | 4 | 2 |
| CodeReview | 1 | 3 |
| Backlog | 2 | 2 |

**Promoted to Ready — 12 of 12.** 712.4, 712.5, 712.14, 713.4, 713.8, 713.10,
713.11, 714.4, 715.2, 716.6, 716.7, 751. Each via Planning → Review → Ready
with `reviewAgent: spark`, and each carrying a shaping-log decision entry naming
this audit as its planning review with the specific reason it qualified.

**Status corrections — 3 clean, 2 partial.** 716.5 → Development (the demotion;
`sim/twin.py:431-432` re-verified as still infinite before demoting). 612.3 →
Planning. 717.5 → CodeReview. 714.6 and 713.7 did not reach Completed.

**Text sweeps — 7 items across 713.7, 713.9 ×4, 713.10, 729.** Text only, no
items checked, item ids preserved.

## Two corrections to this report's own recommendations

**1. "Review" was the wrong target for 717.5, and the state machine says why.**
`Development → Review` is refused. Review here is the *planning* review
(Planning → Review → Ready), not a code review — so it is never the right
landing spot for work that is past development. CodeReview is: delivered,
awaiting validation. Recommendation 4 above was wrong on this point.

**2. "Close 714.6" was not an obvious cleanup, and the platform was right to
refuse it.** `Cannot complete: 1 fix/validation items unchecked`. Closing it
would require either checking a validation nobody ran — asserting on the board
that `sim/ik.py` was proven against the real arm when it was not — or deleting
the item and destroying the record of what is owed. Both are decisions. The
same applies to 713.7, whose fps-matches-profile validation has genuinely never
been run.

The general form, which is the more useful finding: **the "further along than
its status" bucket looks obvious in an audit and is systematically not
applyable**, because the last thing between it and Completed is always a real
validation. That is `dont_gate_on_manual_validation` colliding with the
platform's own integrity gate, and the resolution — convert the item to a
bench-task entry, or accept the gate — is Kyle's. Both plans now carry a log
entry stating exactly what they owe.

## Declined deliberately

- **717.4 and 716.3** — verdict READY, left in Backlog. Kyle put them there
  himself. Promoting them would overwrite a priority decision with a shaping
  judgement; those are different facts.
- **713.9 item be45020d** — annotated as delivered by 716.5 but left unchecked,
  so the delivery is credited to the plan that did it.
- **Recommendations 6–9** — re-parenting, the 714.5 ↔ 716.6 boundary, the fork
  candidates, and the branch deletions. All untouched. No `assignedAgent` set
  anywhere in this pass.
- **612.3's checklist** — its items are implementation tasks where 612's own
  rule says a rung carries acceptance criteria. Rewriting them is shaping.
