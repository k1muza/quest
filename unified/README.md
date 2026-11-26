# Kingdom Quest — canonical unified interactive board

Open **`kingdom-quest.html`** in a modern browser. No internet, server, WebGL, or external library is required. Press **O** for operator controls; **C** for clean map; **F** for fullscreen; **R** to reset camera. Scroll and drag to inspect landmarks. The `environment/` and `gameplay/` editions remain historical references; this is the canonical implementation for future state integrations.

## Build and validation

From the repository root: `pip install -r requirements.txt` then `python unified/build.py`. To regenerate the depth map from the exact KayKit environment triangles: `python unified/build.py --bake-depth`. To regenerate the original six pawn sprites: `python unified/build.py --bake-tokens`. `python unified/qa.py` tests the standalone bundle using Chromium (`CHROMIUM` can override its executable path); `python unified/record_demo.py` records actual browser frames, requiring ffmpeg. Before changing environment geometry, rebuild the historical environment using its instructions and regenerate the unified depth map as a pair. Avoid changing camera parameters without rebaking both background and pawn/depth assets.

## Structure

- `board.js`: public snapshot adapter, score mapping, route interpolation, independent dynamic layers, operator controls.
- `route.json`: derived world-space and projected route, regional distances, visible water glint positions. Source remains `../environment/map.json`, `layout.json` and `environment.json`.
- `assets/`: packed per-pixel scene depth plus original faceted pawn sprites and pawn-relative depth.
- `build.py`, `bake_tokens.py`: deterministic offline bundle pipeline. `../environment/render_world.py` supports optional depth-only export, without altering the approved background.
- `index.html`, `style.css`, `data.js`: modular browser entry and generated offline assets.
- `kingdom-quest.html`: complete standalone distribution.
- `qa.py`, `qa-results.json`, `surface-validation.json`: browser and geometry validation.
- `screenshots/`: full-resolution captures and optional short recording.
- `STATE-API.md`, `TECHNICAL-REPORT.md`, `ASSETS.md`: integration and build documentation.

## Game demonstration

Choose 2–6 teams, edit names and colours, choose stops and set the fixed score at the final stop while in the lobby. Start the session, select a team, award/deduct points or set a direct score, undo the last scoring operation, advance team/round, run or pause the timer and explicitly trigger final results. A team reaching the decorative courtyard is not automatically the winner. Score remains authoritative even outside route capacity. The external state adapter uses the same state reducer as the controls. No networking or Flutter changes are included.
