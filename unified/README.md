# Kingdom Quest — canonical unified interactive board

Open **`kingdom-quest.html`** in a modern browser. No internet, server, WebGL, or external library is required. Press **O** for operator controls; **C** for clean map; **F** for fullscreen; **R** to reset camera. Scroll and drag to inspect landmarks. The `environment/` and `gameplay/` editions remain historical references; this is the canonical implementation for future state integrations.

## Build and validation

From the repository root: `pip install -r requirements.txt` then `python unified/build.py`. To regenerate the depth map from the exact KayKit environment triangles: `python unified/build.py --bake-depth`. Floating medallions are drawn by `floating-markers.js`; the legacy pawn assets are retained only as historical references. `python unified/qa.py` tests the standalone bundle using Chromium (`CHROMIUM` can override its executable path); `python unified/record_demo.py` records actual browser frames, requiring ffmpeg. Before changing environment geometry, rebuild the historical environment using its instructions and regenerate the unified depth map as a pair. Avoid changing camera parameters without rebaking both background and background and scene depth assets.

## Structure

- `board.js`: public snapshot adapter, score mapping, route interpolation, independent dynamic layers, operator controls.
- `route.json`: derived world-space and projected route, regional distances, visible water glint positions. Source remains `../environment/map.json`, `layout.json` and `environment.json`.
- `floating-markers.js`: map-independent floating, bouncing team medallions and shared-anchor clustering.
- `assets/`: packed per-pixel scene depth; legacy pawn assets are not loaded by the runtime.
- `build.py`: deterministic offline bundle pipeline. `../environment/render_world.py` supports optional depth-only export, to keep depth synchronized with the corrected background.
- `index.html`, `style.css`, `data.js`: modular browser entry and generated offline assets.
- `kingdom-quest.html`: complete standalone distribution.
- `qa.py`, `qa-results.json`, `surface-validation.json`: browser and geometry validation.
- `screenshots/`: full-resolution captures and optional short recording.
- `STATE-API.md`, `TECHNICAL-REPORT.md`, `ASSETS.md`: integration and build documentation.

## Game demonstration

Choose 2–6 teams, edit names and colours, choose stops and set the fixed score at the final stop while in the lobby. Start the session, select a team, award/deduct points or set a direct score, undo the last scoring operation, advance team/round, run or pause the timer and explicitly trigger final results. A team reaching the decorative courtyard is not automatically the winner. Score remains authoritative even outside route capacity. The external state adapter uses the same state reducer as the controls. No networking or Flutter changes are included.

## Targeted visual corrections
Rebuild with `(cd environment && python render_world.py --one)` followed by `python unified/build.py --bake-depth`. Verify agricultural polygons with `python environment/validate_farm.py`. See [implementation report](VISUAL-CORRECTIONS.md).
