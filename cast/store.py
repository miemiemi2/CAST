"""Single-process durable stage journal. Revision numbers never go backwards."""
import copy
import json
import os
import threading
import time
import uuid
from pathlib import Path
from .schemas import Rule

class StageStore:
    def __init__(self, path='records/stage.json'):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.data = {'version': 0, 'rules': [], 'state': {'objects': {}, 'flags': {}},
                     'events': [], 'undo': [], 'scene_undo': [], 'recordings': []}
        if self.path.exists():
            # Corruption must be visible, never silently erase a performance.
            self.data = json.loads(self.path.read_text())
            self.data.setdefault('undo', [])
            self.data.setdefault('scene_undo', [])
            self.data.setdefault('recordings', [])

    def save(self):
        with self.lock:
            temporary = self.path.with_suffix('.tmp')
            with temporary.open('w') as handle:
                json.dump(self.data, handle, ensure_ascii=False, indent=2, allow_nan=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)

    def event(self, kind, payload):
        with self.lock:
            event = {'id': str(uuid.uuid4()), 'type': kind, 'timestamp': time.time(), 'payload': payload}
            # Agent / installation receipts must survive frame traffic.
            self.data['events'].append(event)
            self.save()
            return event

    def install(self, rules, expected, origin='human'):
        with self.lock:
            if origin not in ('human', 'agent', 'system'):
                raise ValueError('invalid installation origin')
            if expected != self.data['version']:
                raise ValueError(f'version conflict: expected {expected}, current {self.data["version"]}')
            canonical = [Rule.model_validate(r.model_dump() if isinstance(r, Rule) else r).model_dump() for r in rules]
            if not 1 <= len(canonical) <= 8:
                raise ValueError('one to eight rules required')
            registered = set(self.data['state'].get('scene', {}))
            unknown = sorted({r['target_object'] for r in canonical
                              if r.get('target_object') and r['target_object'] not in registered})
            if unknown:
                raise ValueError('target objects are not registered: ' + ', '.join(unknown))
            if canonical == self.data['rules']:
                return {'status': 'idempotent', 'version': self.data['version'], 'rules': canonical}
            self.data['undo'].append(copy.deepcopy(self.data['rules']))
            self.data['version'] += 1
            self.data['rules'] = canonical
            receipt = {'status': 'installed', 'version': self.data['version'], 'rules': canonical, 'origin': origin}
            self.event('rule.installed', receipt)
            return receipt

    def rollback(self):
        with self.lock:
            if not self.data['undo']:
                return {'status': 'empty', 'version': self.data['version']}
            self.data['rules'] = self.data['undo'].pop()
            self.data['version'] += 1
            receipt = {'status': 'rolled_back', 'version': self.data['version'], 'rules': self.data['rules']}
            self.event('rule.rolled_back', receipt)
            return receipt

    def update_scene(self, objects, expected):
        with self.lock:
            if expected != self.data['version']:
                raise ValueError(f'version conflict: expected {expected}, current {self.data["version"]}')
            scene = {obj.id: obj.model_dump() for obj in objects}
            self.data.setdefault('scene_undo', []).append(copy.deepcopy(self.data['state'].get('scene', {})))
            self.data['state']['scene'] = scene
            runtime = self.data['state'].setdefault('runtime', {})
            runtime.setdefault('objects', {})
            for object_id, obj in scene.items():
                runtime['objects'].setdefault(object_id, {'x': obj['x'], 'y': obj['y'],
                    'rotation': obj['rotation'], 'scale': 1.0, 'flags': {}, 'visible': obj['visible']})
            self.data['version'] += 1
            receipt = {'status': 'scene_updated', 'version': self.data['version'], 'objects': scene}
            self.event('scene.updated', receipt)
            return receipt

    def replace_object(self, obj, expected):
        with self.lock:
            if expected != self.data['version']:
                raise ValueError(f'version conflict: expected {expected}, current {self.data["version"]}')
            scene = self.data['state'].setdefault('scene', {})
            self.data.setdefault('scene_undo', []).append(copy.deepcopy(scene))
            previous = scene.get(obj.id)
            scene[obj.id] = obj.model_dump()
            # Keep the live evaluator in the same object namespace as the
            # scene registry.  Preserve mechanic state while adopting the
            # replacement's physical pose and visibility.
            runtime = self.data['state'].setdefault('runtime', {})
            objects = runtime.setdefault('objects', {})
            prior_runtime = objects.get(obj.id, {})
            objects[obj.id] = {**prior_runtime, 'x': obj.x, 'y': obj.y,
                                'rotation': obj.rotation, 'visible': obj.visible,
                                'scale': prior_runtime.get('scale', 1.0),
                                'flags': dict(prior_runtime.get('flags', {}))}
            self.data['version'] += 1
            receipt = {'status':'object_replaced','version':self.data['version'],
                       'object':scene[obj.id], 'previous':previous}
            self.event('scene.object_replaced', receipt)
            return receipt

    def remove_object(self, object_id, expected):
        with self.lock:
            if expected != self.data['version']:
                raise ValueError(f'version conflict: expected {expected}, current {self.data["version"]}')
            scene = self.data['state'].setdefault('scene', {})
            if object_id not in scene:
                raise ValueError('scene object not found: ' + object_id)
            self.data.setdefault('scene_undo', []).append(copy.deepcopy(scene))
            previous = scene.pop(object_id)
            runtime = self.data['state'].setdefault('runtime', {})
            runtime.setdefault('objects', {}).pop(object_id, None)
            self.data['version'] += 1
            receipt = {'status':'object_removed','version':self.data['version'],
                       'id':object_id, 'previous':previous}
            self.event('scene.object_removed', receipt)
            return receipt

    def rollback_scene(self):
        with self.lock:
            if not self.data.get('scene_undo'):
                return {'status':'empty','version':self.data['version'], 'objects':self.data['state'].get('scene', {})}
            self.data['state']['scene'] = self.data['scene_undo'].pop()
            self.data['version'] += 1
            receipt={'status':'scene_rolled_back','version':self.data['version'], 'objects':self.data['state']['scene']}
            self.event('scene.rolled_back', receipt)
            return receipt
