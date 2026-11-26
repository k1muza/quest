# Map production progress

- **Branch:** `feature/kaykit-blender-maps`
- **Baseline:** `6622636` (`main`, also the unified interactive board baseline)
- **Current phase:** B — first fresh Blender map
- **Design direction:** Use prior maps as gameplay and visual history. New scenes use fresh geography, camera work and lighting with KayKit assets.
- **Source pack:** `assets/kaykit-medieval/originals/KayKit_Medieval_Hexagon_Pack_1.0_FREE.zip` (CC0 1.0)
- **Python environment:** `.venv` created with Python 3.10; dependencies installed from `requirements.txt`.
- **Blender:** 5.2.3 LTS; glTF importer is available.

## Completed

- Compared the available Git branches and started the production branch from the clean stable `main` baseline. The Safari Rush branch remains separate.
- Moved the repository to the workspace root, `C:\Users\Kelvin\Desktop\quests`.
- Confirmed the repository already contains 51 KayKit glTF models; the downloaded pack supplies 221 glTF models. The new Blender library imports the complete original set rather than duplicating them as loose extracted files.
- Added a repeatable Blender asset-library builder that packs source textures, catalogs collections, records dimensions and provenance, and renders an asset showcase.
- Built the library: 221 models, 221 Asset Browser collection assets, 263 mesh objects, 326,492 vertices, 13 packed atlases, 12 catalogs, no import warnings. The 1920×1200 showcase was rendered and visually inspected.
- Added and ran the structural validator. Result: `PASS`, no failures or warnings.
- Installed repository Python requirements into `.venv`.

## Remaining

1. Assemble a fresh first map in Blender and validate its road, terrain and camera export against the existing shared runtime.
2. Produce the other three distinct map layouts from reusable assets and configuration.
3. Integrate map packages, ambient animation, review evidence and runtime builds.

## Commands

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python tools/blender/build_asset_library.py -- --zip assets/kaykit-medieval/originals/KayKit_Medieval_Hexagon_Pack_1.0_FREE.zip --output assets/kaykit-medieval/library/kaykit-medieval.blend
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python tools/blender/validate_asset_library.py -- --blend assets/kaykit-medieval/library/kaykit-medieval.blend --manifest assets/kaykit-medieval/asset-manifest.json
```

## Notes

- The repository's Python requirements are isolated in `.venv` (ignored by Git). Blender-specific scripts use Blender's bundled Python.
- The branch has not yet incorporated any Safari Rush-specific environment changes. Review any shared runtime improvements separately before porting them.
