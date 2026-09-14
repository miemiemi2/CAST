import time
import math
from .schemas import Signal

class StageEngine:
    """Deterministic evaluator shared by API and browser runtime.

    ``event`` gates rules on visibility/occlusion and ``persist`` controls
    whether flags/effects survive frames where a rule is inactive.
    """
    def apply(self, s: Signal, rules, previous=None):
        old = previous or {}
        # Pointer recordings retain exogenous input. Recompute proximity in
        # each world so a candidate's moved cargo does not inherit OLD distance.
        if s.distance_object:
            reference = old.get('objects', old).get(s.distance_object)
            available = bool(reference and reference.get('visible', True))
            s = s.model_copy(update={
                'auxVisible': available,
                'distance': min(1.0, math.hypot(s.x-reference['x'], s.y-reference['y'])) if available else 1.0,
            })
        now_ms = s.time_ms if s.time_ms is not None else time.monotonic() * 1000
        active_since = dict(old.get('_active_since', {}))
        old_visible = old.get('visible', True)
        # Tracking loss freezes the complete prior scene for recovery.
        tracking_lost = not s.visible
        if tracking_lost and not any((raw.get('event') if isinstance(raw, dict) else raw.event) == 'occluded' for raw in rules):
            return old if old else {'visible': False, 'objects': {}}
        def actor(name, default):
            prior = old.get('objects', {}).get(name, old.get(name, {}))
            return {'x': prior.get('x', default[0]), 'y': prior.get('y', default[1]),
                    'rotation': prior.get('rotation', 0.0), 'scale': prior.get('scale', 1.0),
                    'flags': dict(prior.get('flags', {})), 'visible': prior.get('visible', True),
                    'mask': prior.get('mask', 1.0), 'light': prior.get('light', False),
                    '_attach_offset': prior.get('_attach_offset', prior.get('_attachOffset')), '_attach_key': prior.get('_attach_key', prior.get('_attachKey'))}
        out = actor('stage', (s.x, s.y))
        if not tracking_lost:
            out.update({'x': s.x, 'y': s.y, 'rotation': s.rotation, 'scale': 1.0})
        moon = actor('moon', (.8, .25)); actors = {'stage': out, 'moon': moon}
        # Preserve every registered/custom actor in the runtime snapshot.
        for name, prior_actor in old.get('objects', {}).items():
            if name not in actors:
                actors[name] = actor(name, (prior_actor.get('x', .5), prior_actor.get('y', .5)))
        for raw in rules:
            r = raw if isinstance(raw, dict) else raw.model_dump()
            target = r.get('target_object') or r.get('target', 'stage')
            a = actors.setdefault(target, actor(target, (.5, .5)))
            if r.get('effect') == 'mask': a['mask'] = 1.0
            if r.get('effect') == 'visibility': a['visible'] = True
        for raw in rules:
            rr = raw if isinstance(raw, dict) else raw.model_dump()
            if not rr.get('persist', True) and rr.get('effect') in ('state', 'light'):
                target = rr.get('target_object') or rr.get('target', 'stage')
                actors.setdefault(target, actor(target, (.5, .5)))['flags'].pop(rr.get('state_key', 'active'), None)
        for raw in rules:
            r = raw if isinstance(raw, dict) else raw.model_dump()
            value = getattr(s, r['signal'], None)
            if value is None or not isinstance(value, (int, float)): continue
            if r['signal'] == 'distance' and not getattr(s, 'auxVisible', True):
                continue
            rule_key = str(r.get('version', 1)) + ':' + str(r.get('target_object') or r.get('target', 'stage')) + ':' + r['signal'] + ':' + r['effect']
            predicates = [{'signal': r['signal'], 'when': r.get('when', 'always'), 'threshold': r.get('threshold', .5)}] + r.get('conditions', [])
            checks = [self._active(s, p, old) for p in predicates]
            if not (any(checks) if r.get('conditions_mode', 'all') == 'any' else all(checks)):
                active_since.pop(rule_key, None)
                continue
            duration = r.get('duration_ms', 0)
            if duration:
                started = active_since.setdefault(rule_key, now_ms)
                if now_ms - started < duration: continue
            else:
                active_since.pop(rule_key, None)
            event = r.get('event', 'frame')
            if event == 'visible' and not s.visible: continue
            if event == 'occluded' and s.visible: continue
            if event == 'changed' and not (value != old.get('last_signal', {}).get(r['signal'])): continue
            target = r.get('target_object') or r.get('target', 'stage')
            if target not in actors: actors[target] = actor(target, (.5, .5))
            a, amount = actors[target], r.get('amount', 1.0)
            if r['effect'] == 'position' and r['signal'] in ('x','y'): a[r['signal']] = max(0,min(1,value*amount))
            elif r['effect'] == 'rotation': a['rotation'] = max(-180,min(180,value*amount))
            elif r['effect'] == 'scale': a['scale'] = max(.2,min(3,1+value*amount))
            elif r['effect'] == 'mask': a['mask'] = max(0.0, min(1.0, amount))
            elif r['effect'] == 'visibility': a['visible'] = bool(amount)
            elif r['effect'] in ('state','light'):
                a['flags'][r.get('state_key','active')] = True
                if r['effect'] == 'light': a['light'] = True
            elif r['effect'] == 'attach':
                key = r.get('state_key','attached')
                if not a['flags'].get(key): a['_attach_offset'] = (a.get('x', .5) - out.get('x', .5), a.get('y', .5) - out.get('y', .5))
                a['flags'][key] = True
                a['_attach_key'] = key
            elif r['effect'] == 'detach':
                key = r.get('state_key','attached')
                a['flags'].pop(key, None); a.pop('_attach_offset', None); a.pop('_attach_key', None)
            if not r.get('persist', True) and r['effect'] in ('state','light'):
                # Explicitly transient effects are cleared on next frame by absence.
                a.setdefault('_transient', set()).add(r.get('state_key','active'))
        for name,a in actors.items():
            attach_key = a.get('_attach_key', 'attached')
            if name != 'stage' and a.get('flags',{}).get(attach_key):
                off=a.get('_attach_offset',(0,0)); a['x']=max(0,min(1,out['x']+off[0])); a['y']=max(0,min(1,out['y']+off[1]))
            a.pop('_transient', None)
        result = {'x': out['x'], 'y': out['y'], 'rotation': out['rotation'], 'scale': out['scale'],
                  'visible': not tracking_lost, 'objects': {k:v.copy() for k,v in actors.items()}, 'stage': out, 'moon': moon,
                  'flags': {**out['flags'], **moon['flags']}, 'last_signal': s.model_dump(), '_active_since': active_since}
        return result

    def _active(self, s, predicate, old):
        value = getattr(s, predicate.get('signal'))
        mode, threshold = predicate.get('when', 'always'), predicate.get('threshold', .5)
        previous = old.get('last_signal', {}).get(predicate.get('signal'))
        if mode == 'enter': return value >= threshold and (previous is None or previous < threshold)
        if mode == 'exit': return value < threshold and (previous is None or previous >= threshold)
        if mode == 'above': return value >= threshold
        if mode == 'below': return value < threshold
        return True
