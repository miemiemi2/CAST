import base64, json, subprocess
from pathlib import Path
import google.auth
from google.auth.transport.requests import AuthorizedSession

OUT=Path(__file__).resolve().parents[1]/'records/video'
text='''CAST lets designers test a mechanic change against the exact play that made them want the change.

In a normal playtest, a designer notices a bad interaction, leaves the prototype, edits the implementation, rebuilds, and then tries to recreate the moment. The expensive part is not only changing the rule. It is finding out what that same play would have felt like under the new rule.

The designer plays once with a real pointer. CAST records the initial world, the ordered input frames, timing, and the active mechanic version. The designer describes the change in human language while the prototype remains available.

The Strands Agent reads the current scene and rules, preserves unrelated behavior, and constructs a candidate from constrained control primitives. It does not select a named effect.

CAST restores the same initial state and feeds the same recorded input to both rulesets. Only the mechanic changes.

The candidate is a real running mechanic. The designer can try it, keep it, or discard it.

CAST is not a one-shot generator. The next request patches the accepted mechanic. The existing relation remains while a separate relation controls release. The designer compares that revision against the same recorded play again.

Each candidate leaves an auditable tool call, a ruleset version, and an input recording identifier. The comparison is computed by the runtime from one initial snapshot and one input sequence. It is not a pair of pre-recorded animations.

Strands performs the interpretation and tool orchestration. The local runtime validates and versions the candidate, then deterministically replays it. This keeps the designer's judgment in the loop while removing the work of rebuilding and recreating a playtest.

The same primitives can express a new relation without adding a new semantic effect to the code.

CAST shows you what your last play would have felt like under a different rule.'''
creds,project=google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
session=AuthorizedSession(creds)
req={'input':{'text':text},'voice':{'languageCode':'en-US','name':'en-US-Neural2-F','ssmlGender':'FEMALE'},'audioConfig':{'audioEncoding':'LINEAR16','sampleRateHertz':24000,'speakingRate':0.98,'pitch':0}}
r=session.post('https://texttospeech.googleapis.com/v1/text:synthesize',json=req,timeout=120)
print(r.status_code)
if not r.ok: raise SystemExit(r.text)
data=r.json();(OUT/'voiceover.wav').write_bytes(base64.b64decode(data['audioContent']))
(OUT/'voiceover.json').write_text(json.dumps({'provider':'Google Cloud Text-to-Speech','project':project,'voice':'en-US-Neural2-F','sample_rate':24000,'characters':len(text)},indent=2))
