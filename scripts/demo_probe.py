"""Offline end-to-end CAST capability probe.

Exercises the same preview, explanation, install, signal, and rollback calls
used by the browser, without pretending to be camera evidence.
"""
import json
from fastapi.testclient import TestClient
import cast.app as app_module
from cast.store import StageStore
import tempfile

def main():
    temporary = tempfile.TemporaryDirectory(prefix="cast-probe-")
    store = StageStore(temporary.name + "/state.json")
    previous_store = app_module.store
    app_module.store = store
    client = TestClient(app_module.app)
    scene = client.post('/api/scene', json={'objects':[{'id':'hero','label':'Hero','kind':'character'}], 'expected_version':0}).json()
    rule = {'kind':'relation','source':'prop','signal':'distance','target':'moon','effect':'mask','when':'below','threshold':.3,
            'conditions':[{'signal':'rotation','when':'above','threshold':30}],
            'amount':.25}
    base = store.data['version']
    preview = client.post('/api/preview', json={'rules':[rule], 'signal':{'x':.3,'y':.3,'rotation':0,'distance':.2,'rotation':60,'visible':True}}).json()
    explanation = client.post('/api/explain', json={'rules':[rule]}).json()
    installed = client.post('/api/install', json={'rules':[rule], 'expected_version':base, 'origin':'human'}).json()
    changed = dict(rule, amount=.5)
    diff = client.post('/api/rules/diff', json={'rules':[changed]}).json()
    patched = client.post('/api/rules/patch', json={'operations':[{'op':'replace','index':0,'rule':changed}], 'expected_version':installed['version'], 'origin':'human'}).json()
    signal = client.post('/api/signal', json={'x':.3,'y':.3,'rotation':0,'distance':.2,'rotation':60,'visible':True}).json()
    rolled = client.post('/api/rollback').json()
    exported = client.get('/api/export').json()
    app_module.store = previous_store
    temporary.cleanup()
    print(json.dumps({'input_source':'synthetic signal, human rules, isolated temporary store','scene':scene,'preview':preview,'explanation':explanation,'installed':installed,
                      'diff':diff,'patched':patched,'signal':signal,'rolled_back':rolled,
                      'export_format':exported['format'],'export_version':exported['version']}, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
