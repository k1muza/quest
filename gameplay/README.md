# Kingdom Quest — KayKit edition

A standalone 1080p spectator adventure board. No Game Night repository, Flutter app, pairing, networking or existing game rules are modified.

## Run

Open `kingdom-quest-kaykit.html` in a desktop browser. Everything required for this build (JavaScript, CSS, artwork) is embedded. There are no external network requests or CDN dependencies. For the modular source version, run `python -m http.server 8000` from this directory and open `http://localhost:8000/`. `index.html` uses the local JavaScript files.

Use **Controls** to select 2–6 teams, 30/40/50/60 stops, the active team, movement (+1/+3/+5/−1), direct position, undo, tie, rapid movement, reset, milestone and winner. The panel also contains rendering quality, ambient effect and debug controls and separate marker/piece visibility. Drag to pan; wheel or buttons to zoom; reset camera restores the overview. Clean map hides spectator UI and gameplay; press Esc or hover the lower-right return area to restore. Space advances the active team when the document has focus. Full screen requires a browser that supports its Fullscreen API.

## Source architecture

- `map.json`: editable world definition (odd-row coordinates, regional ranges, route/river/secondary road cells, team colours).
- `map.js`: generated runtime map definition.
- `inspect_ports.py`: reads KayKit glTF meshes and texture-atlas UVs, identifies road/water face polygons and discovers edge ports.
- `build_layout.py`: matches connection signatures, selects 60-degree rotations, computes local traversable paths, bridge deck elevation and gate alignment. Generates `layout.json` and `layout.js`.
- `render_assets.py`: bakes selected model meshes into depth-tested orthographic sprites. Generates `assets.js` and `asset-audit.json`.
- `engine.js`: terrain and region composition, cached artwork renderer, arc-length sampling, team state and animation, camera and control handlers.
- `style.css`, `index.html`: spectator presentation and demo controls.
- `bundle.py`: creates the self-contained HTML from the source.
- `validate_surfaces.py`, `qa.py`: geometry validation and headless browser QA.
- `assets/`: original source models and atlas obtained from the supplied KayKit folder; original licence included. These are build inputs, not network dependencies or a mandatory runtime asset download.
- `screenshots/`: actual 1920×1080 renders, including the two intermediate visual passes.

## Rebuild

Use Python 3 with numpy, Pillow, trimesh, shapely, scipy, scikit-image and numba installed. Run from this directory:

```sh
python build_layout.py
python validate_surfaces.py
python render_assets.py
python bundle.py
```

The supplied HTML works without these packages. Browser QA additionally uses Python Playwright and Chromium; adjust the executable path in `qa.py` if needed. `qa.py` loads the exact bundled HTML into Chromium, so it also works in environments that prohibit file/localhost navigation. The project is deliberately fixed-camera 2.5D rather than a full interactive 3D WebGL renderer.

## Licence

KayKit Medieval Hexagon Pack 1.0, by Kay Lousberg (https://www.kaylousberg.com/), CC0. See `assets/License.txt` for the original unmodified licence. Source: https://kaylousberg.itch.io/kaykit-medieval-hexagon and the supplied Google Drive copy. Original game code and UI are separate from the asset collection.
