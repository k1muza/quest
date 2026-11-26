# KayKit Medieval Hexagon source and Blender library

The original `KayKit_Medieval_Hexagon_Pack_1.0_FREE.zip` is retained under
`originals/` as the source of record. It includes the pack's `License.txt`:
KayKit Medieval Hexagon Pack 1.0 by Kay Lousberg, released under CC0 1.0.

The reusable native Blender library is generated at
`library/kaykit-medieval.blend`. Its collections preserve imported model
hierarchies and transforms; repeated placement should use collection instances.
Asset catalogs are stored next to the `.blend` file. A representative render is
in `previews/asset-showcase.png`, and `asset-manifest.json` records provenance,
source hashes, dimensions and import results.

Build the library from the repository root:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python tools/blender/build_asset_library.py -- --zip assets/kaykit-medieval/originals/KayKit_Medieval_Hexagon_Pack_1.0_FREE.zip --output assets/kaykit-medieval/library/kaykit-medieval.blend
```

The project `.venv` is for the repository's Python tools. Blender scripts use
Blender's bundled Python and `bpy`; do not install the Blender API into `.venv`.

Validate the saved library and its packed texture assets:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python tools/blender/validate_asset_library.py -- --blend assets/kaykit-medieval/library/kaykit-medieval.blend --manifest assets/kaykit-medieval/asset-manifest.json
```
