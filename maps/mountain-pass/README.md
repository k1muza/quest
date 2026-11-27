# Mountain Pass - The High Switchbacks

A rising road threads between three connected rocky massifs, a river ford, foothill settlements, and the High Ledge Castle.

The mountain formations are the main visual feature; the winding route stays clear of the rock faces and remains readable through the pass.

## Capacity

The board supports **30, 40, and 50 movement steps**, corresponding to 31, 41, and 51 physical positions including the start. The default is 40 movement steps / 41 positions. A 60-step option is omitted because its screen spacing is too tight for this map.

## Build

From the project root, preview or rebuild this map with the shared Blender assembler:

```powershell
.\.venv\Scripts\python.exe tools\blender\build_all_maps.py --quality review --map-id mountain-pass
.\.venv\Scripts\python.exe tools\blender\build_all_maps.py --quality final --map-id mountain-pass --no-package
.\.venv\Scripts\python.exe tools\blender\package_map.py --map-dir maps\mountain-pass
```

Edit `scene-config.json` to change route points, terrain, forest, fields, bridges, and camera composition. The saved scene is `source\mountain-pass.blend`.

## Outputs and review evidence

- `output\background.png` - full-resolution render master (1920 x 1080)
- `output\background.webp` - compact runtime background
- `output\depth.png`, `route.json`, `camera.json`, and `landmarks.json` - shared runtime data
- `output\route-overlay-review.png` - route projection inspection
- `reports\scene-validation.json` and `map-validation.json` - geometry, route, spacing, and depth checks
- `reports\runtime-board.png` and `runtime-six-team.png` - browser evidence
- `reports\mountain-detail.png` and `river-crossing-detail.png` - close-up evidence
- `unified\maps\mountain-pass.html` - self-contained offline board

See [the overall map-production log](../../docs/MAP-PRODUCTION-PROGRESS.md) for the four-map comparison and validation results.
