import time
import os
import copy
import base64
import httpx
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .schemas import Signal,Intent,InstallRequest,SceneUpdate,ObjectReplace,ObjectRemove
from .store import StageStore
from .agent import RuleAgent,AgentError
from .engine import StageEngine
from .tracker import backend_name, detect
ROOT = Path(__file__).resolve().parent.parent
app=FastAPI(title='CAST Stage',version='0.2.0'); store=StageStore(str(ROOT / 'records' / 'stage.json')); agent=RuleAgent(store); engine=StageEngine()
app.mount('/static',StaticFiles(directory=str(ROOT / 'static')),name='static')
@app.get('/',response_class=HTMLResponse)
def index(): return (ROOT / 'static' / 'index.html').read_text()
@app.get('/api/state')
def state(): return {'version':store.data['version'],'rules':store.data['rules'],'state':store.data['state'],'scene':store.data['state'].get('scene', {}),'events':store.data['events'][-50:]}

@app.get('/api/export')
def export_stage():
 """Return a portable, self-contained CAST performance package.

 The export is derived from the durable store so a user can take the authored
 scene, rules, current runtime snapshot, and audit trail to another machine.
 """
 with store.lock:
  package = {'format':'cast-performance-v1', 'version':store.data['version'],
             'rules':copy.deepcopy(store.data['rules']),
             'scene':copy.deepcopy(store.data['state'].get('scene', {})),
             'runtime':copy.deepcopy(store.data['state'].get('runtime', {})),
             'recordings':copy.deepcopy(store.data.get('recordings', [])),
             'events':copy.deepcopy(store.data['events'])}
 return JSONResponse(package, headers={'Content-Disposition':'attachment; filename=cast-performance.json'})
@app.post('/api/signal')
def signal(s:Signal):
 # Keep the complete evaluator snapshot between frames. Passing only the
 # stage actor drops moon/custom-object flags and makes continuous relations
 # appear to reset on every camera tick.
 previous = store.data['state'].get('runtime')
 out=engine.apply(s,store.data['rules'], previous)
 store.data['state']['runtime']=out
 store.data['state']['objects']['stage']=out
 store.data['state']['last_signal']=s.model_dump()
 store.event('signal.applied',{'signal':s.model_dump(),'result':out})
 return out

@app.post('/api/native-track')
def native_track(payload: dict):
 """Decode one camera frame locally and return the normalized CAST signal.

 Frames are accepted only by the localhost app; they are never sent to the
 agent gateway. Marker IDs 0/1 define the main prop pose and 2 is auxiliary.
 """
 try:
  raw = payload.get('jpeg') or payload.get('image')
  if not isinstance(raw, str): raise ValueError('jpeg payload is required')
  if raw.startswith('data:'): raw = raw.split(',', 1)[1]
  if len(raw) > 2_000_000: raise ValueError('frame exceeds 2 MB limit')
  import cv2
  import numpy as np
  frame = cv2.imdecode(np.frombuffer(base64.b64decode(raw, validate=True), dtype=np.uint8), cv2.IMREAD_COLOR)
  if frame is None: raise ValueError('invalid jpeg frame')
  height, width = frame.shape[:2]
  markers = {m.id:m for m in detect(frame, width, height)}
  mapping = payload.get('mapping') or {'main_a': 0, 'main_b': 1, 'aux': 2}
  if not isinstance(mapping, dict) or any(k not in mapping for k in ('main_a', 'main_b', 'aux')):
   raise ValueError('mapping must contain main_a, main_b and aux marker IDs')
  try:
   ids = {k:int(mapping[k]) for k in ('main_a', 'main_b', 'aux')}
  except (TypeError, ValueError):
   raise ValueError('marker IDs must be integers')
  a,b = markers.get(ids['main_a']), markers.get(ids['main_b'])
  aux = markers.get(ids['aux'])
  if not a or not b:
   return {'visible':False, 'auxVisible':bool(aux), 'backend':'opencv-aruco'}
  import math
  x,y=(a.x+b.x)/2,(a.y+b.y)/2
  distance=min(1.0, math.hypot(x-(aux.x if aux else x), y-(aux.y if aux else y))/math.sqrt(2)) if aux else 0.0
  return {'x':x,'y':y,'rotation':math.degrees(math.atan2(b.y-a.y,b.x-a.x)),
          'distance':distance,'visible':True,'auxVisible':bool(aux),'backend':'opencv-aruco'}
 except (ValueError, TypeError, ImportError, Exception) as error:
  raise HTTPException(422, str(error))

@app.post('/api/replay')
def replay(payload: dict):
 """Run a recorded pointer play from one snapshot under one ruleset."""
 try:
  initial = payload['initial']
  frames = payload['frames']
  # Agents may refer to a scene object's human label (for example Cargo)
  # while browser recordings retain its stable runtime id (for example B).
  # Resolve labels before validation/evaluation so replay cannot create a
  # phantom actor merely because the two representations differ.
  scene = store.data['state'].get('scene', {})
  aliases = {}
  # Prefer the captured snapshot identity when it carries labels; this keeps
  # portable recordings valid even after the live scene registry changes.
  snapshot_objects = initial.get('objects', initial) if isinstance(initial, dict) else {}
  for object_id in set(scene) | set(snapshot_objects if isinstance(snapshot_objects, dict) else {}):
   obj = {**(scene.get(object_id, {}) if isinstance(scene.get(object_id, {}), dict) else {}), **(snapshot_objects.get(object_id, {}) if isinstance(snapshot_objects, dict) and isinstance(snapshot_objects.get(object_id, {}), dict) else {})}
   if isinstance(obj, dict):
    for key in ('label', 'name'):
     value = obj.get(key)
     if isinstance(value, str) and value: aliases[value] = object_id
  raw_rules = copy.deepcopy(payload['rules'])
  for raw in raw_rules:
   if isinstance(raw, dict):
    for key in ('target_object', 'target'):
     target = raw.get(key)
     if isinstance(target, str) and target in aliases: raw[key] = aliases[target]
  rules = [r.model_dump() for r in InstallRequest(rules=raw_rules, expected_version=store.data['version']).rules]
  # Replay must use the same registered object namespace as the captured
  # world.  Silently creating an unknown target would make an OLD/NEW
  # comparison look valid while applying the rule to a phantom actor.
  initial_objects = set(initial.get('objects', initial).keys()) if isinstance(initial, dict) else set()
  registered = initial_objects | set(store.data['state'].get('scene', {}).keys()) | {'stage', 'moon'}
  unknown = sorted({r.get('target_object') or r.get('target') for r in rules
                    if (r.get('target_object') or r.get('target')) not in registered})
  if unknown:
   raise ValueError('target objects are not registered in replay snapshot: ' + ', '.join(unknown))
  if not isinstance(frames, list) or not frames or len(frames) > 2000: raise ValueError('frames required')
  # Browser recordings store the scene map directly; the engine consumes a
  # runtime snapshot with an ``objects`` map. Preserve custom actors in replay.
  runtime = copy.deepcopy(initial)
  if isinstance(runtime, dict) and 'objects' not in runtime:
   runtime = {'objects': runtime}
  results=[]
  for frame in frames:
   signal_data = dict(frame.get('signal', frame))
   # A recorded play has one relative clock, independent of wall-clock time.
   signal_data['time_ms'] = frame.get('t', signal_data.get('time_ms', 0))
   signal = Signal.model_validate(signal_data)
   runtime = engine.apply(signal, rules, runtime)
   results.append({'t':frame.get('t',0), 'state':copy.deepcopy(runtime)})
  return {'frames':results, 'final':runtime}
 except (KeyError, TypeError, ValueError) as e:
  raise HTTPException(422, str(e))

@app.post('/api/recording')
def save_recording(payload: dict):
 """Persist one browser play for later replay/export."""
 try:
  recording = {
   'id': payload['id'], 'initial': copy.deepcopy(payload['initial']),
   'frames': copy.deepcopy(payload['frames']), 'rules': copy.deepcopy(payload['rules']),
   'version': int(payload['version'])
  }
  if not isinstance(recording['id'], str) or not recording['id'] or len(recording['id']) > 100:
   raise ValueError('recording id is invalid')
  if not isinstance(recording['frames'], list) or not 1 <= len(recording['frames']) <= 2000:
   raise ValueError('recording frames must contain 1–2000 items')
  if any(not isinstance(frame, dict) or not isinstance(frame.get('t'), (int, float)) or frame['t'] < 0 for frame in recording['frames']):
   raise ValueError('recording timestamps must be non-negative numbers')
  if not isinstance(recording['initial'], dict) or not isinstance(recording['rules'], list):
   raise ValueError('recording snapshot and rules are required')
  with store.lock:
   existing = [r for r in store.data.setdefault('recordings', []) if r.get('id') != recording['id']]
   existing.append(recording)
   store.data['recordings'] = existing[-50:]
   store.event('play.recorded', {'id': recording['id'], 'frames': len(recording['frames']), 'version': recording['version']})
  return {'status': 'recorded', 'id': recording['id'], 'frames': len(recording['frames'])}
 except (KeyError, TypeError, ValueError) as error:
  raise HTTPException(422, str(error))

@app.post('/api/preview')
def preview(payload: dict):
 """Evaluate candidate rules without changing the installed stage."""
 try:
  candidate = [InstallRequest(rules=payload['rules'], expected_version=store.data['version']).rules][0]
  signal_data = payload.get('signal') or store.data['state'].get('last_signal')
  if not signal_data:
   raise ValueError('signal is required for preview')
  # Preview against the current runtime so edge conditions (enter/exit/changed)
  # show the same transition the performer will get on installation.
  result = engine.apply(Signal.model_validate(signal_data), [r.model_dump() for r in candidate],
                        store.data['state'].get('runtime'))
  store.event('rule.previewed', {'base_version': store.data['version'], 'rules':[r.model_dump() for r in candidate], 'result':result})
  return {'version':store.data['version'],'result':result}
 except (KeyError, ValueError) as e:
  raise HTTPException(422, str(e))

@app.post('/api/explain')
def explain(payload: dict):
 """Return a plain-language explanation of validated declarative rules."""
 try:
  rules = InstallRequest(rules=payload['rules'], expected_version=store.data['version']).rules
 except (KeyError, ValueError) as e:
  raise HTTPException(422, str(e))
 lines=[]
 for rule in rules:
  target=rule.target_object or rule.target
  condition = {'always':'Whenever','above':f'When {rule.signal} is at least {rule.threshold:g}',
               'below':f'When {rule.signal} is below {rule.threshold:g}',
               'enter':f'When {rule.signal} enters above {rule.threshold:g}',
               'exit':f'When {rule.signal} exits below {rule.threshold:g}'}[rule.when]
  effect=f'{rule.effect} of {target}'
  extras = []
  for predicate in rule.conditions:
   extras.append(f'{predicate.signal} {predicate.when} {predicate.threshold:g}')
  logic = ('; also ' + (' or ' if rule.conditions_mode == 'any' else ' and ').join(extras)) if extras else ''
  lines.append(f'{condition}{logic}, apply {effect} using amount {rule.amount:g}.')
 return {'rules':[r.model_dump() for r in rules], 'explanation':lines}

@app.post('/api/rules/diff')
def rules_diff(payload: dict):
 """Describe the concrete control-system change before installation."""
 try:
  candidate = [r.model_dump() for r in InstallRequest(rules=payload['rules'], expected_version=store.data['version']).rules]
 except (KeyError, ValueError) as e:
  raise HTTPException(422, str(e))
 current = store.data['rules']
 key = lambda r: (r.get('kind'), r.get('source'), r.get('signal'), r.get('target'), r.get('target_object'), r.get('effect'), r.get('state_key'))
 old, new = {key(r):r for r in current}, {key(r):r for r in candidate}
 return {'added':[new[k] for k in new.keys()-old.keys()],
         'removed':[old[k] for k in old.keys()-new.keys()],
         'changed':[{'before':old[k], 'after':new[k]} for k in old.keys() & new.keys() if old[k] != new[k]]}
@app.post('/api/intent')
def intent(i:Intent):
 try:
  gateway = os.getenv('CAST_AGENT_URL')
  if gateway:
   with store.lock:
    context = {'text': i.text, 'base_version': store.data['version'],
               'current_rules': copy.deepcopy(store.data['rules']),
               'scene': copy.deepcopy(store.data['state'].get('scene', {})),
               'recent_intents': [e['payload'].get('intent') for e in store.data['events']
                                  if e.get('type') == 'agent.remote.started' and e.get('payload', {}).get('intent')][-6:]}
   store.event('agent.remote.started', {'intent': i.text, 'base_version': context['base_version']})
   try:
    response = httpx.post(gateway.rstrip('/') + '/propose', json=context, timeout=120)
    if response.is_error:
     # Preserve the gateway's actionable model/quota error instead of hiding
     # it behind a generic HTTP status.
     try: detail = response.json().get('detail', response.text)
     except ValueError: detail = response.text
     raise AgentError(f'gateway {response.status_code}: {detail}')
    result = response.json()
    checked = InstallRequest(rules=result['rules'], expected_version=context['base_version'])
    if result.get('base_version') != context['base_version']:
     raise ValueError('Agent returned a proposal for the wrong revision')
    result['rules'] = [r.model_dump() for r in checked.rules]
    store.event('agent.remote.completed', result)
    return result
   except (httpx.HTTPError, ValueError, KeyError) as error:
    store.event('agent.remote.error', {'error': str(error)})
    raise AgentError('Model service failed; stage unchanged: ' + str(error)) from error
  request_agent = RuleAgent(store)
  rules = request_agent.generate(i.text)
  return {'rules':[r.model_dump() for r in rules], 'calls':request_agent.calls, **(request_agent.last_proposal or {})}
 except AgentError as e:
  status = 429 if 'limit' in str(e).lower() or 'quota' in str(e).lower() else 503
  raise HTTPException(status, str(e))
@app.post('/api/install')
def install(req:InstallRequest):
 try:return store.install(req.rules,req.expected_version,req.origin)
 except ValueError as e: raise HTTPException(409,str(e))

@app.post('/api/rules/patch')
def patch_rules(payload: dict):
 """Atomically apply validated add/replace/remove operations to rules."""
 try:
  expected = int(payload['expected_version']); operations = payload['operations']
  if not isinstance(operations, list) or not operations or len(operations) > 8:
   raise ValueError('one to eight patch operations required')
  with store.lock:
   if expected != store.data['version']:
    raise ValueError(f'version conflict: expected {expected}, current {store.data["version"]}')
   rules = copy.deepcopy(store.data['rules'])
   for operation in operations:
    op = operation.get('op'); index = operation.get('index')
    if op == 'add': rules.append(InstallRequest(rules=[operation['rule']], expected_version=expected).rules[0].model_dump())
    elif op == 'replace' and isinstance(index, int) and 0 <= index < len(rules):
     rules[index] = InstallRequest(rules=[operation['rule']], expected_version=expected).rules[0].model_dump()
    elif op == 'remove' and isinstance(index, int) and 0 <= index < len(rules): rules.pop(index)
    else: raise ValueError('invalid rule patch operation')
   if not 1 <= len(rules) <= 8: raise ValueError('result must contain one to eight rules')
   return store.install(rules, expected, payload.get('origin', 'agent'))
 except (KeyError, TypeError, ValueError) as e:
  raise HTTPException(409, str(e))

@app.post('/api/scene')
def update_scene(req: SceneUpdate):
 try:
  return store.update_scene(req.objects, req.expected_version)
 except ValueError as e:
  raise HTTPException(409, str(e))

@app.post('/api/scene/replace')
def replace_object(req: ObjectReplace):
 try:
  return store.replace_object(req.object, req.expected_version)
 except ValueError as e:
  raise HTTPException(409, str(e))

@app.post('/api/scene/remove')
def remove_object(req: ObjectRemove):
 try:
  return store.remove_object(req.id, req.expected_version)
 except ValueError as e:
  raise HTTPException(409, str(e))

@app.post('/api/scene/rollback')
def rollback_scene():
 return store.rollback_scene()
@app.post('/api/rollback')
def rollback(): return store.rollback()
@app.get('/api/health')
def health(): return {'ok':True,'version':store.data['version'],'agent_calls':agent.calls,'max_agent_calls':agent.max_calls,'provider':('remote-strands' if os.getenv('CAST_AGENT_URL') else agent.provider),'native_tracker':backend_name(),'browser_tracker':'colour-fallback'}

@app.get('/api/events')
def events(since: int = 0, type: str | None = None, limit: int = 100):
 """Read bounded raw execution records for reproducible evaluation."""
 limit = max(1, min(limit, 500))
 start = max(0, since)
 with store.lock:
  page = copy.deepcopy(store.data['events'][start:start + limit])
  total = len(store.data['events'])
 records = [event for event in page if not type or event['type'] == type]
 return {'since': start, 'next': start + len(page), 'total': total, 'events': records}

def main():
 import uvicorn; uvicorn.run('cast.app:app',host='127.0.0.1',port=8765,reload=False)
