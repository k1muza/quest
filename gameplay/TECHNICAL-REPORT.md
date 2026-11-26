# Technical report — Kingdom Quest KayKit edition

## Implementation

- 158 land terrain modules, irregular island perimeter; 35-cell primary route plus connected secondary streets and 13 river cells.
- 50 original glTF models inspected; 42 selected model types and 79 model/rotation sprites baked, including original terrain, roads, rivers, bridge, walls, castle, buildings, woodland, rock and farming assets. No substitute geometric houses, mountains, road tiles or bridge in the delivered default rendering. The ocean backdrop, paving accents, pawn graphics, gate recess and courtyard surface are original 2D presentation elements.
- Actual model terrain dimensions: X −1 to +1, Z −1.1547 to +1.1547, origin at top plane Y=0, base thickness 1 model unit; pointy-top offset grid. Terrain sprite base thickness visually compressed to 48% for miniature presentation. 60° rotations are calculated from model port signatures. Original UV atlas retained, with a warmer colour grade and diffuse directional illumination.
- Road and water footprints are derived from the model's UV-coloured top triangles. Each required connection set matches a real model/rotation; reciprocal edges are checked. A raster geodesic biased toward the middle of the traversable polygons is smoothed and transformed into world-plane points. The bridge crossing uses `hex_river_crossing_B` rotated 120° and `building_bridge_A` rotated 60°. The bridge deck centre height of +0.20 model units is measured by vertical mesh intersection and used by movement. Gate centre is aligned to the measured intersection of the primary route and the southern perimeter; the finish is in the courtyard.
- Stop placement samples cumulative path length in unprojected terrain-plane units, including bridge height. The same map supports changing the stop count without rebuilding terrain. Pairwise stop separation is checked and excessive density is rejected. Teams retain normalized progress when count changes; rapid commands replace the previous target rather than creating an unbounded queue. Motion uses smoothstep interpolation plus visual hopping, with forward/backward movement using the same route.
- Sprite rendering uses a software depth buffer at build time. The runtime uses a cached Canvas 2D environment and small animated overlays; no WebGL dependency. This is a deliberate fixed-view rendering strategy for TV compatibility; zoom and pan inspect the same projected world, not a freely orbitable 3D scene.

## Measured validation

1920×1080, headless Chromium, DPR 1. All 4 supported counts passed browser validation. Minimum pairwise marker gaps are 59 / 49 / 43 / 37 px for 30 / 40 / 50 / 60 stops respectively. Browser tests reported no JavaScript page errors. The rapid forward/backward command sequence reconciled exactly to its last target. Controls exercised: team count, +5, undo, 60 stops, reject 500 stops. 6-team tied bridge screenshot is included.

Independent mesh-footprint verification sampled 3,956 road and 941 river positions across 72 paths (one bridge path handled separately). Zero samples exceeded the 0.025-model-unit tolerance. Maximum outside distance was 0.001805 model units. These are checks of the road/river surface centrelines, not a full collision simulation of every decorative mesh. The bridge deck was sampled independently at 41 longitudinal positions.

A recent 180-frame Chromium sample measured about 60 FPS, median frame interval 16.7 ms, p95 16.8 ms. This is a laboratory frame-cadence measurement, not a benchmark on a Smart TV. See `qa-results.json` and `surface-validation.json` for raw measurements.

## Visual refinements

1. Genuine KayKit terrain and architecture, forest coverage, river/road composition (initial bespoke path rendering; screenshot `pass-1.png`).
2. Replaced the bespoke primary road and river strokes with actual matched KayKit terrain modules; corrected river outlets, connected roads, gate alignment, bridge profile and town orientation (`pass-2.png`).
3. Deliberately composed north mountain ridge and wooded spur, region-specific colour treatment, farms and decorative props, expanded readable markers, tied-team formation, gate recess, clean-map presentation and debug controls (final screenshots 01–12).

## Limitations and TV considerations

The assets have a deliberately chunky low-poly look; the result should be evaluated from the supplied screenshots rather than assigned a speculative 9/10 rating. This is not a live 3D scene: no orbit camera, physically simulated lighting, real-time occlusion between independently drawn tokens and scenery, or full 3D collision detection. Decorative prop placement uses route/river and separation checks; there is no full mesh-to-mesh collision audit. Some overlap can occur when several pawns occupy one small location. Lighting and shadows are baked or stylized; animated water glints are lightweight, and windmill geometry is static. Coasts use an irregular land-tile silhouette above a stylized ocean rather than a full ring of dedicated coastline/water meshes. A viewer can pan/zoom, reset camera, and hide gameplay, but cannot change camera tilt. The map definition and placement recipes can be edited and rebuilt; there is no full editor or procedural generator.

Actual Smart TV hardware/browser testing, browser storage constraints, input/remote control mappings and long-session performance are unverified. The HTML avoids external dependencies and WebGL and offers 3 rendering resolutions, making it a practical starting point. Older TV browsers may need JS transpilation (e.g. optional chaining, Array.at, and other modern features) and a remote-specific control surface. A future live Three.js version could reuse the map layout and model-origin metadata; the existing 2.5D build is already a lightweight fallback.
