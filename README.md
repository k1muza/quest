# Kingdom Quest

An offline spectator board and a Blender map production kit built around the KayKit Medieval Hexagon assets (CC0 1.0).

## Map gallery

Open [the four-map gallery](unified/maps.html) locally. Each board is a standalone offline HTML page with the shared Quest scoring controls, animated team pieces, route depth, and subtle water glints.

- [Four-map render comparison](maps/contact-sheet.png)
- [Interactive board comparison](maps/contact-sheet-runtime.png)
- [Route comparison](maps/contact-sheet-routes.png)
- [Bridge and coastal landing details](maps/contact-sheet-details.png)
- [Current tie, movement, reversal, and winner sequence](maps/kingdom-quest/reports/runtime-review-sequence.webm)
- [Original gameplay recording](unified/screenshots/quest-gameplay-demo.webm)

Each map folder contains its editable `.blend` scene, scene configuration, full-resolution render, compact WebP background, depth map, route/camera/landmark exports, validation reports, and visual evidence. The maps support 30, 40, or 50 movement steps; each setting includes the start position, so 40 moves use 41 physical positions.

## Build and edit maps

Project root: `C:\Users\Kelvin\Desktop\quests`.

Create the project virtual environment and install the repository's Python libraries there:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Blender is used for scene assembly and rendering; Python scripts use `.venv` for image processing, packaging, and validation. To rebuild all map renders and their standalone packages:

```powershell
.\.venv\Scripts\python.exe tools\blender\build_all_maps.py --quality final --threads 8
```

Use `--quality draft` or `--quality review` when shaping a map. A new map starts from a copy of a `maps/<id>` folder; edit its `scene-config.json`, then run the review and final commands with `--map-id <id>`. See [map production progress and workflow](docs/MAP-PRODUCTION-PROGRESS.md).

Run the map-package browser smoke checks with:

```powershell
.\.venv\Scripts\python.exe unified\qa_maps.py
```

## Historical editions

- [Unified board notes](unified/README.md): original approved Quest runtime and state API.
- [Environment edition](environment/README.md): earlier environment-only implementation.
- [Gameplay edition](gameplay/README.md): earlier playable spectator board.

These editions remain for history and regression reference. The Safari Rush branch remains separate and is not part of this map set.

The downloaded KayKit pack and its CC0 licence are kept in `assets/kaykit-medieval/originals/`; the reusable Blender library and asset manifest are documented in [the asset library notes](assets/kaykit-medieval/README.md).
