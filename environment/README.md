# Kingdom Quest — environment-only edition

Open `kingdom-quest-environment.html` in Chrome, Edge, or another modern browser. Internet is not required. Drag to pan, scroll to zoom, R or Esc to reset, F to toggle fullscreen. No gameplay overlay or numbered stops is exposed in this edition.

## Files
- `map.json` / `map.js`: original map definition and road network.
- `layout.json` / `layout.js`: matched KayKit tile rotations and original route geometry.
- `environment.json`: sculpted terrain samples, selected projection and declarative asset placements.
- `render_world.py`: offline geometry construction, lighting and three camera bakes.
- `engine.js`: existing browser route-generation and presentation architecture, adapted for elevation-aware projection and clean-only display.
- `environment.js`: embedded environment image and height samples.
- `index.html`, `style.css`, `bundle.py`: development entrypoint and standalone bundler.
- `screenshots/`: 1080p browser captures, three camera/light views, refinement passes and before/after comparison.
- `qa-results.json`, `elevation-validation.json`, `TECHNICAL-REPORT.md`: inspection and validation findings.
- `assets/`: original KayKit Medieval Hexagon Pack subset and licence (CC0).

## Build locally
Python 3.10+ with numpy, scipy, shapely >=2, pillow, trimesh and numba. To regenerate the original matched road geometry, additionally install scikit-image and run `python build_layout.py` before the bake. To rebuild the environment and single-file HTML:

```
pip install numpy scipy 'shapely>=2' pillow trimesh numba
python render_world.py
python bundle.py
```

Browser tests use Playwright and Chromium (`/usr/bin/chromium` in this environment; adjust executable path locally):

```
pip install playwright
python qa_environment.py
```

The HTML bundle is offline; Python dependencies are needed only for rebuilding, not viewing. Original KayKit models and textures retain their original CC0 terms; supplemental coast, terrain, crop and harbour geometry is original to this standalone revision.
