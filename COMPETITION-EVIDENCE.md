# CAST evidence map

CAST's product claim is: **a designer plays once, asks for a mechanic change, and sees that exact play under the old and new control systems.**

## Evidence available

- `records/browser-replay/first-creation-1789428828759/`: fresh-baseline browser run with 84 real pointer frames, a real Strands proposal, identical OLD/NEW initial state and input, visible Cargo difference, Try, and Keep.
- `records/browser-replay/two-rounds-1789428885073/`: two successive real patch requests from accepted versions, candidate trial, Keep, Revert, and identical input/snapshot proofs.
- `records/browser-replay/anti-preset-1789428962799/`: an unlisted relation assembled from generic signal, condition, and position primitives, with identical replay input/snapshot and a visible result difference.
- Earlier browser captures remain under `records/browser-replay/` as historical evidence.
- `records/video/voiceover.wav`: English Google Cloud voiceover, 121.3 seconds.

## Automated runtime evidence

- Python suite: 44 passed with one dependency deprecation warning.
- Browser runtime suite: 16 passed.
- Coverage includes threshold and edge conditions, AND/OR composition, duration, occlusion, custom objects, stateful attach/detach, scene replacement and rollback synchronization, and Python/browser parity.

## Boundaries

Pointer/replay is the primary competition route. Camera/ArUco remains an input adapter and has automated tracker coverage, but a complete physical-camera acceptance record is not claimed here. A public live deployment and final competition video URL are not present in this repository.
