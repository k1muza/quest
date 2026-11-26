# Cinematic 2.5D rendering — experimental report

Baseline: `6622636b30f7434392a275ba7bab9bfaf9490086`. This laboratory adds a separate build, not a replacement for the unified board. No map redesign, transport, Flutter or mandatory WebGL. All imagery is rendered from the existing KayKit-derived scene (564,849 triangles, 714 placements). The camera is orthographic; the 1920×1080 logical board remains the coordinate system. All 1,932 sampled route points retain their world-space coordinates, distance and elevation.

## Experimental decisions

| Experiment | Hypothesis / implemented evidence | Cost and decision |
|---|---|---|
| A Offline rendering | Reuse the Python mesh generator; linear-light hemisphere and directional illumination, projected shadow raster, water specular response, depth-neighborhood shading. Six genuine lighting bakes. Blender executable/module absent; programmatic mesh export and Blender import script supplied but not run. | Native 4K golden render 3.78 s after geometry generation; other 1080p lighting bakes 0.86–1.06 s. Adopt reproducible CPU renderer; compare Cycles/Eevee on a suitable workstation before replacing it. No claim of GI or path tracing. |
| B Materials / atmosphere | Sky and sun contribution changes the apparent canopy, stone and roof colors; water specular term; depth-based contact shading and distant haze. See comparison and closeups. | No additional per-frame shading. Existing palette preserved. Not physically based texture/material reconstruction; no modeled windows or reflections. Refine art direction and textures offline. |
| C Resolution | Render 3840×2160 directly; downsample to 2560×1440 and 1920×1080; compare three encodings. | See measured table below. 1440p is the best default for TV experiments. 4K optional; 8K not tested (126.56 MiB for one RGBA image alone). Regional tiles and pyramids deferred pending real-device budget. |
| D Camera | Smoothstep zoom/pan, follow active team, landmark framing, return to overview, event triggers, explicit victory framing at winner's real target. | CSS transform, no new scene redraw; ordinary scoring can leave cinema disabled. Adopt with automatic events off by default. |
| E Alternate cameras | Independently rasterized bridge and citadel views, exact projection, independent depth and pawn sprites, world-to-screen reprojection; fade through dark when switching. | Measured 238–240 ms end-to-end switch. 2.31–2.50 s offline bake at 2880×1620 each. Adopt optional cuts; no fake rotation/cross-camera interpolation. Views are altered elevation angles rather than street-level perspectives. |
| F Depth effects | Bake subtle contact and depth fog only over valid scene pixels. | No full-screen per-frame CPU cost. Approximate screen-space shading, not true AO/GI. Adopt subtle depth cues; leave DOF optional (markers must be readable). |
| G Parallax | Consider separated depth layers and disocclusion. | Not implemented: sliding original pixels would detach the road, scenery and depth. Reject naive parallax; investigate layered depth images only with a complete background/occlusion treatment. |
| H Living environment | Reuse animated water highlights; regenerate color-derived safe glint anchors for each alternate camera. | Small Canvas path strokes; off in Standard. Windmills, boats, flags and chimney smoke not implemented; need isolated model parts and static-component removal. |
| I Lighting | Day, morning, golden hour, dusk, night, ceremony use different illumination vectors, sky/sun channels and exposure, not simple blue tint overlays. | Optional same-projection cuts; larger distribution. No emissive windows, torches or lightmaps. Pawns retain original lighting (per-camera projection is correct, not per-light matching); night is a research preset, not a production look. |
| J Pawns | Re-bake camera-specific existing faceted pawn mesh/depth, retain shadows, elevation-aware hopping and per-pixel masking. | 14 small PNGs for two extra viewpoints; no new game semantics. Not a new premium mesh or higher-res pawn set. Zoom exposes low logical overlay resolution. |
| K Sequence | Follow on score award, point label, return, turn handover, winning pawn framing and presentation; recorded actual browser demonstration. | 11.25 s, 8 fps recording (capture format, not runtime FPS). Sequence button awards 7 demo points; automated transitions optional; independent landmark cuts available. Fully automatic bridge-crossing cut and introduction not implemented. |

## Performance measurements

Desktop headless Chromium 144.0.7559.96. 240 frame intervals per profile; 2 teams at 720p, 6 at 1080p and 4K. These are mixed animation/settled frame intervals, not physical TV results. 4K p95 shows significant tail stutter; do not infer sustained 60 fps from the median. No controlled GPU/CPU utilization measurement. JavaScript heap is not total decoded image, canvas or compositor memory.

| Profile | Viewport | Background | Median | p95 | JS heap estimate | Profile switch |
|---|---|---|---|---|---|---|
| Standard | 1280×720 | 1920×1080 baseline | 16.7 ms | 16.7 ms | 24.5 MB | 70 ms |
| Enhanced | 1920×1080 | 2560×1440 relit JPEG | 16.7 ms | 16.8 ms | 24.5 MB | 123 ms |
| Cinematic | 3840×2160 | 3840×2160 WebP | 16.7 ms | 83.4 ms | 24.5 MB | 115 ms |

Initial baseline asset load inside page: 167.6 ms on cinematic QA run; entire set_content to enhanced-ready 2179 ms including browser protocol transfer, parsing and image decode. Full lab HTML 11,998,851 bytes vs reported 1.98 MB baseline (~6.1×), not a recommended TV distribution. Standard profile reduces active rendering work, **not** the size of this all-in-one file. For production, use existing baseline on constrained devices and build per-profile packs, retaining optional images separately. Decode only active view, use budgeted eviction; current prototype leaves caching to browser. Two 1920×1080 RGBA canvases alone require ~15.82 MiB plus depth arrays, temporary canvas, sprites, textures and compositor buffers. Peak total memory was not measured; a 4K RGBA background adds 31.64 MiB, and browser compositing may allocate additional 4K surfaces.

First `Image.decode()` timings include data URI parsing and cache behavior, not network; repeated timings in cinematic-qa.json show caching. Images are identical art at each resolution. JPEG/WebP quality 90, PNG lossless.

| Image | JPEG bytes / ms | WebP bytes / ms | PNG bytes / ms | RGBA MiB |
|---|---:|---:|---:|---:|
| 1080p | 319,476 / 22.5 | 221,054 / 62.3 | 1,527,435 / 124.6 | 7.91 |
| 1440p | 500,852 / 46.0 | 338,108 / 49.6 | 2,554,801 / 70.6 | 14.06 |
| 4K | 1,069,303 / 71.7 | 782,318 / 90.2 | 4,179,082 / 135.4 | 31.64 |

WebP reduces background distribution by 27–32% vs JPEG in this test; JPEG remains useful for compatibility and decode latency. Keep scene/pawn depth lossless. No measured TV decoder compatibility. Adaptive quality is not implemented; manually select a profile.

## Validation and visual evidence

41/41 original browser regression checks and 20/20 added cinematic checks passed. Alternate-camera world projection error 0 in the JS arithmetic test; all 1,932 projected route samples lie on valid scene-depth pixels in all three views. This verifies registration/math, not pixel-perfect correctness of all occlusion boundaries. Base tests showed depth masking clipped 210 pixels versus zero with masking disabled. Visual bridge and citadel screenshots inspected; pawns retain route alignment; marker fallback badges remain visible. State, rapid-scoring reconciliation, timer, stop counts, negative/overflow scores and explicit winner semantics preserved. No browser errors or external HTTP requests. Recorded demonstration captures real browser output; not a conceptual animation. Detailed evidence in `qa-results.json`, `cinematic-qa.json`, `bake-results.json` and gallery. Performance samples were collected on desktop headless Chromium; processes shared the lab machine, so isolate future tests before drawing hardware conclusions.

## Production recommendation

Keep the canonical unified engine and add a presentation-only camera director. Adopt per-map orthographic art and matching depth at 1440p, fixed 1080 logical route space, event-driven smooth camera zoom and cuts to a small number of independently rendered cameras. Prefer daytime/golden look over dark variants for spectator readability. Preserve optional 4K and lighting packs, not a mandatory 12 MB bundle. Don't adopt arbitrary background parallax, expensive dynamic postprocessing or compulsory WebGL. Higher resolution is visibly sharper but doesn't add geometric detail: the low-poly asset style remains the limiting factor. For a professional strategy-game finish, the next highest-value offline work is material/texturing, separated windmill and flag animations, lighting-consistent pawn assets, and local hero viewpoints with careful composition. Do not claim parity with modern 3D titles or assign a numeric visual rating without independent review.

## Map-production contract (proposal, not a new map implementation)

Keep declarative geometry and world route separate from presentation. For each map package: `mapId`, mesh generator and source asset provenance; world route `[distance,x,y,z]`; landmark distances; main and alternate camera definitions (`cos`, `sin`, offset, viewport, world origin); background URI per quality/light; lossless scene depth and pawn sprite/depth sets per projection; visible animation anchors; optional effect masks and foreground layers. Scene depth encodes projected depth as unsigned RG16 with zero invalid, valid depth `(R*256+G-1)/32-128`. All cameras share the route distances, scores and IDs. Build regenerates screen coordinates from camera metadata. Current lab is still Quest-specific: bridge/citadel buttons and render offsets are fixed; generalize into data-driven manifests before adding three more maps. No additional maps implemented.

## References / relevance

- [MDN: Optimizing canvas](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Optimizing_canvas) — layered static/dynamic rendering, pre-rendering repeated primitives. Quest uses separate background, markers and motion layers.
- [Blender: render passes](https://docs.blender.org/manual/en/dev/render/layers/passes.html) — depth and other passes for offline compositing; a future Blender path should export registered depth and color together.
- [Shade et al., Layered Depth Images](https://dash.harvard.edu/entities/publication/73120378-7e84-6bd4-e053-0100007fdf3b) — multiple samples per viewing ray address disocclusion in view synthesis. Supports rejecting naive sliding layers where hidden pixels are missing.
