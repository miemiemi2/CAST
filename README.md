# CAST · live object theatre

CAST turns a performer’s new interpretation into a new control system while the performance is still happening. Move physical objects and describe a relationship,
and change how those movements affect a theatre scene. Strands interprets the
request and calls a constrained rule tool; the local application controls
validation, installation, revisions and Undo.

The agent does not select from a catalog of visual presets. Each accepted
intent produces a new, recorded declarative rule set with validated targets,
conditions, amounts and effects; it is previewed locally before installation.
The same recorded play must produce a changed runtime result for the
intent to count as a successful creation.

**In development.** Real Vertex tool calls and the Mac-to-VPS proposal path have
been verified. Browser capture uses local ArUco identity tracking when available,
with colour fallback. Full product acceptance has not passed. See [current
state](IMPLEMENTATION-STATUS.md).

## Start

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[agent,test]'
uvicorn cast.app:app --host 127.0.0.1 --port 8765
```

Open http://127.0.0.1:8765. The primary playtest path is a deterministic mouse
interaction: drag Player, carry Cargo into Goal, and let CAST record the exact
pointer frames. Camera input remains available as an adapter, but is not needed
for the replay workflow.

During development or when no camera is available, click **Simulate performance**
to drive the same runtime with moving synthetic objects. This is useful for
checking a newly installed control without changing the physical setup.

For natural-language creation, configure [Vertex and Strands](docs/VERTEX.md).
The existing Mac installation uses an SSH tunnel to the VPS model service, so
credentials stay on the VPS. Model failure leaves the installed rules unchanged;
the manual JSON authoring interface remains available and labels human input.

## Current capabilities

- Real Strands/Gemini proposals based on the intent, current rules and scene.
- Multi-turn revision of installed rules; verified rotation multiplier changes
  from 1 to 0.5, and preservation of an unrelated position binding.
- Declarative position, rotation, scale, visibility and mask outputs with
  composable all/any conditions. Custom targets
  must be registered, and local ArUco marker IDs are configurable with colour
  fallback.
- Proposal explanations, API preview, version-checked install, rule Undo,
  scene update/replace/Undo and event export through `/api/events`.
- Camera selection and local colour/ArUco tracking. No image frames are sent to
  models. Pointer play recording, OLD/NEW deterministic replay, and portable
  export include the input identity and ruleset version.

Important gaps: complete field validation with physical markers, shared
runtime semantics across every temporal feature, and a full unattended-use
acceptance pass are still pending. Presence of a schema field or a passing
unit test is not evidence that all of these features work.

## Verify

```sh
pytest -q
node --test tests/tracking.test.mjs
python scripts/demo_probe.py
```

The probe runs human-authored rules on **synthetic signals in an isolated store**.
It does not call a model and must not be presented as camera or natural-language
evidence.

Actual model evidence:

- `records/vertex-proof-20260914T174411.json`: raw
  Strands messages and tool calls.
- `records/vertex-proof-behavior.json`: the resulting rules evaluated on positive
  and negative synthetic rotation, comparing Python and browser module output.
- `records/vertex-preserve-unrelated.json`: real model revision preserving a
  second, unrelated binding.
- `records/vertex-api-probe-20260915T014746.json`: Mac API → SSH → Strands → Vertex
  proposal, with the installed stage unchanged.

The model ledger lives outside the source tree. Do not copy VPS `records/` over
an active Mac installation; it contains performance state and audit history.

See the [architecture](docs/ARCHITECTURE.md) for the complete input → Agent →
candidate → deterministic replay data flow.

Optional native CV adapter: `pip install -e '.[cv]'`. This installs a dependency,
not an automatic browser integration. OpenCV is third-party infrastructure;
CAST's contribution is the creative workflow and governed relationship changes.
