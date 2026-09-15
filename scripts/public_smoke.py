"""Isolated public-session smoke test; no model calls or production stores."""
import os
import tempfile
os.environ['CAST_PUBLIC_DATA'] = tempfile.mkdtemp(prefix='cast-public-test-')
from fastapi.testclient import TestClient
from cast.public import app, sessions
with TestClient(app, base_url='https://example.test') as a, TestClient(app, base_url='https://example.test') as b:
    assert a.get('/cast/').status_code == b.get('/cast/').status_code == 200
    sa, sb = a.get('/cast/api/state').json(), b.get('/cast/api/state').json()
    assert sa['version'] == sb['version'] == 2
    candidate = sa['rules']
    candidate[0]['conditions'] = [{'signal':'speed','when':'below','threshold':.2}]
    installed = a.post('/cast/api/install', json={'rules':candidate,'expected_version':2,'origin':'human'})
    assert installed.status_code == 200, installed.text
    sessions.clear()  # A server restart must not expose or erase another visitor's play.
    assert a.get('/cast/api/state').json()['version'] == 3
    assert b.get('/cast/api/state').json() == sb
    assert a.get('/cast/api/export').json()['rules'] != b.get('/cast/api/export').json()['rules']
    assert a.post('/cast/api/rollback', json={}, headers={'Origin':'https://wrong.example'}).status_code == 403
    assert a.post('/cast/api/native-track', json={}).status_code == 404
    assert a.get('/cast/docs').status_code == 404
    for cookie in a.cookies.jar:
        assert cookie.secure and cookie.path == '/cast'
    assert 'static/stage.mjs' in a.get('/cast/').text
    print('PASS: session isolation, export isolation, secure cookies, origin validation, route restrictions')
