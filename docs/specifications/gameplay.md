# Kingdom Quest — Standalone Modular Hexagonal Adventure Board

## 1. Role and objective

Act as a senior game environment designer, level designer, 3D artist and frontend game engineer.

Design and implement a visually impressive, fully functional, standalone browser-based board game environment using the **KayKit Medieval Hexagon asset collection**.

The board will eventually serve as a television spectator display for Game Night, a multiplayer party game in which competing teams earn points and advance their playing pieces through a shared world.

For this phase, concentrate exclusively on producing an exceptional standalone map and demonstrating its visual and movement capabilities.

**Do not integrate with the existing Game Night repository, Flutter application, networking infrastructure or gameplay engine.**

## 2. Provided asset collection

Use KayKit Medieval Hexagon as the primary world-building asset library.

Official sources:

- https://kaylousberg.itch.io/kaykit-medieval-hexagon
- https://github.com/KayKit-Game-Assets/KayKit-Medieval-Hexagon-Pack-1.0

Download and inspect the actual asset collection before commencing implementation.

Identify the available:

- Hexagonal terrain modules.
- Road configurations.
- River configurations.
- Bridge assets.
- Coastline and water tiles.
- Hills and mountains.
- Trees and vegetation.
- Residential buildings.
- Castles and defensive structures.
- Agricultural assets.
- Decorative props.

Determine the actual model dimensions, origins, orientations, connection points and material configurations.

Do not make assumptions about the available models without inspecting them.

Use the supplied assets wherever practical instead of recreating them using primitive geometry.

Verify and retain the original asset licence.

## 3. Artistic direction

Create a premium miniature medieval kingdom with the appearance of a professionally designed digital tabletop game.

The environment should feel:

- Adventurous.
- Richly populated.
- Geographically coherent.
- Architecturally believable.
- Playful but not childish.
- Visually sophisticated.
- Interesting to explore.

Draw inspiration from the visual quality and environmental composition of games such as:

- Civilization VI.
- Northgard.
- Dorfromantik.
- The Settlers.
- Kingdoms and Castles.
- Premium digital tabletop games.

Do not reproduce their artwork or proprietary designs.

The simplicity of the hexagonal construction system should not result in a simplistic visual experience.

**The map must look like a deliberately designed kingdom, not an asset demonstration or a randomly generated terrain grid.**

## 4. Map size and composition

Create a substantial landscape-oriented map suitable for a 1920 × 1080 television display.

Begin by evaluating approximately 100–180 terrain hexagons, adjusting the final quantity according to composition, visual clarity and asset scale.

The map should have an irregular, geographically interesting perimeter rather than necessarily forming a perfect rectangle.

Consider presenting the world as a miniature continent or island surrounded by water.

Use an elevated orthographic or near-isometric camera that allows spectators to see the complete journey.

Ensure that important settlements and landmarks remain sufficiently large and recognisable.

Do not sacrifice visual detail merely to increase the number of terrain tiles.

## 5. Geographic world design

Design the world as a coherent geographical system before placing individual decorative objects.

Include the following major regions.

### A. Starting village

A humble, welcoming settlement from which all teams begin their journey.

Include:

- Small houses.
- A central gathering area.
- Local streets.
- Gardens or farms.
- Supporting vegetation.
- A clearly identifiable starting position.

### B. Agricultural district

A developed farming region.

Include:

- Organised agricultural plots.
- Farmhouses.
- Windmills where available.
- Access roads.
- Natural boundaries.
- Nearby woodland.

Agricultural areas should follow a logical arrangement rather than appearing randomly scattered.

### C. Dense woodland

Create a substantial forest region with:

- Dense tree coverage.
- Natural variations in tree species and scale.
- Irregular forest boundaries.
- Small clearings.
- A road passing through the woodland.
- Occasional rocks and decorative props.

The forest should feel like a genuine geographical region rather than a few isolated trees.

### D. River valley

Create a continuous river system that interacts with the surrounding landscape.

Requirements:

- River segments must connect correctly across terrain boundaries.
- Water should follow a geographically believable course.
- Include riverbank vegetation where appropriate.
- Position settlements and agricultural areas logically around the river.
- Include at least one bridge crossing on the playable route.

The river should contribute to the map's composition and visual identity.

### E. Mountain region

Create an impressive mountainous area with:

- Connected mountain formations.
- Foothills.
- Rocky terrain.
- Mountain passes.
- Forest transitions.
- A winding road navigating the terrain.

Avoid placing isolated mountains randomly across a flat grass surface.

Mountain formations should have a convincing geological relationship with their surrounding terrain.

### F. Developed township

Create a more sophisticated town approaching the final destination.

The township should demonstrate deliberate urban planning.

Include:

- A coherent street network.
- Houses facing streets.
- Residential clusters.
- A central market or public square.
- Supporting commercial buildings.
- Decorative vegetation.
- A clear connection to the kingdom's principal road.

The town should resemble an inhabited miniature settlement.

### G. Royal citadel

Create the most impressive architectural landmark on the map.

The citadel must include:

- A convincing outer defensive perimeter.
- Connected walls.
- Defensive towers.
- A clearly identifiable gatehouse.
- A royal castle or palace inside the enclosure.
- An internal courtyard.
- Supporting buildings where appropriate.
- An impressive final destination.

The castle must be protected by the walls rather than positioned beside them.

The playable route must enter the citadel through its gate and terminate within the royal courtyard.

## 6. Terrain construction system

Use hexagonal coordinates as the foundation of the world.

Implement a reusable terrain system supporting axial coordinates or another mathematically consistent hex-grid representation.

Each terrain cell should define:

- Grid coordinates.
- Terrain type.
- Model reference.
- Orientation.
- Elevation.
- Road connections.
- River connections.
- Decorative objects.
- Walkability where applicable.

Ensure that:

- Adjacent terrain modules align correctly.
- Road connections meet at compatible edges.
- River connections meet at compatible edges.
- Coastlines face the correct direction.
- Buildings do not intersect neighbouring objects.
- Terrain transitions remain visually convincing.

Inspect the actual KayKit geometry to establish the correct coordinate transformation and orientation conventions.

Do not rely on arbitrary screen-space positioning of terrain objects.

## 7. Road network

The road network is one of the most important components of the experience.

Design a substantial primary road that travels throughout the kingdom.

The route should:

1. Begin in the starting village.
2. Travel through the agricultural district.
3. Pass through dense woodland.
4. Cross a river.
5. Navigate the mountain region.
6. Enter the developed township.
7. Approach the fortified royal citadel.
8. Pass through the gatehouse.
9. Terminate within the royal courtyard.

The road should make effective use of the entire map rather than following a short diagonal across its centre.

Use multiple sweeping turns, regional detours and interesting geographical transitions.

Introduce secondary roads where appropriate to connect settlements, farms and buildings.

Distinguish the primary playable route from secondary roads without introducing an excessively bright or visually intrusive overlay.

Ensure all road connections are geometrically valid.

## 8. Independent gameplay stopping positions

**Terrain hexagons and gameplay stopping positions must be separate systems.**

Do not restrict gameplay to one stop per hexagonal tile.

The terrain grid defines the world, while the gameplay route defines where playing pieces stop.

A single terrain hexagon may contain:

- No gameplay stops.
- One gameplay stop.
- Multiple gameplay stops.

The number of stops depends on the road length passing through the tile.

### Route representation

Represent the primary playable route as a continuous ordered path following the actual road centreline.

Each road module should have corresponding local path metadata describing:

- Entry position.
- Exit position.
- Intermediate curve points.
- Ground elevation.
- Travel direction.

Transform these coordinates into world-space positions using the terrain module's translation, rotation and elevation.

For curved road sections, use suitable interpolated curves rather than straight lines that cut across the surrounding terrain.

Bridge paths must follow the actual bridge deck.

The path through the citadel must follow the gate opening and courtyard road.

### Stop generation

Implement automatic gameplay stop generation based on distance along the complete route.

The algorithm should:

1. Identify the ordered sequence of road modules.
2. Validate their connectivity.
3. Construct a continuous world-space path.
4. Calculate the cumulative arc length.
5. Generate stopping positions at approximately regular distance intervals.
6. Assign sequential stop indices.
7. Determine the appropriate surface elevation and orientation at each position.
8. Validate that every generated stop is located on a traversable surface.

Initially demonstrate configurations containing:

- 30 stops.
- 40 stops.
- 50 stops.
- 60 stops.

Treat these as demonstration configurations, not fixed limits.

The same environment should support different numbers of gameplay stops without requiring the terrain to be rebuilt.

Ensure the configured stop count does not produce overlapping markers or unreadable spacing. Reject excessively dense configurations or provide a clearly explained alternative.

### Stop appearance

Stopping positions should resemble small physical objects integrated into the road.

Consider:

- Numbered stone stepping platforms.
- Small cobblestone plaques.
- Circular stone discs.
- Embossed markers.
- Decorative milestone platforms.

Use restrained visual styling that complements the medieval environment.

Avoid oversized square tiles that obscure the underlying road.

The starting position should be clearly recognisable.

Important milestones may receive distinctive styling.

The final destination should feature a special decorative finish marker.

## 9. Team playing pieces

Implement attractive miniature playing pieces representing competing teams.

Support two to six teams.

Playing pieces may take the form of:

- Classic board game pawns.
- Medieval adventurers.
- Miniature knights.
- Heraldic figures.
- Other appropriate collectible-style tokens.

If suitable pieces are unavailable in the primary asset collection, obtain compatible CC0 models from:

- KayKit Board Game Bits.
- Kenney.
- Quaternius.

Playing pieces must:

- Be immediately identifiable from a distance.
- Have distinct team colours.
- Cast convincing contact shadows.
- Remain visible against the environment.
- Follow the correct terrain elevation.
- Have appropriate scale relative to the stopping positions.
- Avoid intersecting buildings or environmental objects.

Where multiple teams occupy the same stop, arrange them using a consistent local offset system.

Do not allow pieces to completely obscure one another.

Display the team identity above or beside each piece where appropriate.

## 10. Movement and animation system

Implement a standalone movement engine that animates team pieces along the generated route.

Movement should follow the road centreline, including curved sections, bridges, mountain passes and the citadel entrance.

Support:

- Forward movement by one or multiple stops.
- Backward movement.
- Animated jumps or hops.
- Smooth acceleration and deceleration.
- Rotation towards the direction of travel where appropriate.
- Subtle landing effects.
- Milestone celebrations.
- Active-team highlighting.

The token must follow the complete traversable path between stops rather than moving directly through intervening buildings, mountains or rivers.

Handle rapid movement commands without allowing the animation queue to become excessively long.

The final animated position must always reconcile with the commanded position.

Ensure that backward movement retraces the same valid route.

## 11. Camera and rendering

Evaluate the best implementation approach after inspecting the asset collection.

Three.js is a reasonable starting point because KayKit provides reusable 3D models.

Consider:

- Orthographic camera.
- Consistent isometric or three-quarter perspective.
- Physically coherent lighting.
- Ambient illumination.
- Directional shadows.
- Ambient occlusion where practical.
- Appropriate antialiasing.
- Contact shadows.
- Balanced colour grading.

Use soft, warm daylight to establish a welcoming miniature-world aesthetic.

Avoid:

- Excessively dark shadows.
- Oversaturated colours.
- Harsh lighting.
- Excessive bloom.
- Intrusive visual effects.
- Flat, unlit materials.

The map should look like a high-quality physical miniature displayed on a tabletop.

### Camera behaviour

Provide:

- A default full-map presentation.
- Optional zoom and pan for inspection.
- A reset-camera action.
- Optional cinematic camera transitions for demonstration.

The default presentation must show the complete map.

Do not automatically zoom into individual teams during ordinary gameplay, as spectators must remain able to follow the overall competition.

## 12. Environmental animation

Introduce selective, lightweight ambient animations to make the world feel alive.

Potential effects include:

- Flowing river water.
- Rotating windmills.
- Gently moving trees.
- Flags moving in the wind.
- Birds flying over the landscape.
- Subtle smoke from settlements.
- Moving clouds.
- Small water reflections.

Use only effects appropriate to the assets and visual composition.

Ambient animation should not compromise frame rate or distract from team movement.

Provide an option to disable ambient effects during performance testing.

## 13. Standalone demonstration controls

Provide a collapsible development panel separate from the normal presentation.

The panel should allow the operator to:

- Configure the number of teams.
- Select the active team.
- Move the selected team forward by one point.
- Move forward by three or five points.
- Move backwards.
- Undo the previous movement.
- Set a team's position directly.
- Create tied positions.
- Reset all team positions.
- Change the number of gameplay stops.
- Simulate rapid movement events.
- Trigger milestone effects.
- Trigger a winner celebration.
- Enable or disable ambient animation.
- Inspect and reset the camera.
- Toggle route debugging information.
- Enter full-screen presentation.

Do not expose these controls during normal spectator presentation.

Use simulated game state only.

There is no requirement to connect to the existing Game Night application.

## 14. Minimal spectator interface

The primary deliverable is the map, not a complete game dashboard.

Keep interface elements minimal.

Provide only:

- Map title.
- Active team.
- Team names.
- Team scores or positions.
- Optional demonstration countdown.
- Full-screen control.

Use modern, highly legible typography.

The environment should occupy the overwhelming majority of the screen.

Avoid oversized score cards, dashboard panels and decorative interface elements that compete with the map.

Provide a clean-map mode that hides the entire interface and optionally hides the playing pieces and gameplay stops.

This mode will allow the artistic quality of the environment to be assessed independently.

## 15. Reusable map architecture

Although this phase delivers only one complete map, the implementation should establish a reusable foundation.

Separate the following responsibilities:

1. Asset loading.
2. Terrain grid construction.
3. Geographic composition.
4. Road connectivity.
5. Route construction.
6. Stop generation.
7. Playing-piece management.
8. Movement animation.
9. Camera management.
10. Public presentation.

Store map definitions declaratively rather than hardcoding every terrain position into the rendering engine.

An example conceptual structure is:

```json
{
  "id": "kingdom-quest",
  "name": "Kingdom Quest",
  "terrain": [],
  "settlements": [],
  "environment": [],
  "roadNetwork": [],
  "primaryRoute": [],
  "defaultStopCount": 40,
  "milestones": [],
  "camera": {},
  "lighting": {}
}
```

The final schema should reflect the actual asset library and rendering implementation.

A future map should primarily require a new terrain configuration and asset arrangement rather than a rewritten rendering engine.

Do not build a complete procedural map generator or visual map editor during this phase.

However, avoid architectural decisions that would prevent those features from being introduced later.

## 16. Performance and offline operation

The final application will eventually run in a Smart TV browser, so performance must remain a significant consideration.

Requirements:

- All dependencies and assets must be bundled locally.
- No mandatory internet connection.
- No runtime dependency on external CDNs.
- No runtime dependency on Google Drive or GitHub.
- Efficient asset loading and caching.
- Reuse materials and geometry.
- Use instanced rendering where appropriate.
- Avoid unnecessarily expensive post-processing.
- Limit shadow complexity.
- Optimise texture and model sizes.

Do not package unused asset collections into the runtime application.

Provide configurable rendering quality where practical.

For example:

- High quality for desktop demonstrations.
- Medium quality for ordinary hardware.
- Low quality for modest television hardware.

Evaluate the feasibility of exporting the environment as a pre-rendered background with animated 2D playing pieces as a future fallback for browsers without reliable WebGL support.

Do not compromise the initial visual design merely to implement every possible fallback during this phase.

## 17. Map validation

Implement automated validation for:

- Duplicate terrain coordinates.
- Incorrect tile orientations.
- Invalid road connections.
- Disconnected primary route segments.
- Incorrect river connections.
- Invalid stop positions.
- Overlapping stopping markers.
- Non-traversable route sections.
- Missing assets.
- Invalid team positions.
- Route entry and exit alignment.
- Incorrect movement across bridges or elevated terrain.

Where possible, provide a visual debugging mode showing:

- Hexagonal grid boundaries.
- Terrain coordinates.
- Road entry and exit points.
- Route centreline.
- Gameplay stop positions.
- Elevation information.
- Invalid connections.

Debugging overlays must be disabled by default in the normal presentation.

## 18. Mandatory visual refinement process

Do not immediately proceed to gameplay implementation.

Follow this sequence.

### Phase 1 — Asset inspection

Inspect the actual KayKit collection and document its capabilities.

### Phase 2 — World planning

Develop a coherent map layout showing:

- Settlements.
- Mountain formations.
- Forest regions.
- River systems.
- Coastlines.
- Main road.
- Secondary roads.
- Royal citadel.

### Phase 3 — Static environment construction

Construct the complete world using the selected assets.

Do not introduce gameplay markers until the underlying environment is visually convincing.

### Phase 4 — Architectural and environmental refinement

Improve:

- Township organisation.
- Forest density.
- Mountain composition.
- River continuity.
- Castle enclosure.
- Road geometry.
- Environmental detail.
- Lighting.
- Camera composition.

### Phase 5 — Gameplay route integration

Implement the continuous route and automatically generated stopping positions.

### Phase 6 — Playing pieces and animation

Introduce team pieces, movement and spectator presentation.

### Phase 7 — Visual quality assurance

Render and inspect the actual implementation at 1920 × 1080.

Undertake at least three meaningful visual refinement passes.

Do not merely add more objects to increase apparent complexity.

Every refinement should improve composition, visual storytelling, geographical coherence or presentation quality.

## 19. Acceptance criteria

The finished environment must demonstrate:

- A beautifully composed miniature medieval kingdom.
- Consistent use of KayKit assets.
- Dense, believable forest regions.
- Organised townships with coherent street networks.
- Connected mountain formations.
- A continuous river system.
- At least one playable bridge crossing.
- A substantial road travelling throughout the kingdom.
- A fully enclosed royal citadel.
- A playable route entering the citadel through its gate.
- A final destination within the royal courtyard.
- Independently generated gameplay stopping positions.
- Attractive and readable team playing pieces.
- Smooth movement along the actual road.
- Support for two to six teams.
- Complete offline operation.
- A clean and reusable implementation.

The map should remain visually impressive when all gameplay elements are hidden.

Target a visual quality of at least 9/10, but support the assessment with actual screenshots and observable criteria rather than an arbitrary self-assigned rating.

## 20. Deliverables

Create a self-contained standalone project containing:

- `index.html`
- Locally bundled JavaScript and CSS.
- All required optimised assets.
- A declarative map definition.
- A reusable hexagonal terrain renderer.
- A road and route connectivity system.
- An automatic stopping-position generator.
- A team-piece animation system.
- A demonstration control panel.
- Asset licensing documentation.
- A README containing local execution instructions.

Provide screenshots showing:

1. The complete environment without any gameplay overlays.
2. The complete board with numbered stopping positions.
3. Four competing teams.
4. Six competing teams.
5. The starting village.
6. The agricultural region.
7. The dense forest.
8. The river and bridge crossing.
9. The developed township.
10. The royal citadel and its internal courtyard.
11. The final winner presentation.

Also provide a brief technical report covering:

- Rendering approach.
- Asset selection.
- Map definition architecture.
- Stop-generation algorithm.
- Asset sizes.
- Measured browser performance.
- Known limitations.
- Future Smart TV compatibility considerations.

Where browser security restrictions prevent direct opening of local model files through `file://`, provide a simple local HTTP server command or startup script.

The project must not require an internet connection after its dependencies and assets have been obtained.

## 21. Explicit exclusions

For this phase:

- Do not modify the Game Night repository.
- Do not create a Game Night feature branch.
- Do not modify the Flutter application.
- Do not implement WebSocket networking.
- Do not implement device pairing.
- Do not implement multiplayer synchronisation.
- Do not change existing gameplay rules.
- Do not implement multiple maps.
- Do not implement a full map editor.
- Do not introduce paid assets without approval.

Deliver one exceptional standalone map.

## Final creative standard

Imagine a beautifully constructed miniature kingdom sitting on a large tabletop, with competing teams travelling through villages, forests, river crossings, mountain passages and fortified towns before reaching a magnificent royal citadel.

The audience should enjoy looking at the world even when no pieces are moving.

The environment should inspire curiosity about what lies further along the road.

The hexagonal terrain system is a construction tool, not a restriction on creativity.

**Build the kingdom first. Establish its roads second. Generate the gameplay stops third. Bring the competition to life last.**