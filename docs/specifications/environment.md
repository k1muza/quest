# Kingdom Quest — KayKit Environment and Art Direction Refinement

## 1. Background

The current KayKit-based Kingdom Quest map establishes a promising technical foundation for a reusable hexagonal world-building system.

However, its visual quality is provisionally rated **7.5/10**.

The environment currently resembles a level editor preview rather than a finished, professionally designed game world.

The main weaknesses are:

- Excessively flat terrain.
- Muted lighting and colours.
- Mountains resembling isolated stacks of hexagonal blocks.
- Poorly organised townships.
- An overly mechanical coastline.
- An oversized and relatively empty castle courtyard.
- Insufficient geographical and architectural intrigue.

**Do not abandon KayKit or undertake another technical redesign.**

This iteration should concentrate exclusively on environmental composition, terrain modelling, architectural planning and rendering quality.

## 2. Reference material

Use the existing `kingdom-quest-clean-map.png` screenshot as the baseline for comparison.

Continue using the KayKit Medieval Hexagon asset collection:

https://kaylousberg.itch.io/kaykit-medieval-hexagon

https://github.com/KayKit-Game-Assets/KayKit-Medieval-Hexagon-Pack-1.0

Where the supplied assets are insufficient, consider modifying their geometry or materials, constructing compatible modular assets in Blender, or obtaining complementary CC0 assets.

Maintain a consistent artistic style throughout.

## 3. Terrain elevation — highest priority

The current map sits almost entirely on a single flat plane. This is one of the main reasons it lacks visual sophistication.

Introduce a coherent elevation system.

Create:

- Low-lying coastal regions.
- Rolling agricultural land.
- Raised woodland areas.
- River valleys.
- Mountain foothills.
- Elevated mountain passes.
- Terraced settlements.
- A raised plateau supporting the royal citadel.

Elevation changes must form meaningful geographical regions rather than isolated raised tiles.

Use gradual transitions, slopes, cliffs, retaining walls and terraces where appropriate.

Ensure that adjacent terrain modules remain visually connected.

Roads must accommodate elevation changes through traversable slopes, ramps, bridges or suitable transitional geometry.

Avoid floating objects, exposed terrain gaps and disconnected road sections.

### Acceptance standard

The island should have a recognisable three-dimensional silhouette, with meaningful differences in elevation visible from the default camera.

It should resemble a miniature landscape rather than a flat collection of hexagonal cells.

## 4. Mountain reconstruction

The existing mountains resemble repetitive stacks of concrete hexagons.

Redesign the mountain region as a connected geographical formation.

Requirements:

- Vary mountain height, size and orientation.
- Establish a continuous mountain ridge.
- Introduce smaller foothills around larger peaks.
- Integrate exposed rock with surrounding terrain.
- Introduce vegetation transitions at lower elevations.
- Establish a recognisable mountain pass.
- Route the principal road naturally through or around the mountain formation.

Where the existing mountain models are inadequate, modify them or introduce stylistically compatible low-poly mountain assets.

Retain the modular hexagonal terrain system without forcing every visible geological formation to resemble a hexagonal prism.

The mountains should create visual drama and a meaningful sense of geographical progression.

## 5. Township planning — highest priority

The current settlements still resemble houses scattered around available roads.

Redesign them as intentionally planned miniature townships.

Before positioning buildings, establish each settlement's street network, public spaces and functional areas.

### Starting village

Create a compact, welcoming rural settlement featuring:

- A recognisable village centre.
- Small houses facing local streets.
- Gardens and yards.
- A modest marketplace.
- Connected pedestrian paths.
- Agricultural land around its perimeter.
- A distinctive starting location for the future gameplay route.

Avoid isolated houses positioned randomly near the coastline.

### Agricultural district

Develop an organised agricultural landscape featuring:

- Larger contiguous agricultural plots.
- Different crop types where assets permit.
- Farmhouses positioned logically.
- Windmills.
- Barns and storage buildings.
- Access roads.
- Fences or natural boundaries.
- Irrigation channels where appropriate.

Replace the current scattered agricultural hexagons with clearly identifiable fields and farming districts.

### Developed township

The eastern settlement should resemble a prosperous medieval town.

Create:

- A main street.
- Smaller intersecting streets.
- Recognisable residential blocks.
- Buildings oriented towards their street frontages.
- A central paved market square.
- A fountain, monument or civic landmark.
- Market stalls.
- Gardens and public spaces.
- Commercial buildings grouped logically.
- A ceremonial road leading towards the royal citadel.

Use consistent setbacks and spacing appropriate to a miniature medieval settlement.

Introduce architectural variation without making the town visually chaotic.

### Acceptance standard

Each settlement should appear to have been designed by a town planner rather than populated by a random asset-placement algorithm.

## 6. Royal citadel redesign

The castle is now properly enclosed, which is an improvement. However, the courtyard is oversized and relatively empty, and the complex lacks a dramatic geographical setting.

Relocate or reconstruct the citadel on an elevated plateau overlooking the developed township.

Create a convincing fortified royal complex containing:

- A continuous outer defensive perimeter.
- Logically positioned defensive towers.
- A prominent gatehouse.
- A royal palace or castle.
- Internal roads.
- Supporting buildings.
- A ceremonial courtyard.
- Gardens or landscaped areas.
- Flags and royal decorative elements.
- A central monument, fountain or future finish location.

Ensure that the architecture is proportionate.

Reduce excessive empty space without overcrowding the complex.

The approach to the citadel should feel ceremonial, potentially incorporating:

- A rising avenue.
- A bridge.
- A fortified entrance.
- Terraced gardens.
- An ascending road.
- A sequence of defensive gates.

The primary route must eventually terminate inside the royal complex.

The citadel should be the dominant architectural landmark and the visual climax of the entire map.

## 7. Coastline and island perimeter

The current island boundary is mechanically defined by exposed hexagonal edges.

Retain the underlying modular grid, but improve the visible coastline.

Introduce:

- Sandy beaches.
- Rocky coastal sections.
- Coastal cliffs.
- Shallow-water transitions.
- Small bays.
- Jetties or docks.
- Coastal vegetation.
- Natural rock formations.
- Occasional small offshore islands where composition permits.

Different sections of the island should exhibit different coastal characteristics.

Consider subtle water colour transitions between shallow coastal water and deeper surrounding water.

Avoid making the entire island appear as a uniformly extruded tabletop slab.

The coastline should communicate that this is a miniature geographical world.

## 8. River and bridge refinement

The existing river provides a useful geographical division but lacks sufficient environmental detail.

Improve the river through:

- More natural riverbank treatment.
- Vegetation along appropriate sections.
- Exposed rocks and sandy banks.
- Subtle variations in width.
- Meaningful relationships with nearby farmland and settlements.
- Visible shallow-water transitions.
- Gentle water animation where practical.

Inspect the current bridge carefully.

Ensure that:

- The road aligns with the bridge deck.
- The bridge has adequate structural support.
- The approaches are traversable.
- The river passes naturally underneath.
- The bridge does not appear to float above disconnected road geometry.

Consider a second bridge or a small riverside settlement only if it improves the overall composition.

## 9. Forest composition

The current forest density is one of the strongest aspects of the map.

Preserve this improvement.

Refine the forests by introducing:

- Varied tree sizes.
- Different woodland densities.
- Organic forest boundaries.
- Small clearings.
- Undergrowth.
- Fallen logs and rocks.
- Forest-edge transitions.
- Occasional woodland structures.
- Meaningful openings for roads.

Avoid uniform tree spacing or repetitive rotation patterns.

Use environmental variation to distinguish ancient woodland, mountain forest and coastal vegetation.

## 10. Primary road refinement

The current road network covers a reasonable portion of the island, but its presentation remains relatively flat and uneventful.

Develop a distinctive primary adventure route that:

1. Begins in the starting village.
2. Travels through agricultural fields.
3. Enters dense woodland.
4. Crosses the river.
5. Climbs towards the mountain pass.
6. Descends towards the developed township.
7. Travels through the town's central district.
8. Ascends towards the royal citadel.
9. Passes through the gatehouse.
10. Terminates inside the royal courtyard.

The route should make extensive use of the island's geography and perimeter.

Introduce sweeping bends, meaningful changes in elevation and memorable landmark crossings.

Secondary roads should support the internal organisation of settlements.

The primary route and secondary roads should remain distinguishable without relying on intrusive glowing outlines or oversized markers.

Ensure that the road network remains compatible with the planned automatic gameplay stop-generation system.

Do not introduce visible numbered gameplay stops during this environmental refinement phase.

## 11. Lighting and rendering — highest priority

The current lighting is too muted and flat.

Substantially improve the rendering quality using a coherent miniature-diorama lighting setup.

Consider:

- Warm directional sunlight.
- Soft, natural shadows.
- Ambient occlusion.
- Contact shadows beneath buildings and vegetation.
- Subtle ambient illumination.
- Improved material response.
- Balanced colour grading.
- Higher-quality antialiasing.
- Atmospheric depth where appropriate.

The lighting should establish a clear relationship between objects and terrain.

Avoid excessive bloom, harsh shadows, washed-out colours and expensive post-processing that offers little visual benefit.

### Colour direction

Develop a richer and more intentional colour palette:

- Deep greens for dense forests.
- Warm golden tones for agricultural fields.
- Natural earth tones for roads.
- Cool greys for rocky mountains.
- Turquoise and blue tones for water.
- Warm architectural accents for settlements.
- Distinctive royal colours for the citadel.

Maintain sufficient contrast between different geographical regions.

## 12. Camera composition

Evaluate the current camera angle.

The existing view is relatively high, which reduces the visible depth of buildings, mountains and terrain elevation.

Experiment with a slightly lower orthographic or three-quarter-perspective camera angle.

The selected camera should:

- Reveal more vertical depth.
- Maintain visibility of the complete map.
- Preserve readability of the future gameplay route.
- Avoid excessive object occlusion.
- Present important landmarks at recognisable scales.
- Make effective use of a 16:9 television display.

Avoid perspective distortion that makes distant regions excessively small.

Produce at least three camera and lighting variations before selecting the strongest presentation.

## 13. Environmental detail and storytelling

Introduce meaningful environmental detail where suitable assets exist.

Examples include:

- Carts beside agricultural buildings.
- Market stalls arranged around public squares.
- Barrels and crates near commercial buildings.
- Docks beside coastal settlements.
- Fishing boats.
- Gardens.
- Fences.
- Watchtowers.
- Woodland cabins.
- Small monuments.
- Flags.
- Wells.
- Stone bridges.
- Retaining walls.

Do not add objects simply to increase asset counts.

Every decorative cluster should reinforce the identity and function of its surrounding region.

The environment should reward visual exploration.

## 14. Preserve the technical foundation

Retain the existing:

- KayKit asset-based workflow.
- Modular hexagonal terrain system.
- Declarative map configuration.
- Road connectivity architecture.
- Route-generation capabilities.
- Standalone browser rendering.
- Offline asset loading.

Update the architecture where necessary to support elevation, connected slopes, terrain transitions and coherent settlement layouts.

Do not hardcode the refined environment into the core renderer unnecessarily.

Preserve the ability to reuse the terrain system for future maps.

## 15. Mandatory visual refinement methodology

Do not approach this task as a checklist of additional objects to place.

Follow a deliberate environment-design process.

### Pass 1 — Geography

Refine:

- Terrain elevation.
- Mountain formations.
- River valleys.
- Coastline.
- Major geographical regions.

### Pass 2 — Architecture and settlement planning

Refine:

- Village layout.
- Agricultural organisation.
- Township streets.
- Market squares.
- Royal citadel.
- Road relationships.

### Pass 3 — Art direction

Refine:

- Lighting.
- Shadows.
- Materials.
- Colour grading.
- Camera angle.
- Environmental density.
- Visual hierarchy.

### Pass 4 — Final inspection

Render the complete environment and inspect it critically.

Check for:

- Floating objects.
- Intersecting buildings.
- Disconnected roads.
- Incorrect terrain transitions.
- Repetitive asset placement.
- Empty or poorly composed regions.
- Inconsistent object scales.
- Unconvincing architecture.
- Excessive visual clutter.

Resolve significant issues before concluding the exercise.

## 16. Deliverables

Provide the updated standalone map and the following full-resolution screenshots:

1. Complete environment at 1920 × 1080.
2. Elevated terrain and mountain formations.
3. Starting village.
4. Agricultural district.
5. Dense woodland.
6. River and bridge.
7. Developed township.
8. Royal citadel.
9. Coastline and harbour areas.
10. Three alternative camera and lighting configurations.
11. Before-and-after comparison with the existing implementation.

Provide a concise technical report covering:

- Changes to terrain representation.
- Elevation and road connectivity.
- Settlement planning decisions.
- Additional or modified assets.
- Lighting and rendering configuration.
- Measured browser performance.
- Asset size.
- Known limitations.

## 17. Explicit exclusions

For this iteration:

- Do not integrate with the Game Night repository.
- Do not modify the Flutter application.
- Do not implement networking.
- Do not implement multiplayer synchronisation.
- Do not develop additional maps.
- Do not introduce visible gameplay stops.
- Do not prioritise playing-piece animations.
- Do not redesign the spectator interface.
- Do not introduce paid assets without approval.

The sole objective is to produce an exceptional standalone game environment.

## 18. Final acceptance criteria

The revised environment should demonstrate:

- Meaningful terrain elevation.
- Convincing mountain formations.
- Well-planned settlements.
- Organised agricultural districts.
- Dense, natural forests.
- Attractive coastlines.
- A geographically coherent river.
- A dramatic and traversable adventure route.
- A magnificent elevated royal citadel.
- Professional lighting and shadows.
- Strong visual depth.
- Consistent architectural and environmental composition.

Target a visual quality of at least 9/10, supported by observable improvements rather than self-assigned ratings.

The completed map must look impressive without scores, tokens, numbered tiles or interface overlays.

**The hexagonal grid is the construction system. It should not define the entire visual aesthetic.**

**Stop thinking like a developer arranging assets. Think like a landscape architect, urban planner and professional game environment artist designing a miniature kingdom.**