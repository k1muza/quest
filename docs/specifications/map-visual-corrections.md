# Quest — Branch Consolidation and Targeted Visual Corrections

Repository: https://github.com/k1muza/quest

## 1. Objective

Quest has undergone sufficient architectural development, visual experimentation and rendering research.

We are now transitioning from experimentation to product delivery.

The immediate objectives are to:

1. Establish a stable canonical implementation on `main`.
2. Preserve the cinematic research without introducing unnecessary production complexity.
3. Resolve three specific visual issues in Kingdom Quest.
4. Prepare a reliable foundation for subsequent multi-map development.

**Do not undertake another broad redesign, rendering investigation or architectural research exercise.**

## 2. Branch consolidation

Inspect the current repository status and the following branches:

- `main`
- `feature/unified-interactive-board`
- `research/cinematic-2.5d`

### Unified interactive board

Review `feature/unified-interactive-board` against the current `main` branch.

Confirm:

- All intended implementation changes are committed.
- The standalone HTML distribution is present and reproducible.
- Existing regression tests pass.
- No unintended changes or regressions have been introduced.
- No merge conflicts or uncommitted work will be lost.

Once validated, merge `feature/unified-interactive-board` into `main`.

The unified interactive board should become the canonical Quest implementation.

### Cinematic research

Preserve `research/cinematic-2.5d` as a historical research branch.

Do not merge it into `main`.

The research has demonstrated useful techniques, but its additional rendering profiles, alternative viewpoints, lighting variants and larger asset distribution are not required for the initial product.

Do not delete the research branch or discard its findings.

### New feature branch

After consolidating the unified board into `main`, create:

`feature/map-visual-corrections`

Base this branch on the updated `main`.

All subsequent work described in this brief must occur on this new branch.

## 3. Correction A — Rocky mountain formations

The current mountains resemble large piles of earth with small rocks placed on top.

This is visually unconvincing.

Redesign the existing mountain formations so that they are recognisably rocky mountains.

### Requirements

- Construct the main mountain formations entirely from rock-like geometry and materials.
- Introduce irregular rocky faces, angular ridges, fractured surfaces and exposed cliffs.
- Use natural variations in stone colour and shading.
- Eliminate the appearance of smooth dirt mounds.
- Remove the repetitive small decorative rocks protruding from the mountain peaks.
- Integrate smaller rocks and boulders naturally into the larger geological formations.
- Concentrate grass and vegetation around the foothills rather than across the main mountain surfaces.
- Maintain a coherent mountain range rather than creating isolated piles of rocks.

The mountains should have a strong, recognisable rocky silhouette when viewed from the default overview camera.

Do not simply recolour the existing smooth terrain grey. The geometry itself must communicate that these are rocky formations.

Use existing KayKit assets, compatible original geometry or modifications to the existing terrain-generation system where appropriate.

### Road and gameplay preservation

Preserve the existing mountain road and its general geographical course.

Ensure that:

- The road follows a believable mountain pass.
- Rocky formations do not obstruct traversable road sections.
- Gameplay markers remain visible.
- Route elevation remains accurate.
- Moving team markers do not pass through solid rock.
- Terrain transitions remain visually coherent.

Regenerate the environment background, depth map and affected route metadata together where required.

## 4. Correction B — Agricultural fields and river clearance

Several agricultural fields currently overlap or extend into the river.

Correct this throughout the entire agricultural district.

### Requirements

- Inspect the complete footprint of every agricultural plot.
- Ensure that no crop geometry, field surface, fence or farming structure unintentionally intersects the river.
- Establish a consistent minimum clearance between agricultural plots and the riverbank.
- Trim, reposition or reshape affected fields where necessary.
- Maintain organised, contiguous agricultural plots.
- Preserve reasonable access from surrounding roads and farm buildings.

Introduce a natural transition between the agricultural areas and the river.

The transition may include:

- Grass margins.
- Exposed soil.
- Reeds.
- Shrubs.
- Small rocks.
- Narrow farm paths.

The river should appear as an independent geographical feature with recognisable banks.

Do not solve this problem by reducing the river width or unnecessarily changing its course.

### Validation

Where practical, implement a reusable geometric validation check comparing complete agricultural footprints against river and riverbank exclusion polygons.

Checking only the centre point of each field is insufficient.

This validation should also be useful when producing future maps.

## 5. Correction C — Replace chess pieces with floating team markers

The current chess-piece-style pawns are no longer the preferred visual direction.

Replace them with attractive, floating, bouncing team-location markers.

The markers should feel playful, modern and highly readable on a television.

They should be suitable for use across all future Quest maps, regardless of theme.

### Visual direction

Explore a small number of focused marker designs, such as:

- Floating coloured medallions.
- Rounded three-dimensional badges.
- Hovering location markers.
- Gem-like team tokens.

Select and implement the strongest design.

The markers should include:

- A distinctive team colour.
- A clearly readable team number or symbol.
- Subtle dimensional shading.
- A visible outline.
- A soft ground shadow.
- A clear indication of the exact stopping position.
- A distinctive active-team state.

Avoid:

- Chess pieces.
- Human-shaped pawns.
- Large character models.
- Flat, generic circles.
- Excessive neon effects.
- Oversized markers that obscure the environment.
- Visual styling specific to the medieval theme.

The markers should resemble polished game-world indicators rather than ordinary interface icons.

### Idle animation

When stationary, each marker should gently hover and bob above its assigned stopping position.

Use:

- Subtle vertical oscillation.
- Smooth easing.
- Slightly varied animation phases.
- Ground shadows that respond naturally to hover height.

Avoid exaggerated or distracting continuous bouncing.

### Movement animation

When a team earns points, its marker should travel along the actual route.

Implement:

- Smooth forward and backward movement.
- Playful bouncing or hopping.
- Controlled acceleration and deceleration.
- A satisfying arrival animation.
- Subtle destination highlighting.

The marker must remain associated with the correct route position throughout the animation.

Preserve the existing rapid-event reconciliation and undo behaviour.

Do not introduce an unbounded animation queue.

### Active-team emphasis

The active team's marker should be immediately identifiable.

Consider:

- A restrained pulsing ring.
- A slightly brighter outline.
- A subtle glow.
- A small active-team indicator.

Inactive markers should remain clearly visible.

### Foreground visibility

Floating markers are primarily spectator information indicators rather than physical objects travelling at ground level.

Their visibility is therefore more important than strict physical occlusion.

Retain depth-aware rendering where it improves the presentation, but ensure that team identity is not lost behind trees, buildings, mountains or castle walls.

Use a visible identity indicator or adjusted hover placement where necessary.

The marker's ground anchor must remain associated with the actual stopping position.

### Tied positions

Improve the presentation of multiple teams occupying the same stop.

Support two to six tied teams using a stable arrangement of floating markers.

Ensure that:

- Every team remains identifiable.
- Markers do not excessively obscure one another.
- The shared stopping position remains obvious.
- The arrangement works at bridges, mountain passes, village roads and castle entrances.
- Markers do not incorrectly imply that tied teams occupy different gameplay stops.

Evaluate compact clustering, staggered hover heights or other appropriate arrangements.

Do not rely solely on an additional roster to compensate for completely hidden team markers.

## 6. Preserve existing functionality

The following capabilities must remain operational:

- Automatic generation of 30, 40, 50 and 60 stopping positions.
- Elevation-aware route geometry.
- Two to six competing teams.
- Authoritative score handling.
- Forward and backward movement.
- Undo.
- Rapid scoring reconciliation.
- Tied positions.
- Public game-state interface.
- Timer.
- Scoreboard.
- Active-team presentation.
- Winner presentation.
- Clean-map mode.
- Fullscreen presentation.
- Offline operation.
- Standalone HTML distribution.

Do not introduce new game rules.

## 7. Performance and architecture

Retain the established lightweight 2.5D architecture.

Use the existing offline environment-rendering pipeline and Canvas 2D runtime.

Do not introduce mandatory:

- Three.js.
- WebGL.
- Real-time 3D rendering.
- Blender runtime dependencies.
- External services.
- CDN dependencies.

Keep the runtime distribution reasonably compact.

The new floating marker implementation should be reusable across future maps.

Separate marker appearance and animation from map-specific geometry.

Do not implement the complete multi-map architecture during this iteration, but avoid introducing further Kingdom Quest-specific dependencies.

## 8. Visual quality assurance

Inspect the actual rendered implementation rather than relying exclusively on automated tests.

Provide before-and-after comparisons for:

1. Complete Kingdom Quest map.
2. Mountain formations.
3. Mountain road and surrounding rocky terrain.
4. Agricultural district and riverbank.
5. Old chess pieces versus new floating markers.

Provide additional screenshots showing:

- Four teams distributed across the map.
- Six teams distributed across the map.
- Six teams sharing the same stop.
- Markers at the mountain pass.
- Markers crossing the bridge.
- Markers entering the royal citadel.
- Active-team highlighting.
- Winner presentation.

Produce a short browser-recorded demonstration showing the new markers hovering, bouncing and travelling along the route.

Inspect the result at 1920 × 1080 and 1280 × 720 resolutions.

## 9. Regression testing

Re-run the existing unified board regression suite.

Extend validation to cover:

- Agricultural footprint and river intersection checks.
- Mountain route alignment.
- Updated elevation and depth-map consistency.
- Floating marker positioning.
- Marker visibility.
- Tied-team arrangements.
- Forward and backward animation.
- Rapid scoring.
- Undo operations.
- Responsive rendering.
- Offline operation.
- Absence of JavaScript errors.

Report actual test results.

Do not claim that physical Smart TV compatibility has been established unless tested on actual television hardware.

## 10. Deliverables

Commit and push the completed implementation to:

`feature/map-visual-corrections`

Include:

- Updated environment-generation source.
- Corrected mountain geometry and materials.
- Corrected agricultural layout.
- Updated rendered environment.
- Matching depth and route data.
- Reusable floating marker renderer.
- Marker animation implementation.
- Updated standalone HTML distribution.
- Regression test results.
- Before-and-after screenshots.
- Recorded browser demonstration.
- Updated README.
- Concise implementation report.

Document any remaining limitations.

Do not merge the visual corrections branch into `main` until it has been reviewed and approved.

## 11. Explicit exclusions

Do not:

- Create additional maps.
- Implement Game Night integration.
- Modify the Game Night repository.
- Introduce networking.
- Resume cinematic rendering research.
- Investigate alternative camera perspectives.
- Introduce day/night rendering.
- Redesign the entire landscape.
- Rebuild functioning gameplay architecture.
- Introduce paid assets.
- Expand the scope beyond the three identified visual corrections.

## Final acceptance standard

The revised Kingdom Quest map should retain its established identity while resolving three clear visual deficiencies:

1. Mountains that genuinely resemble rugged rock formations.
2. Agricultural fields that respect natural river boundaries.
3. Distinctive floating, bouncing team markers that are attractive and readable during gameplay.

Once these objectives are achieved and regression tests pass, conclude the iteration.

Do not introduce additional refinement cycles merely to pursue an arbitrary visual rating.

**Consolidate the branches. Fix the three problems. Preserve functionality. Deliver a working implementation.**