# Map production progress

- **Branch:** `feature/kaykit-blender-maps` (not merged into `main`)
- **Project root:** `C:\Users\Kelvin\Desktop\quests`
- **Baseline:** `6622636` (`main` / approved unified board baseline)
- **Current phase:** F - validation and delivery
- **Design direction:** use existing maps as gameplay/history references; build fresh Blender geography, lighting, composition, and camera work with the KayKit asset family.
- **Source pack:** `assets/kaykit-medieval/originals/KayKit_Medieval_Hexagon_Pack_1.0_FREE.zip` (CC0 1.0)
- **Python:** `.venv` with repository requirements installed
- **Blender:** 5.2.3 LTS

## Completed

- Created the reusable KayKit Blender library from the downloaded 221-model pack: 221 Asset Browser collections, 263 mesh objects, 13 packed atlases, and 12 catalogs. Asset validation passed with no import warnings.
- Built four original Blender layouts using a shared configurable assembler and the same lightweight Canvas 2D Quest runtime:
  - **Kingdom Quest - The Long Crossing:** forest and farms, a broad river crossing, northern ridge, and castle approach.
  - **Winding River - The Two Crossings:** S-shaped river, two bridges, three settlements, and a long loop between riverbanks.
  - **Mountain Pass - The High Switchbacks:** three connected rocky massifs around a high switchback route, village, ford, and elevated destination.
  - **Coastal Kingdom - The Sapphire Reach:** irregular bays, coastal road, inlet crossing, piers, headland, and castle.
- Rendered every environment at 1920 x 1080 and saved its editable Blender scene. Depth and route exports use matching camera framing.
- Packaged four self-contained offline boards and a gallery at `unified/maps.html`. Runtime backgrounds are WebP; depth, route data, CSS, JavaScript, and pawn art are embedded in each board.
- Added clean-map, route-overlay, default-board, six-team, highland, and river-crossing visual evidence. Produced a short gameplay recording and comparison contact sheets under `maps/` and `unified/screenshots/`.
- Updated the runtime contract so each map's 40-move default uses 41 physical positions. The selector lists only map-validated 30, 40, and 50 movement steps.

## Validation results

- Scene and route validation: **PASS for all four maps**. No route intersections, out-of-frame route samples, geometry validation issues, or depth samples missing.
- Depth road alignment, p95 absolute error: Kingdom Quest 0.115; Winding River 0.075; Mountain Pass 0.191; Coastal Kingdom 0.089 world units.
- Route spacing at 30 / 40 / 50 movement steps (minimum final-resolution pixels):

| Map | 30 steps / 31 positions | 40 / 41 | 50 / 51 |
|---|---:|---:|---:|
| Kingdom Quest | 47.51 | 35.63 | 29.16 |
| Winding River | 44.58 | 28.79 | 26.05 |
| Mountain Pass | 48.70 | 36.32 | 28.70 |
| Coastal Kingdom | 46.94 | 36.57 | 29.66 |

- **60 steps are excluded**: the projected positions fall below the 26-pixel readability threshold on each map.
- New offline pages were opened in Chromium for all four maps. Backgrounds decoded at 1920 x 1080, each advertised route capacity validated, six-team setup and start worked, and no browser errors occurred.
- The repeatable map runtime smoke suite `unified/qa_maps.py` passes across the gallery and four boards; its current report is `maps/runtime-qa.json`.
- Existing canonical runtime regression suite `unified/qa.py`: **41/41 PASS** in Chrome 158; zero page errors and zero external requests. This suite covers the approved original board. The separate map-page checks above cover the new standalone routes and controls.
- Some optional crag groups have fewer rocks than their requested count after clearance checks; these are placement warnings only and did not produce geometry/route validation failures. Winding River's 50-step setting is close to the 26-pixel limit (26.05 px).

## Rebuild commands

Run these from the project root. Python image processing and package validation use `.venv`; Blender runs through its installed executable (or `BLENDER` environment variable).

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tools\blender\build_all_maps.py --quality review --threads 8
.\.venv\Scripts\python.exe tools\blender\build_all_maps.py --quality final --threads 8
.\.venv\Scripts\python.exe unified\qa_maps.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python tools\blender\validate_asset_library.py -- --blend assets\kaykit-medieval\library\kaykit-medieval.blend --manifest assets\kaykit-medieval\asset-manifest.json
```

To build only one map, add `--map-id <id>`. For a one-map render without repackaging the complete gallery, add `--no-package`, then run `tools\blender\package_map.py --map-dir maps\<id>`.

## Map-specific instructions

- [Kingdom Quest](../maps/kingdom-quest/README.md)
- [Winding River](../maps/winding-river/README.md)
- [Mountain Pass](../maps/mountain-pass/README.md)
- [Coastal Kingdom](../maps/coastal-kingdom/README.md)

## Next action

Review the gallery and screenshots, then request any targeted artistic corrections. Keep this branch separate; do not merge it into `main` without approval.
