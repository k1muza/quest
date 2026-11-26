# Kingdom Quest — Environment & Art Direction Refinement

## Scope and outcome
The original 158-cell KayKit map, 35-cell primary road, secondary road network, asset licence, and gameplay route generation are retained. This edition opens in permanent environment-only presentation. No repository or Flutter changes were made. The render is a new whole-scene bake of actual KayKit meshes, not an AI illustration or a collection of flat proxy buildings.

## Geography
- The terrain is a continuous heightfield sampled every four world units. Genuine KayKit tile top triangles are subdivided and displaced onto this common field; internal tile side faces are omitted. Road and river port geometry and orientations are retained. The heightfield is declarative in `environment.json` and included in the offline browser bundle.
- The Crownspine ridge consists of connected relief, asymmetrical peaks, exposed rock faces, lower forested foothills, and a pass following the original road. KayKit rock models add detail; stacked hexagonal mountain assets are not used for the main ridge.
- Heightfield range: 4.0–266.63 world units. The sampled primary terrain route ranges from 4.17–100.96 world units; the royal gate sits at 75.85. These are relative model units, not surveyed metres.
- The route profile was constrained and smoothed, then blended into adjacent terrain. Final sampled maximum terrain grade is 29.11% and 95th percentile 26.61%. This is suitable as stylised board-game terrain, not a civil-engineering road standard. The stone bridge is placed on a level riverbed at its original orientation. The existing sampled bridge deck profile is included in route projection and arc length.
- Coastline has a rounded outer sand apron and shallow water band, two open river mouths, coastal rocks, two small timber jetties and original low-poly boats. The underlying coastline still retains visible hex geometry.

## Architecture and composition
- Village and township buildings now follow regular street frontage bands, with civic sites and plazas reserved before residences and vegetation. Village market and well are located in the bends of the local road; township includes a well court, church, market, tavern and blacksmith. Houses retain genuine KayKit mesh detail.
- Farm plots use aligned rectangular furrows, contrasting crop colours and actual KayKit grain models. A windmill and adjacent storage detail reinforce the agricultural district.
- Forest density is intentionally concentrated in the west; 552 trees are placed with varying scale and rotation, road and river clearances, clearings and sparse mountain vegetation.
- Citadel sits on a raised plateau, retains its connected perimeter and original gate alignment, and contains a royal keep, two smaller buildings, garden beds, trees, well and paved final approach. It is less empty than before, though further architectural refinement would be valuable.
- The final scene includes 714 KayKit mesh placements (excluding the terrain tile instances), and approximately 564,849 rendered triangles including terrain subdivision and supplemental geometry. The raw asset collection is retained with original CC0 licence in `assets/License.txt`; local rendering uses a subset of the original assets.

## Rendering and camera
The offline Python renderer reads actual glTF mesh positions and palette texture samples, constructs scene geometry, and uses one global depth buffer and light-space shadow map. Nine shadow-depth samples provide soft-edged cast shadows. The image is rendered at 1.5x 1080p and downsampled with Lanczos. A richer water gradient and region-specific ground colours support visual hierarchy. No live WebGL requirement was introduced.

Three camera/lighting alternatives were rendered. Camera 1 (selected): 49.46-degree elevation above the horizontal, warm front-left sunlight. Camera 2: 42.84-degree elevation, lower and more dramatic back/side lighting but more road occlusion. Camera 3: 57.14-degree elevation, higher overview with brighter, less dramatic light. The selected camera is lower than the original 56.10-degree camera, balancing depth and route visibility. All share the same world geometry.

## Validation and performance
Final test: headless Chromium, 1920x1080, device scale 1, self-contained HTML. No page errors, no HTTP(S) network requests, HUD and footer hidden. 180 measured frames: median and 95th percentile 16.70 ms; average 60.00 FPS. This measures the 2.5D browser runtime, not offline mesh-bake speed or actual Smart TV performance.

| Hidden route configuration | Result | Minimum projected spacing |
| --- | --- | --- |
| 30 | Pass | 70 px |
| 40 | Pass | 59 px |
| 50 | Pass | 46 px |
| 60 | Pass | 40 px |

Primary route arc length after elevation projection: 3,071 world units. Browser validation includes grid uniqueness, reciprocal road and river connections, model orientation, gate alignment and generated stop spacing. Elevation sampling is documented in `elevation-validation.json`. Stop markers and teams are intentionally never rendered in this edition. The route is retained for future integration; movement animation was not a priority and was not revalidated in this environment-only pass.

## Limitations / artistic assessment
- This is a meaningful improvement over the flat baseline, not a certified 9/10 finished game environment. The coast remains recognisably modular, certain buildings remain repetitive, and the ridge's rocky forms are still stylised. The riverbanks and harbour would benefit from bespoke curved bank meshes, more natural coastal cliffs, varied docks and more intentional water materials.
- The global scene is baked from 3D geometry into a 1080p image; browser zoom uses the baked image, so close-up screenshots are 1080p viewport captures but cannot add new mesh detail. Camera alternatives are separate bakes, not live orbit modes. Water, flags and windmills are static in this revision.
- Collision checks for props use clearance radii, not exhaustive mesh intersection tests. The scene was visually inspected; no claim of complete absence of all tiny intersections or seams is made. The highest slopes are a design compromise for the visible mountain pass. No TV browser was tested.
- Final runtime HTML is 1,663,910 bytes, about 1.66 MB decimal. It contains its image and heightfield, route data, JavaScript and CSS. No external runtime dependencies. Raw source glTF assets are about 2.1 MB on disk; the larger project archive includes the full set of 1080p screenshots and intermediate renders.

## Reproduce
Open `kingdom-quest-environment.html` directly in a browser. Drag to pan, scroll to zoom, R/Esc to reset, F for fullscreen. To rebuild the bake, install Python dependencies listed in README, then run `python render_world.py`, followed by `python bundle.py`. To rerun browser QA run `python qa_environment.py` with Chromium and Playwright available.
