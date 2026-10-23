# Space Org Web Games & Sims — Reference + Teardowns

Research doc (July 2026). Catalog of official public-facing games/simulators from space agencies
and companies, plus tech teardowns of the notable ones. Gathered for inspiration for Spark
projects (Orbital et al.) — the niche of beautiful, physics-flavored, zero-dependency browser
sims is surprisingly uncrowded.

## Catalog

### SpaceX (2 — that's all of them)

| Title | URL | Year | Stack (verified) |
|---|---|---|---|
| ISS Docking Simulator | https://iss-sim.spacex.com/ | 2020 | Three.js r112 + GSAP 3, S3 + Fastly |
| Starship: The Game | https://starshipthegame.spacex.com/ | 2024 | Phaser 3 + GSAP, Azure Front Door |

### NASA

- **NASA's Eyes suite** — https://science.nasa.gov/eyes/ — real-time 3D web apps (Solar System,
  Asteroids, Earth, Exoplanets). Custom JPL "Pioneer" WebGL engine. Teardown below.
- **CODing Sim** (Crew Orbital Docking Simulation) — fly Crew Dragon *and* Starliner to the ISS,
  manual docking mode. NASA's counterpart to iss-sim.
  https://www.nasa.gov/stem-content/crew-orbital-docking-simulation-coding-sim/
- **Roman Space Observer** — official 8-bit arcade game. https://roman.gsfc.nasa.gov/game.html
- **Moonbase Alpha** — 2010 Unreal Engine co-op lunar repair game on Steam.
- **Games & Interactives hub** — https://www.nasa.gov/interactives/ — Exoplanet Travel Bureau,
  Solar System Treks (trek.nasa.gov), Hubble games, Climate Time Machine, Rocket Builder,
  Space Place kids' games.
- **The Lost Universe** — official tabletop RPG adventure (PDF).

### ESA

- **The Space Game** — HTML5 interplanetary trajectory design (gravity assists to Jupiter).
  https://www.esa.int/Education/Compete_and_find_your_way_to_Jupiter
- **ESA SHIELD** — planetary-defense tower defense on Steam (official outreach).
- **Mars Horizon** — commercial agency-management game, official ESA/UKSA partnership.
- **Paxi games** (kids) — https://paxigames.esa.int/ — and AIM: The Game (Hera mission).

### Everyone else

- **ULA**: RocketBuilder.com (Atlas V mission configurator); official KSP Vulcan-building challenge.
- **Boeing**: nothing public — Starliner VR trainer is internal; public docking experience is NASA's CODing Sim.
- **Blue Origin, Rocket Lab, Firefly, Sierra Space, Axiom, Lockheed, Northrop, Virgin Galactic**:
  no official public games/sims found (their simulators are astronaut/engineering trainers).
- **JAXA / Roscosmos / ISRO / CNSA**: nothing surfaced in English-language search.

---

## Teardown: SpaceX ISS Docking Simulator (iss-sim.spacex.com)

Shipped May 2020 for Demo-2, untouched since (`Last-Modified: 14 May 2020`). Static,
no-framework, no-build-pipeline WebGL page by designer Shane Mielke.

- **Three.js r112** as classic global `<script>` tags (no modules, no bundler). Helpers:
  `GLTFLoader`, `CSS2DRenderer` (floating ISS labels), `WebGL.js` detection.
- **GSAP 3** + paid Club plugins **DrawSVGPlugin** (HUD ring strokes) and **ScrambleTextPlugin**
  (sci-fi text flicker).
- **No framework/jQuery** — `$` in the bundle is a hand-rolled `getElementById` helper.
- **Custom GLSL** embedded in the HTML as `x-shader` tags: sprite-atlas shader for HUD sprites
  (`ForwardViewSprites.json/png`) and a per-vertex-alpha fog line shader for the docking-axis rings.
- **HUD is mostly SVG, not WebGL**: inline SVG worms/arrows animated by GSAP, `hud-darken.png`
  vignette, pre-rendered number sprite PNGs. Font: Lato (Google Fonts).
- **Sim logic** (one 63 KB hand-minified `threed.min.js`, readable globals like `createIss`,
  `checkCollision`): camera *is* Dragon — direct kinematics, no physics engine. Docking check =
  `THREE.Raycaster` against ISS meshes, `far` tightening 1 m → 0.1 m inside 0.5 m range;
  tolerances hard-coded `toleranceRotation = 0.2`, `toleranceRate = 0.004`.
- **Assets**: uncompressed glTF in `/3d/` — `iss.glb` 19.2 MB, `iss_mobile.glb` 9.5 MB,
  `tesla.glb` 1.35 MB (Starman Easter egg). Also `flat_earth.png` (settings toggle) and a full
  wormhole/warp sequence (`createWormhole`/`finishWarp`).
- **Zero analytics, zero third-party JS** (besides Google Fonts), no audio, no network after load.
- **Hosting**: S3-style origin (bare-MD5 ETag) behind **Fastly** (`Via: varnish`,
  `X-Served-By: cache-…`). Joke header `Server: whydoyoucare?`; HEAD requests get 204.

## Teardown: Starship: The Game (starshipthegame.spacex.com)

Oct 2024 (Flight 5 booster catch). Completely different build from iss-sim:

- **Phaser 3** game engine + GSAP (DrawSVG, Draggable, CustomEase) + webfontloader.
- ES modules this time (`js/scenes/{preloader,menu,game}Scene.js`) but still no bundler.
- Pixel UI in plain CSS divs; "Press Start 2P" Google Font.
- Hosted on **Azure** (blob storage ETag `0x8DC…`, `x-ms-*` headers, Azure Front Door CDN).

## Teardown: NASA's Eyes (eyes.nasa.gov) — where the data comes from

Front end is a tiny static HTML + `config.js` + four webpack bundles (`commons`, `preload`,
`vendors` 2.4 MB, `app` 1.7 MB). Only tracker: federal **DAP analytics** (digitalgov GA4).

- **Engine: "Pioneer"** — JPL's in-house WebGL engine, bundled inside `app.js` (160+ symbol hits;
  not Three.js, not Unity — the old desktop Eyes was Unity, the web rewrite is custom). PBR
  shading cites Unreal's SIGGRAPH 2013 notes. `vendors.js` is just UI libs (Swiper etc.).
  Font: Raleway.
- **The suspicion is right — it streams everything.** `config.js` declares three roots:
  - `staticAssetsUrl: eyes.nasa.gov/assets/static` — glTF models per body/spacecraft
    (Bennu, Ryugu, ʻOumuamua, Psyche…), star catalog `stars.<res>.bin`, skybox env maps.
  - `dynamicAssetsUrl: eyes.nasa.gov/assets/dynamic` — ephemeris + terrain (below).
  - `animdataUrl: eyes.nasa.gov/server/spice` — "SPICE server" (below).
- **Ephemeris, two mechanisms** (per-entity `controllers` in a giant scene config):
  1. `dynamo` — chunked **binary `.dyn` files** (`def.dyn` + named chunks, format versions 1–2,
     `orb` header) at `/assets/dynamic/dynamo/<body>/…`. Planets, moons, Lagrange points
     (e.g. `l1/def.dyn`, 3.8 KB, verified live).
  2. `animdata` — per-spacecraft `pos`/`ori` streams at
     `/server/spice/<sc_name>/<pos|ori>.animdef` (binary; verified `sc_apollo_15/pos.animdef`).
- **"server/spice" is not a live compute API.** Response headers say `Server: AmazonS3` via
  CloudFront, with `x-amz-meta-mtime` bake dates (Apollo 15's data was generated in 2011).
  Pipeline: JPL runs **NAIF SPICE kernels offline → bakes binary ephemeris chunks → S3 →
  CloudFront**, and the Pioneer client interpolates chunks against the wall clock. The "real-time"
  view is client-side interpolation of precomputed trajectories — no websockets, no EventSource;
  the `setInterval`s in the bundle are UI/session timers. Fresh mission data = re-bake + re-upload.
- **Terrain**: two tile sources — its own **CMTS** quadtree sets per planet
  (`/assets/dynamic/cmts/<body>/{color,height,normal,night,specular,cloud}`) and **NASA Trek**
  public WMTS servers (`trek.nasa.gov/tiles/…`) for the Mars Viking and Moon LRO global mosaics.
  (Direct tile probes 403 without the exact quadtree path format — bucket listing is denied.)
- Related public data services linked from the app: `ssd.jpl.nasa.gov` (Solar System Dynamics /
  Horizons) and `cneos.jpl.nasa.gov` (NEO close approaches) — the upstream sources for the
  asteroid/comet catalogs.

## Licensing: commercial use of the NASA data (verified July 2026)

- **NASA-produced content is U.S. public domain** (federal works can't be copyrighted);
  commercial use explicitly permitted. https://www.nasa.gov/nasa-brand-center/images-and-media/
- **SPICE kernels + NAIF toolkit: formally approved for commercial use**, no license/fees,
  TSPA export designation. https://naif.jpl.nasa.gov/naif/rules.html — this is the upstream
  source of Eyes' ephemeris. Horizons + CNEOS data likewise free.
- Caveats:
  1. NASA insignia/logotype/seal are statutorily protected (separate from copyright); no
     implied NASA endorsement in commercial use.
  2. Third-party content interleaved on NASA sites keeps its owner's copyright — ESA imagery
     is CC BY-SA (not PD); some instrument-team/contractor assets (incl. models of SpaceX
     vehicles) are copyrighted. Check provenance per asset, esp. Trek layers from
     international partners.
  3. Identifiable people in imagery carry privacy/publicity rights.
  4. Public-domain data ≠ public API: Eyes' baked `.dyn`/`.animdef` CDN is unsupported and
     undocumented. For a product, pull SPICE kernels from NAIF / query Horizons and bake your
     own chunks — same data, clean license story, format you control.

### Takeaway pattern

All three flagship sims are **static sites on a CDN with zero backend compute**. Even NASA's
"live" solar system is baked binary data streamed from S3 and interpolated client-side. The
engineering effort goes into the offline data pipeline (SPICE bakes, tile generation, model prep)
and a lean client engine — a pattern directly applicable to small deterministic-sim projects.
