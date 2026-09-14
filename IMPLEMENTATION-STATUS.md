# CAST current status

## Current user-approved objective

CAST is a Live Playtest Agent for game / interaction designers: play once, request a mechanic change, execute the exact same recorded input from the same initial world under OLD and NEW rules, try the candidate, keep/revert/revise. The complete 17-section product goal in the conversation supersedes the original camera-theatre attachment. Only section 3 was replaced with the Competition Video Goal; all other sections remain in scope. The video is a required 3–4 minute English competition submission (under 5 minutes), opening with a 20–30 second hero segment. A finished video alone does not complete the product goal.

Camera/ArUco development is paused. Main experience is a playable graybox with Player, Cargo and Goal; no commercial-game integration. Model calls remain serial. Do not request repeated user camera/button testing.

## Verified now

- Mac app: `/Users/mixu/Desktop/CAST`, http://127.0.0.1:8765 . VPS source: this directory.
- Real Strands/Vertex previously generated and installed attach then detach mechanics, installed revision 15. Those API records alone are not a complete browser acceptance test.
- New browser evidence: `records/browser-replay/1789423519310/evidence.json`, screenshots and WebM. Real Playwright mouse input recorded 73 frames; real Agent removed speed-triggered release; both API replays used identical initial state and input. OLD Cargo finished at x≈0.630; NEW at x≈0.895. Browser comparison shown; Try Candidate entered; discard restored installed mechanic. No page errors.
- Failed trials are retained: one candidate changed nothing and another incorrectly claimed the current rules already matched a request. Do not describe these as successes or anti-preset proof.
- Actual cause of absent recording was synthetic PointerEvent dispatch: setPointerCapture threw before snapshot creation. The earlier cache-root-cause claim was not supported. Browser automation now uses actual mouse events.
- Pointer speed now uses elapsed time, with a scene reference for distance. Each runtime recalculates distance against its own world. Replay uses relative timestamps, not a fixed 40 ms playback rate.
- Recorded play is copied before Agent generation, so continued play cannot replace the comparison input. Candidate discard restores the installed rules/scene even after trying the candidate.
- Python/browser parity test covers far+slow, near+fast, near+slow, following, release and retention. Latest suite: 40 passed, 1 warning; browser runtime suite: 16 passed.

- Continuous browser two-round evidence: `records/browser-replay/two-rounds-1789423869980/`. From installed revision 16, real Agent added a release rule (Keep → 17), then removed it on a new request (Keep → 18). Both pairs used identical initial state/input, visibly different cargo outcomes. The browser physically dragged the trial candidate before each Keep. Revert restored the prior rules as revision 19. No reload within the sequence, no page errors. `agent-tool-flow.json` records both real propose_rule_patch calls; `proof-summary.json` contains snapshot/input/rules SHA-256 values. Raw WebM and screenshots are retained. Comparison now uses the same Player/Cargo/Goal renderer as live play, including outcome-derived Delivered status.

- Latest English-only hero capture: `records/browser-replay/1789424427412/`. A real mouse play (73 frames) was followed by a real Strands request to add a fast-release rule. OLD finished with Cargo delivered at x≈0.895; NEW released it at x≈0.630. The screenshot and WebM contain no Chinese UI text and show the Goal/Delivered state.

## Remaining acceptance work (not complete)

- Browser first creation from a fresh baseline now has evidence in `records/browser-replay/first-creation-1789428828759/`: 84 real pointer frames, real Agent attach proposal, identical OLD/NEW input and snapshot, visible Cargo difference, Try and Keep.
- Browser two-round revision/Keep/Revert now also has fresh evidence in `records/browser-replay/two-rounds-1789428885073/`; generic anti-preset composition is recorded in `records/browser-replay/anti-preset-1789428962799/`.
- Strengthen Agent semantic reliability, especially negated/reversed requests and false unchanged claims. No hardcoded fallback.
- Trial dragging and Keep/Revert were exercised in the continuous sequence; retain and review these screenshots/video for the final demonstration.
- Finish persistent recording/export and auditable input/version identity; current browser evidence captures the raw requests/results externally.
- Replay controls, coherent ready/error state, scene context alignment, and target validation need review. The prior uppercase-only target heuristic does not prove registered-object validation.
- Completed silent hero check, public source, English submission/README, architecture/Strands evidence, and full 3–4 minute video are still outstanding. Current raw WebM files are evidence, not the final video.

## Operational notes

Gateway runs on VPS 127.0.0.1:8877; VPS-initiated SSH reverse forwarding exposes it on Mac 127.0.0.1:18765. Mac app must start with CAST_AGENT_URL set (scripts/start-mac.sh). Do not initiate the tunnel toward the Mac's own IP from the Mac. Gateway hard ceiling and configured run budget are now 100, with usage history preserved. Do not regenerate a successful proposal merely to install it: install the actual returned candidate once.

Previous camera-focused status is archived in docs/status-before-pointer-replay.md; it is not the active roadmap.

## Verification update (2026-09-15)

- Restored safe offline provider semantics: library/tests default to disabled Bedrock unless `CAST_PROVIDER=vertex` (the production gateway launcher sets Vertex explicitly). This prevents unconfigured imports from consuming model quota or fabricating proposals.
- Full Python suite: 38 passed, 1 warning.
- Google Cloud Text-to-Speech API enabled for project `ata-creative-change-2026`; English voiceover generated at `records/video/voiceover.wav` (121.3 seconds).
- Browser runtime suite: 15 passed (`node --test tests/tracking.test.mjs`).
- Added explicit Play, Pause, and Replay controls to the OLD/NEW comparison; controls stay synchronized to the recorded frame sequence. Browser module syntax and 15 runtime tests pass. Synced updated static files to Mac.
- Browser export now packages the latest real play recording (UUID, initial snapshot, ordered timestamped input frames, ruleset/version) together with the server's scene/rules/audit export; synced to Mac and syntax-checked.
- Replay now rejects rules targeting objects absent from the captured initial snapshot/current registered scene, preventing phantom actors from corrupting OLD/NEW comparisons. Python suite remains 38 passed; synced to Mac.
- Added regression coverage for replay phantom-target rejection; Python suite now 39 passed.
- `scripts/demo_probe.py` rerun successfully: isolated scene registration → preview → explanation → install → runtime signal → patch → rollback → export (`cast-performance-v1`).
- Imported the user's `CAST-完整提交文案.md` as internal `docs/CAST-submission-copy-source.md`. It is source material only; placeholder fields and conditional release claims remain unpublished until corresponding runtime evidence exists.
- Completed the MIT license disclaimer using the standard full text; the public source license no longer has the truncated warranty clause.
- Added `THIRD-PARTY-NOTICES.md` documenting upstream dependency licensing and optional providers/adapters.
- Rendered the architecture source to `docs/architecture.svg` and `docs/architecture.png` with Graphviz; linked both from `docs/ARCHITECTURE.md`.
- Persisted the latest pointer play in browser localStorage, restoring it after reload and including it in export; Reset clears the persisted recording. Syntax-checked and synced to Mac.
- Real browser reload check restored a persisted two-frame play (`Play restored · 2 input frames`) with no page errors; persistence is verified without a model request.
- Added explicit browser tracker occlusion boundary coverage: last signal is held for the 350 ms recovery window and then becomes invisible. Browser suite now 16 passed.
- Generated `records/video/artifact-manifest.json` with SHA-256 and byte sizes for release docs, architecture renders, voiceover, and product-cut assets.
- Added `product-cut-with-full-voiceover.webm`: the real 98.32 s product cut is extended with its final frame so the complete 121.34 s Google Cloud narration is preserved; artifact manifest updated.
- Worker finished `records/video/competition-cut-draft-with-voiceover.webm` and copied it to Mac as `/Users/mixu/Desktop/CAST-competition-cut-draft.webm`. Verified duration 226.008 s (3:46), 1440x1080 VP9 + 48 kHz mono Opus, 35,157,336 bytes; SHA-256 `afe5c23a8081f96e9f2bc1862bf23d10d6fe5b0177be28196e33b75013ca38e7` on both sides. This remains a draft requiring visual/audio review before submission.

- Verification refresh: Python `pytest -q` reports 40 passed with one dependency deprecation warning; `node --test tests/*.test.mjs` reports 16 passed. `static/stage.mjs` and `static/tracking.mjs` pass syntax checks and Python modules compile cleanly. README was aligned with the pointer/replay competition path.
- Fresh acceptance refresh: Python `pytest -q` reports 44 passed with one dependency deprecation warning. Real browser first creation, two-round patch, and anti-preset evidence were generated and pushed in commits `baeb2f6`, `0c339f9`, and `e61772e`.
- Scene replacement and rollback now synchronize the live runtime namespace while preserving state for surviving object identities; regression suite reports 44 passed. English Vertex/Strands documentation is current in `docs/VERTEX.md`.
- Public source snapshot `v0.1.1` is tagged and published as a GitHub Release; release notes point judges to the documented local run path and explicitly avoid claiming a hosted demo.
