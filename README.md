# Kingdom Quest

Standalone medieval adventure board and environment, based on KayKit Medieval Hexagon assets (CC0).

## Canonical interactive board

**[Unified interactive board](unified/README.md)** — latest approved environment combined with animated tokens, scoring, depth-aware occlusion and television presentation. Open `unified/kingdom-quest.html` locally. See [state API](unified/STATE-API.md) and [technical report](unified/TECHNICAL-REPORT.md).

## Historical editions

- [Environment](environment/README.md): latest terrain, architecture and art-direction revision; open `environment/kingdom-quest-environment.html` locally.
- [Gameplay](gameplay/README.md): earlier playable spectator board with team controls and automatic stops; open `gameplay/kingdom-quest-kaykit.html` locally.

The historical editions are retained independently for regression reference. Each edition is self-contained to preserve its tested build paths. The environment edition does not yet expose gameplay controls. Both standalone HTML files work offline.

## Blender map production

The current production branch, `feature/kaykit-blender-maps`, is building fresh 3D map scenes from the KayKit Medieval Hexagon pack. Existing maps are retained as historical references and runtime-contract examples. See [map production progress](docs/MAP-PRODUCTION-PROGRESS.md) and [the KayKit asset library notes](assets/kaykit-medieval/README.md).

## Development

Install `pip install -r requirements.txt` for rendering and validation. Follow the edition-specific README for build commands. Browser tests require Chromium and Playwright.

## Documentation

- [Environment report](environment/TECHNICAL-REPORT.md)
- [Gameplay report](gameplay/TECHNICAL-REPORT.md)
- [Environment specification](docs/specifications/environment.md)
- [Gameplay specification](docs/specifications/gameplay.md)

Original KayKit asset licence is included with both asset directories. No Game Night or Flutter integration is included.
