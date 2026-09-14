# CAST architecture

CAST keeps physical input, interpretation, validation, and execution in one
auditable loop. Camera frames stay local; pointer play is the deterministic
default for replay.

Rendered exports: [SVG](architecture.svg) · [PNG](architecture.png)

```mermaid
flowchart TD
  U[Designer] --> I[Pointer or local camera adapter]
  I --> R[Input recorder\ninitial snapshot + timestamped signals]
  R --> S[Scene and installed rules]
  S --> A[Strands Agent\nVertex/Gemini or optional Bedrock]
  A --> T[Constrained rule tools\npropose / patch / validate]
  T --> C[Candidate ruleset]
  C --> V[Preview and versioned install]
  R --> P[Deterministic replay]
  S --> P
  V --> P
  P --> D[OLD | NEW comparison]
  D --> K[Try, keep, revert, or revise]
  K --> S
  S --> E[(Durable event journal\nversions, tool calls, exports)]
```

The local `StageStore` provides compare-and-swap versioning, atomic rule
installation, scene registration, undo stacks, and bounded event reads. The
Python engine and browser runtime evaluate the same declarative rule model,
including composed predicates and stateful attach/detach relations. A replay
restores one initial world and feeds the identical recorded signal sequence to
each ruleset; only the ruleset is allowed to differ.

The model never installs directly. Strands tools return validated candidate
rules, and the local service checks the base version and registered targets
before installation. An unavailable model is reported as an error; human
authored rules remain explicitly marked as such.
