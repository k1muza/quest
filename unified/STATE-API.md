# Public state adapter (v1)

Wait for `window.quest.ready === true`. Call `window.quest.applyState(snapshot)` with a complete authoritative snapshot; no transport is assumed. `getState()` returns a defensive copy with the current countdown value. `generateStops(n)` returns independent generated stops; `at(distance)` returns world/projected coordinates and tangent. `positions()` returns score, stop (1-based), interpolation distance, target and current location. `validate(n)` checks projected separation and connectivity metadata. `reset(n)` starts a fresh local lobby. `setClean`, `setAmbient`, `setOcclusion`, `inspect(distance, zoom)` and `resetCamera` are presentation-only.

```js
quest.applyState({
  sessionId: 'session-001', phase: 'active', round: 2, totalRounds: 5,
  activeTeamId: 'blue', remainingTime: 30, timerRunning: true,
  stopCount: 40, scoreAtFinish: 60,
  teams: [
    { id: 'red', name: 'Ruby', color: '#c83f38', score: 14 },
    { id: 'blue', name: 'Sapphire', color: '#287dc5', score: 21 }
  ],
  complete: false, winnerIds: [], scoringEventId: 'round2-004'
});
```

`phase`: `lobby`, `handover`, `active`, `turn-complete`, `complete`. IDs must be unique and stable within a session; `activeTeamId` and winner IDs must refer to existing teams. The six supported colours are `#c83f38`, `#287dc5`, `#d6a137`, `#8256bb`, `#288b64`, `#d85a9a`. Unknown colours use the indexed fallback palette. Numeric symbols distinguish teams independently of colour. Optional `scoringEventId` is carried in snapshots but not needed for deduplication; scoring is absolute, not delta-based. Reapplying scores does not enqueue new movement. Snapshots should be ordered by the external session controller; a sequence or event transport is intentionally not implemented.

`remainingTime` is in seconds; when `timerRunning` is true, the browser counts down locally until a new snapshot corrects it. The local demonstration transitions to `turn-complete` at zero. An external controller can override phase. `complete: true` or `phase: 'complete'` requires explicit `winnerIds`, including multiple IDs in a tie. The operator's Final results command computes winners from the highest authoritative score. Reaching the final route stop never completes a session.

Score mapping: `stopIndex = clamp(round(score / scoreAtFinish * (stopCount - 1)), 0, stopCount-1)`. `score` is unchanged, including negative/overflow scores; only displayed location is bounded. Set `scoreAtFinish` before play to suit expected game length. Stop count and score scale lock after lobby; use a new `sessionId` to reset. New snapshots reconcile from current interpolated distance (not a historical animation queue). `applyState(snapshot, {instant:true, quiet:true})` is intended for test and setup; standard use is animated. Undo changes scores only, retaining current round and active team.

Each generated stop includes `index`, `distance`, `world` (`x,y,z`), projected `x,y`, `depth`, `elevation`, `tangent`, `angle`, and optional `milestone`. Units are the original KayKit world scaled to the 1920×1080 rendering coordinates, not metres.
