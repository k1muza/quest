# Safari Rush

Southern African-themed Quest board for 30-Second Sprint. Source implementation on feature/map-safari-rush, based on the approved visual-corrections branch (beb778c129b38d0fa639e8fc423ca4fd11d41cfe), not the cinematic research branch.

## Build and inspect

From repository root:

```sh
pip install -r requirements.txt
python -m playwright install chromium
python unified/build.py --safari --render
python maps/safari-rush/qa.py
python maps/safari-rush/record_demo.py  # requires ffmpeg
python unified/build.py
CHROMIUM=/path/to/chromium python unified/qa.py
```

Open maps/index.html to select either standalone board. Open maps/safari-rush/safari-rush.html directly for Safari Rush. Generated JPEG, lossless packed depth PNG, route metadata and standalone HTML are outputs of the canonical offline renderer and bundler; they are not substitutes for the source.

## Implementation decisions

- Reuse the matched KayKit hex layout, actual road and river centerlines and bridge deck from Kingdom Quest. This intentionally preserves the topology, not its medieval scenery. The current layout contains approximately 158 cells; terrain elevation, palette and props are separate for Safari.
- Theme props are original procedural low-poly meshes in environment/safari_scene.py; road and river are still rendered from the original glTF geometry.
- A steep upstream river spillway, western granite domes, dry savanna, clustered wildlife, southwest camp and curved dry-stone enclosure replace medieval thematic objects.
- The map contract is map.json; render and bake are selected by --safari. The runtime uses the same board.js and floating-markers.js, with per-map presentation defaults.
- Default 30 movement steps / 31 stops. Supported candidates 20, 30, 40 and 50 movements (21, 31, 41, 51 physical positions). The state API retains stopCount and the legacy one-based stop field; positions() adds zero-based step. Safari labels use zero-based steps. Invalid projected clearance is rejected, not silently accepted. State remains authoritative; route arrival never ends the round-based game.

## Evidence status

The source and acceptance suite were authored and committed using the GitHub connector. The author's container could not resolve GitHub; a complete repository checkout, offline render, browser acceptance and visual inspection could not be executed there. Consequently this source revision is not a visually accepted or production-ready map. The branch workflow runs rendering and tests and publishes actual generated evidence when those jobs execute successfully. Do not infer a passing run from the presence of this workflow. Inspect the rendered images, wildlife proportions, waterfall, route visibility, object footprints, sanctuary entrance and both game regressions before merging.

The current implementation intentionally uses the inherited road topology; it is not a newly routed map. Its artistry, waterfall geometry, exact regional allocation, 1080p marker clearance and size are unverified until the generated evidence exists.
