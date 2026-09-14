# CAST Competition Video Script

Target length: 3:20–3:50. Keep the product visible for roughly 75% of the video. Record the browser at 1440p or 1080p. Use English captions throughout.

## 0:00–0:25 — Hero (minimal voice)

**Picture:** The graybox prototype is already running. The designer drags Player through Cargo and into Goal. The current mechanic leaves Cargo behind. Show `PLAYTEST 01` briefly.

**Voiceover (one sentence):** “CAST lets designers test a mechanic change against the exact play that made them want the change.”

**Action:** Enter: “When Player moves quickly, detach Cargo and leave it where it was. Keep the existing slow approach attachment mechanic.” Show the candidate state, then the two canvases.

**On-screen:** `SAME INITIAL STATE` · `SAME RECORDED INPUT` · `OLD | NEW`

**Picture:** OLD carries Cargo into `DELIVERED`; NEW releases Cargo at the fast movement. Do not explain the difference verbally.

## 0:25–0:45 — The problem

**Picture:** Simple text animation beside the live product.

**Voiceover:** “In a normal playtest, a designer notices a bad interaction, leaves the prototype, edits the implementation, rebuilds, and then tries to recreate the moment. The expensive part is not only changing the rule. It is finding out what that same play would have felt like under the new rule.”

**On-screen:** `PLAY → NOTICE → EDIT → REBUILD → RECREATE → PLAY AGAIN` then `PLAY → DESCRIBE → COMPARE`

## 0:45–1:45 — One real product flow

**Picture:** Real pointer drag. The interface shows `Recording play…` and then `Play recorded`.

**Voiceover:** “The designer plays once with a real pointer. CAST records the initial world, the ordered input frames, timing, and the active mechanic version. The designer describes the change in human language while the prototype remains available.”

**Picture:** Agent request and compact candidate explanation. Do not linger on JSON.

**Voiceover:** “The Strands Agent reads the current scene and rules, preserves unrelated behavior, and constructs a candidate from constrained control primitives. It does not select a named effect.”

**Picture:** `OLD | NEW` replay, synchronized.

**Voiceover:** “CAST restores the same initial state and feeds the same recorded input to both rulesets. Only the mechanic changes.”

**Action:** Click `Try new version`, drag Player in the candidate, then click `Keep new mechanic`.

**Voiceover:** “The candidate is a real running mechanic. The designer can try it, keep it, or discard it.”

## 1:45–2:25 — Second revision

**Picture:** Without reloading, enter a second change: “Add a release condition to the existing Cargo connection: when Player speed exceeds 0.5, detach Cargo and leave it where it was.” Show the new OLD/NEW replay.

**Voiceover:** “CAST is not a one-shot generator. The next request patches the accepted mechanic. The existing slow pickup relation remains, while a separate detach relation controls release. The designer compares that revision against the same recorded play again.”

**On-screen:** `RULESET 17 → RULESET 18` · `PATCH` · `SAME INPUT`

## 2:25–2:55 — Why this is real

**Picture:** Brief Agent details panel and evidence cards, then replay again.

**Voiceover:** “Each candidate leaves an auditable tool call, a ruleset version, and an input recording identifier. The comparison is computed by the runtime from one initial snapshot and one input sequence. It is not a pair of pre-recorded animations.”

**On-screen:** `REAL STRANDS TOOL CALL` · `propose_rule_patch` · `RECORDED INPUT` · `OLD / NEW`

## 2:55–3:20 — Architecture

**Picture:** One diagram: `Designer plays → Input Recorder → Scene + Rules → Strands Agent → Constrained Rule Tools → Candidate Ruleset → Deterministic Replay → OLD | NEW → Keep / Revert / Revise`.

**Voiceover:** “Strands performs the interpretation and tool orchestration. The local runtime validates and versions the candidate, then deterministically replays it. This keeps the designer's judgment in the loop while removing the work of rebuilding and recreating a playtest.”

## 3:20–3:40 — Unseen mechanic

**Picture:** Enter an English request that was not used in the hero: “When Player is to the right of Cargo, make Cargo follow Player vertical movement. Keep the existing attachment mechanic unchanged.” Show the generated generic condition and a short OLD/NEW replay.

**Voiceover:** “The same primitives can express a new relation without adding a new semantic effect to the code.”

## 3:40–3:50 — End

**Picture:** Best OLD/NEW frame, then CAST wordmark.

**Voiceover:** “CAST shows you what your last play would have felt like under a different rule.”

**On-screen:** `Play once. Change the rule. Feel the difference.`

## Recording rules

- Start with the result. Do not open with a logo, team introduction, architecture, terminal, or credentials.
- Keep all visible product copy in English.
- Let the OLD/NEW canvases establish the behavior; never narrate a visual fact the viewer cannot see.
- Use the real browser recording, real Agent responses, and real replay results from `records/browser-replay/`.
- Keep the final cut under five minutes. The Hero segment must be the first 20–30 seconds.
