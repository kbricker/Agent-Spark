# GarageBox 3.5" drive caddy — Dell OptiPlex 7070 SFF

Printed caddy for the surveillance drive in the camera host. Plan 951.2.

## Files

- `garagebox-caddy.stl` — **the part to print**. PETG, tree supports, prints flat.
  Wall loops 4, nozzle at the top of the PETG range, reduced part cooling: the two
  tall latch arms print as thin vertical blades and layer adhesion across the flex
  direction is what stops them snapping.
- `source-5050-SFF-Drive-Caddy-V3.stl` — unmodified input. Maladaptive,
  [Printables 454705](https://www.printables.com/model/454705-dell-sff-drive-caddy),
  **OptiPlex 5050 SFF version**. Not the 3080 version in that listing, which does not fit.
- `build-caddy.py` — regenerates the part from the source. Headless Blender:
  `blender -b --python build-caddy.py -- source-5050-SFF-Drive-Caddy-V3.stl garagebox-caddy.stl`
- `measure_rays.py` — axis-aligned ray caster used to verify the result. trimesh's own
  needs `rtree`, which is not installed and was not added.

## Why the 5050 version

Dell's OEM 3.5" SFF caddy is one part across the 40/50/60/70 range — **H8V8K**
(= 0CW33 / T3420 / 1B5146200-600), listed by multiple sellers for 3040 through 7070 SFF
plus the Precision T3420. The 5050 and the 7070 take the identical caddy. The 80-series
is where Dell changed the mount, which is why the author needed a separate 3080 model.

## What the build changes

Four tab members moved, four holes opened. Nothing else.

| | from | to |
|---|---|---|
| left tab members | x 1.00–3.00 | 2.00–4.00 (1.0 mm inboard) |
| right tab members | x 105.50–107.50 | 108.00–110.00 (2.5 mm outboard) |
| screw holes | Ø4.25 | Ø5.00 |
| gap between tabs | 102.50 | 104.00 mm |

Drive is a SkyHawk ST4000VX016, **101.85 × 146.99 × 20.20 mm**, so 1.08 mm per side.
The left move buys 1.00 mm of outboard room for the screw head, where stock had none.
Holes at 5.00 clear the 4.53 mm screw shoulder by 0.47 mm — dremel if they want more.

## Two things that will bite anyone editing this

**Tab members are much wider in Y than the holes suggest.** The ramps flare outward as
they sweep down to the floor. Real footprints at z=2.6: left **Y 19.2–64.5** and
**120.8–147.5**, right **Y 59.5–87.5** and **121.2–145.5** — up to 45 mm, not the ~18 mm
the boss looks like. Move whole members and put every patch boundary in a natural Y gap,
or you slice the ramps and leave steps mid-structure.

**Measure by true section, not by sampling vertices.** The floor plate's triangles are
large enough that vertex sampling misses material entirely — that error produced a wrong
reading of the right tabs' clearance and sent two builds down the wrong path.

## The tray, as measured

- Envelope 124.50 × 147.75 × 31.75 mm. That width occurs only around Y 30–45 where a
  left flange and a latch arm coincide; the main body is **112.50 mm** (x 1.00 to 113.50).
- **Asymmetric.** Left edge x=1.00 with tabs at 1.50 → 0.50 mm outboard. Right edge
  x=113.50 with tabs at 107.50 → 6.00 mm outboard. All the slack is on the right.
- Four holes at Z=8.50: left Y 32.25 and 133.75, right Y 73.75 and 133.75. Spacings
  41.5 and 60.0 mm are SFF-8301, and Z=8.50 over a 2.00 mm floor puts the drive's
  6.35 mm side-hole height right. The source model is correctly built to spec.
- **Shared member:** the left member carrying the Y=32.25 hole also carries the cage rail
  reaching x=−4.00 at Y 46–54. One piece, so the rail moves with it and now reaches
  −3.00, keeping ~4.5 mm of its 5.5 mm engagement. The caddy's overall −4.00 edge is
  unchanged — the other rail at Y 90–96 belongs to no tab member and is untouched.

## Verified

Watertight, 0 open edges, one connected body. Envelope −4.00…120.50 in X, identical to
the source. Floor-level structure extents identical to the source on both sides, so
nothing was cut. Holes measure 4.95. Honeycomb, floor and both latch arms untouched.

**Not yet printed.** Physical fit in the cage, and against the real screws, is open.
