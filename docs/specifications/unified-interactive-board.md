# Kingdom Quest — Unified Interactive Board and Presentation

Repository: https://github.com/k1muza/quest

Baseline commit: `92b5173dcf6f4dfa31b1e0127eff4cfc492faa2b`

Latest environment reference:
https://github.com/k1muza/quest/blob/main/environment/screenshots/01-environment.jpg

## 1. Background and objective

The latest Kingdom Quest environment has been reviewed and provisionally rated **8.4/10 for visual quality**.

The terrain elevation, forest density, agricultural organisation, coastline, township planning and lighting represent substantial improvements over earlier iterations.

The current environment is sufficiently developed to proceed with interactive gameplay presentation.

**Do not undertake another comprehensive environmental redesign.**

The primary objective of this iteration is to unify the latest environment with the existing interactive board functionality, producing a polished, animated, standalone spectator experience.

The project must remain independent of Game Night and Flutter during this phase.

## 2. Inspect and consolidate the existing architecture

The repository currently contains two editions:

- `environment/` — latest environment, improved terrain, architecture, lighting and camera projection.
- `gameplay/` — earlier interactive implementation containing team management, automatic stopping positions, movement animations and demonstration controls.

Inspect both implementations before making changes.

Identify reusable components and differences in:

- Terrain representation.
- World coordinates.
- Camera projection.
- Route geometry.
- Elevation sampling.
- Stop generation.
- Playing-piece rendering.
- Animation systems.
- Browser presentation.
- Asset bundling.

Establish a single canonical interactive implementation that uses the latest environment.

Do not maintain two independent gameplay engines indefinitely.

Preserve the existing editions as historical references until the unified implementation has been validated.

Avoid unnecessary architectural rewrites. Reuse functioning components wherever practical.

## 3. Preserve the latest environment

Use the latest environment as the visual foundation.

Preserve:

- The sculpted terrain heightfield.
- Connected mountain formations.
- Dense western forests.
- Agricultural fields.
- Improved township organisation.
- Continuous river.
- Existing bridge crossing.
- Coastline.
- Royal citadel.
- Current camera composition.
- Warm lighting and baked shadows.

The approved environment must not regress as a consequence of introducing gameplay overlays.

Minor environmental refinements are permitted where they directly improve movement visibility, geographical coherence or presentation.

## 4. Limited environmental finishing touches

Address the following targeted issues only where they can be resolved without another broad redesign.

### Mountains

Reduce the artificial appearance of small rocks protruding from the upper mountain ridge.

Integrate exposed rock formations more naturally into the terrain.

### Royal citadel

Improve the ceremonial entrance and internal courtyard composition.

Ensure that the primary route passes through the actual gate opening and terminates at a recognisable destination within the courtyard.

Consider a royal monument, trophy platform, fountain or treasure display.

### Township

Introduce a more recognisable central public square if space permits.

Reduce obvious building repetition through subtle architectural variations and thoughtful arrangement.

### Waterfront

Improve the existing harbour area with a coherent arrangement of docks, boats and waterfront structures.

These are secondary refinements. Do not allow them to delay the interactive implementation.

## 5. Rendering architecture

Retain the existing offline-rendered 2.5D approach.

The latest environment is rendered from genuine KayKit geometry using an offline Python rendering pipeline.

This is an appropriate architectural foundation for eventual Smart TV deployment.

The interactive browser presentation should consist of independently managed rendering layers:

1. Pre-rendered environmental background.
2. Dynamic gameplay stopping markers.
3. Ground-level effects and token shadows.
4. Animated team playing pieces.
5. Foreground occlusion layers.
6. Ambient environmental animations.
7. Spectator information and celebration effects.

The map background must remain visually sophisticated while interactive elements are rendered independently.

Do not introduce a mandatory real-time WebGL or Three.js runtime.

Retain the ability to rebuild the environment from its declarative source configuration.

## 6. Accurate route projection

Reuse the validated primary route from the latest environment.

The route currently contains elevation-aware geometry and a reported arc length of approximately 3,071 world units.

Ensure that the complete playable route follows:

- The actual road centreline.
- Terrain elevation.
- Bridge deck elevation.
- Mountain passes.
- Township roads.
- The citadel entrance.
- The final courtyard destination.

Use the same camera projection as the rendered environment when converting world coordinates into screen coordinates.

Do not manually approximate screen-space positions where accurate world-space geometry is already available.

All projected coordinates must remain aligned with the environment when the presentation is resized, zoomed or panned.

## 7. Automatic stopping-position generation

Restore the automatic stop-generation functionality from the earlier gameplay edition, using the latest route geometry and camera projection.

Support the previously validated configurations:

- 30 stops.
- 40 stops.
- 50 stops.
- 60 stops.

Use 40 stops as the initial demonstration default.

Generate positions based on cumulative distance along the actual three-dimensional road centreline.

Each stop should contain sufficient metadata to support:

- Sequential index.
- World-space position.
- Projected screen position.
- Surface elevation.
- Direction of travel.
- Distance along the route.
- Local route tangent.
- Milestone classification where applicable.

The terrain grid and gameplay stops must remain independent.

Changing the number of stopping positions must not require rebuilding the environment.

Validate that generated stops:

- Are positioned on traversable surfaces.
- Follow the actual road.
- Maintain sufficient spacing.
- Do not overlap excessively.
- Do not intersect environmental obstacles.
- Remain visible at television resolutions.

Changing the stop configuration should be restricted to demonstration setup or an explicit reset, rather than unexpectedly repositioning teams during an active game.

## 8. Design premium stopping markers

The stopping positions should resemble physical elements integrated into the road.

Explore suitable visual treatments such as:

- Small engraved stone discs.
- Raised cobblestone platforms.
- Numbered stepping stones.
- Bronze road plaques.
- Medieval milestone markers.

Create a cohesive visual style that complements the KayKit environment.

Requirements:

- Clear numbering.
- Strong contrast against the road.
- Consistent perspective.
- Subtle physical depth.
- Appropriate shadows.
- Readability from several metres away.

Important milestone stops may use distinctive materials or decorative accents.

The starting and final positions should be immediately recognisable.

Avoid oversized markers that cover substantial portions of the road or diminish the environment.

Provide a clean-map mode that hides all gameplay markers.

## 9. Premium team playing pieces

Develop attractive team pieces that resemble collectible physical board game tokens.

Use rendered 3D assets wherever practical.

Consider classic miniature pawns, medieval adventurers, heraldic figures or other stylised objects consistent with the map.

Use complementary CC0 assets or create original models where necessary.

Support up to six teams with clearly differentiated colours:

- Red.
- Blue.
- Gold.
- Purple.
- Green.
- Pink or another sufficiently distinct colour.

Do not rely exclusively on colour to distinguish teams. Include identifiable symbols, shapes, labels or numbered accents.

Each playing piece should have:

- A convincing three-dimensional appearance.
- A clearly defined ground-contact point.
- Appropriate lighting.
- Subtle contact shadows.
- Consistent scale.
- Strong readability.
- An active-team visual state.

The pieces should be sufficiently large for television viewing without overwhelming the map.

Avoid basic coloured circles containing team initials.

## 10. Team positioning and tied scores

Support two to six competing teams.

When teams occupy different stops, their pieces should align naturally with the road.

When multiple teams occupy the same stop, implement a stable local formation system that keeps every team visible.

The formation system should:

- Use offsets relative to the local direction of the route.
- Preserve each piece's association with its stop.
- Avoid overlapping adjacent stopping markers.
- Minimise overlap between pieces.
- Remain stable when teams join or leave a tied position.
- Work with two, three, four, five and six tied teams.

Where the road is narrow, use visual clustering or carefully arranged offsets rather than placing pieces inside buildings, trees or water.

Test six-team ties at:

- The starting position.
- Ordinary road sections.
- The bridge.
- Mountain passes.
- The citadel entrance.
- The final courtyard.

## 11. Natural movement animations

Playing pieces must move along the actual route rather than teleporting between stops.

Implement satisfying board-game-style movement.

Consider:

- Small hopping movements.
- Smooth acceleration and deceleration.
- Controlled landing effects.
- Directional rotation where appropriate.
- Subtle squash-and-stretch.
- Brief illumination of the destination marker.

Movement across several stops should follow the intervening road geometry.

The piece must not move directly through buildings, mountains, rivers or other obstacles.

Movement on elevated terrain must reflect the route's changing projected elevation.

Support:

- Forward movement.
- Backward movement.
- Multi-stop movement.
- Undo.
- Direct repositioning.
- Rapid successive movement commands.

The animation engine must reconcile with the latest commanded position.

Avoid an unbounded animation queue when several points are awarded rapidly.

Prioritise accurate visual state over playing every historical animation in full.

## 12. Foreground occlusion — critical requirement

The existing pre-rendered environment must support convincing interaction between moving pieces and scenery.

A playing piece should not appear to float over the top of a tree, building, bridge railing or castle wall when it is actually travelling behind that object.

Extend the offline rendering pipeline to produce suitable occlusion data.

Evaluate approaches including:

- Transparent foreground sprites.
- Scene depth maps.
- Per-object masks.
- Route-specific occlusion masks.
- Depth-aware layered compositing.

Select the approach that provides the best balance of visual correctness, performance and maintainability.

At minimum, support correct occlusion around:

- Forest edges.
- Tall buildings near the road.
- Mountain passages.
- Bridge railings where applicable.
- The royal gatehouse.
- The citadel walls.

Ensure that:

- Objects in front of a token correctly obscure it.
- Objects behind a token do not obscure it.
- A token entering the citadel appears to pass through the gate rather than over the wall.
- Token shadows respect the underlying visible surface where practical.

Avoid a simplistic global foreground overlay that incorrectly hides pieces regardless of their location.

Preserve sufficient spectator visibility. Do not design route sections where pieces disappear for unnecessarily long periods.

Document the chosen occlusion technique and its limitations.

## 13. Environmental animation

Introduce subtle environmental movement to make the kingdom feel alive.

Prioritise the following effects:

### Water

- Gentle river flow.
- Subtle water highlights.
- Slow-moving coastal ripples.
- Light reflections near the shoreline.

### Windmills

Animate windmill blades where the existing models and composition support separate rendering.

### Flags

Introduce restrained flag movement near the royal citadel and important buildings.

### Settlement activity

Consider occasional chimney smoke or other subtle signs of habitation.

### Atmospheric effects

Consider slow-moving cloud shadows or occasional birds.

These animations must be secondary to gameplay.

Avoid excessive particle effects, constant environmental movement or distracting visual noise.

Separate animated environmental assets from the baked background where required.

Provide a setting to disable ambient animation for low-performance devices.

## 14. Spectator interface

Introduce a polished, minimal television interface that complements the kingdom.

Display:

- Game or demonstration title.
- Current round.
- Active team.
- Countdown timer.
- Team names and scores.
- Connection or presentation status where appropriate.

The map should remain the dominant visual element.

Design for:

- 1280 × 720.
- 1920 × 1080.
- 3840 × 2160.

Preserve safe margins for televisions with overscan.

Use bold, modern, highly legible typography.

Avoid:

- Oversized dashboard cards.
- Excessive decorative borders.
- Intrusive interface overlays.
- Small text intended for desktop viewing distances.
- Team information that obscures important scenery.

The interface should feel like a professionally designed tabletop game presentation.

Keep the primary gameplay controls separate from spectator mode.

## 15. Presentation states

Implement visually polished transitions between the following states.

### Lobby

Present the kingdom and competing teams.

All playing pieces should gather at the starting location.

### Team handover

Briefly highlight the upcoming team.

Preserve visibility of the map and other teams.

### Active turn

Display the countdown, active team and animated scoring progression.

### Turn completion

Briefly summarise the team's performance.

### Milestone arrival

Introduce a tasteful celebration when a team reaches a significant location.

Possible effects include:

- A brief glow.
- A small banner.
- A landmark highlight.
- A short sound effect.

Milestones must remain decorative and must not modify scoring.

### Lead change

Celebrate a new leader with a brief, unobtrusive notification.

### Final results

Create a memorable winner presentation using the royal citadel and surrounding environment.

Consider:

- A ceremonial spotlight.
- Royal flags.
- Celebratory particles.
- A trophy presentation.
- A short cinematic transition.

Do not automatically declare a winner merely because a team reaches the final decorative stop.

The demonstration's authoritative game state determines the winner.

## 16. Scoring and route capacity

The eventual Game Night integration will use round-based scoring rather than a fixed race-to-the-finish mechanic.

Do not assume that the highest possible game score equals the number of available stopping positions.

For the standalone demonstration, maintain separate values for:

- Authoritative team score.
- Displayed route position.
- Animation target.
- Current interpolated position.

Define and document a sensible score-to-position mapping strategy.

Account for:

- Negative scores.
- Scores exceeding the available number of stops.
- Tied scores.
- Different game lengths.
- Undo operations.

Do not silently cap authoritative scores.

Do not unexpectedly redistribute every team's position whenever the leader earns another point.

A fixed pre-game scale, extended route or clearly communicated lap system may be evaluated.

Keep the mapping strategy replaceable so the future Game Night integration can determine the appropriate progression model.

## 17. Standalone demonstration controls

Provide a collapsible operator panel supporting:

- Configure two to six teams.
- Edit team names.
- Choose team colours.
- Select the active team.
- Configure 30, 40, 50 or 60 stops.
- Start a demonstration game.
- Award one point.
- Award three points.
- Award five points.
- Deduct points.
- Undo.
- Set a score directly.
- Create tied scores.
- Simulate rapid scoring.
- Advance to the next team.
- Advance rounds.
- Start, pause and reset the countdown.
- Trigger milestone celebrations.
- Trigger the winner presentation.
- Toggle environmental animations.
- Toggle foreground occlusion for debugging.
- Toggle clean-map mode.
- Reset the demonstration.
- Reset the camera.
- Enter fullscreen mode.

Normal television presentation must not display the operator panel.

Ensure that the controls are usable on desktop browsers without requiring external services.

## 18. Public game-state interface

Although networking integration is explicitly excluded, prepare the unified board for future external state updates.

Define a clean, documented interface through which an external application could supply:

- Session identifier.
- Game phase.
- Current round.
- Total rounds.
- Active team identifier.
- Remaining time.
- Team identifiers.
- Team names.
- Team colours.
- Authoritative scores.
- Session completion state.
- Winner identifiers.
- Optional scoring event identifiers.

Separate external state application from demonstration controls.

The demonstration panel should operate through the same state interface that a future Game Night integration would use.

Avoid coupling the renderer directly to a specific scoring implementation.

The renderer should be capable of applying a complete state snapshot and reconciling the visual presentation with it.

No WebSocket server, device pairing or Flutter code should be implemented during this phase.

## 19. Performance requirements

The eventual target remains a Smart TV browser receiving the board from a locally hosted HTTP server.

Maintain:

- Complete offline operation.
- Locally bundled assets.
- No mandatory external CDN dependencies.
- No mandatory WebGL.
- Efficient 2D rendering.
- Cached static environment layers.
- Lightweight animations.
- Reasonable memory consumption.
- Responsive landscape presentation.

Do not redraw the complete static environment unnecessarily.

Use efficient compositing and minimise expensive per-frame operations.

Evaluate suitable quality settings for:

- Background image resolution.
- Rendering resolution.
- Ambient animation.
- Particle effects.
- Token shadows.
- Occlusion quality.

The previous environment-only edition reports a standalone HTML size of approximately 1.66 MB.

Measure the size of the unified implementation and explain any substantial increase.

Aim to retain a compact runtime distribution without sacrificing visual quality.

Chromium benchmark results must not be represented as proof of Smart TV compatibility.

## 20. Regression testing and validation

Preserve the previous geometry and connectivity validation.

Extend testing to cover the unified implementation.

Verify:

- All supported stop configurations.
- Accurate projection onto the latest environment.
- Correct bridge crossing.
- Correct movement over elevated terrain.
- Citadel gate traversal.
- Foreground occlusion.
- Two to six competing teams.
- Multiple teams occupying the same stop.
- Forward and backward movement.
- Undo operations.
- Rapid score changes.
- Negative scores.
- Scores beyond nominal route capacity.
- State snapshot reconciliation.
- Timer behaviour.
- Presentation state transitions.
- Winner presentation.
- Fullscreen operation.
- Clean-map mode.
- Offline loading.
- Responsive presentation.
- Absence of JavaScript errors.

Test the actual bundled standalone implementation, not merely the modular development version.

Document the test environment and limitations.

## 21. Mandatory visual quality assurance

Perform actual browser rendering and screenshot inspection.

Undertake at least three meaningful refinement passes.

### Pass 1 — Integration

Confirm that the latest environment, route projection, stop positions and team pieces work together.

### Pass 2 — Visual polish

Refine markers, token materials, scale, shadows, foreground occlusion, interface composition and movement.

### Pass 3 — Presentation

Refine environmental animations, lead changes, milestone effects, winner celebrations and television readability.

Do not consider implementation complete merely because all controls function.

The result must look like a cohesive, commercially presentable interactive game.

## 22. Deliverables

Provide the following within the Quest repository:

- A canonical unified interactive board implementation.
- A standalone HTML distribution.
- Updated build and bundling scripts.
- Reusable map configuration.
- Route and stopping-position metadata.
- Playing-piece assets.
- Foreground occlusion assets or data.
- Environmental animation assets.
- Public game-state interface documentation.
- Updated README.
- Updated technical report.
- Automated validation results.
- Asset and licensing documentation.

Provide full-resolution screenshots showing:

1. Clean environment.
2. Board with stopping markers.
3. Four competing teams.
4. Six competing teams.
5. Six teams sharing one stop.
6. Movement across the bridge.
7. Movement through the forest.
8. Movement through the mountain pass.
9. Entry through the royal gatehouse.
10. Final courtyard arrival.
11. Active gameplay presentation.
12. Winner celebration.

Where practical, provide a short recorded demonstration of token movement and environmental animation.

Report measured:

- Runtime bundle size.
- Browser frame cadence.
- Initial loading time.
- Memory consumption where measurable.
- Validation results.
- Known compatibility limitations.

## 23. Repository management

Create a dedicated feature branch:

`feature/unified-interactive-board`

Commit the completed implementation and push the branch to GitHub.

Preserve the current main branch until the unified implementation has been reviewed.

Do not merge into main without approval.

## 24. Explicit exclusions

For this phase:

- Do not modify `k1muza/game-night`.
- Do not integrate with Flutter.
- Do not implement local networking.
- Do not implement WebSocket communication.
- Do not implement device pairing.
- Do not implement cloud services.
- Do not introduce paid assets without approval.
- Do not develop additional maps.
- Do not undertake another comprehensive terrain redesign.
- Do not replace the established rendering pipeline without a compelling demonstrated reason.

## Final acceptance standard

The finished Kingdom Quest experience should resemble a beautifully rendered physical miniature kingdom brought to life through interactive board-game mechanics.

Spectators should see distinctive team pieces travelling through forests, crossing bridges, navigating mountain passes, entering settlements and ultimately arriving at a magnificent royal citadel.

The environment, stopping positions, moving pieces, occlusion, lighting and interface should feel like components of the same world.

The complete experience should run offline in a lightweight browser application.

**Preserve the kingdom. Unify the architecture. Bring the board to life.**