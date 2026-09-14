# CAST evidence map

CAST's current product claim is: **a designer plays once, asks for a
mechanic change, and sees that exact play under the old and new control
systems.**

## Evidence already available

- `records/browser-replay/1789424427412/`: real Playwright pointer input,
  real Strands/Vertex proposal, 73 recorded frames, identical initial state
  and input, and visibly different OLD/NEW Cargo outcomes.
- `records/browser-replay/first-creation-1789424115303/`: first creation from
  stage rules using a real Agent, 84 pointer frames, and deterministic replay.
- `records/browser-replay/two-rounds-1789423869980/`: two successive real
  patch requests, candidate trial, Keep, and Revert with identical
  initial-state/input proofs; tool calls and hashes are retained.
- `records/browser-replay/anti-preset-1789424616191/`: an unlisted relation
  assembled from generic signal, condition, and position primitives, with a
  saved `proof.json` and comparison screenshot (no video claim).
- `records/video/voiceover.wav`: English Google Cloud voiceover, 121.3 seconds.

## Automated runtime evidence

- Python suite: 38 passed.
- Browser runtime suite: 15 passed.
- Coverage includes threshold/edge conditions, AND/OR composition, duration,
  occlusion, custom objects, stateful attach/detach, and Python/browser parity.

## Boundaries

Pointer/replay is the active competition route. Camera/ArUco remains an input
adapter, not the current hero gate. Stronger evidence is still required for
multi-object camera recovery, persistent recording/export identity, and final
end-to-end delivery; those are not claimed complete.
