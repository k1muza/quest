# Kingdom Quest

Standalone medieval adventure board and environment, based on KayKit Medieval Hexagon assets (CC0).

## Editions

- [Environment](environment/README.md): latest terrain, architecture and art-direction revision; open `environment/kingdom-quest-environment.html` locally.
- [Gameplay](gameplay/README.md): earlier playable spectator board with team controls and automatic stops; open `gameplay/kingdom-quest-kaykit.html` locally.

Each edition is self-contained to preserve its tested build paths. The environment edition does not yet expose gameplay controls. Both standalone HTML files work offline.

## Development

Install `pip install -r requirements.txt` for rendering and validation. Follow the edition-specific README for build commands. Browser tests require Chromium and Playwright.

## Documentation

- [Environment report](environment/TECHNICAL-REPORT.md)
- [Gameplay report](gameplay/TECHNICAL-REPORT.md)
- [Environment specification](docs/specifications/environment.md)
- [Gameplay specification](docs/specifications/gameplay.md)

Original KayKit asset licence is included with both asset directories. No Game Night or Flutter integration is included.
