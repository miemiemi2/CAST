"""Public pointer demo: isolated browser sessions over the existing CAST app."""
import asyncio
from collections import deque
from contextvars import ContextVar
from pathlib import Path
import os
import re
import secrets
import time
from urllib.parse import urlsplit
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from . import app as core
from .agent import RuleAgent
from .schemas import Rule, SceneObject
from .store import StageStore

DATA = Path(os.environ.get('CAST_PUBLIC_DATA', '/var/lib/cast-live/sessions'))
DATA.mkdir(parents=True, exist_ok=True)
selected = ContextVar('cast_public_store')
class SessionStore:
    def __getattr__(self, name):
        return getattr(selected.get(), name)
core.store = SessionStore()
core.agent = RuleAgent(core.store)
sessions = {}
ip_calls = {}
model_slot = asyncio.Lock()


def new_store(sid):
    store = StageStore(DATA / (sid + '.json'))
    store.update_scene([
        SceneObject(id='stage', label='Player', x=.18, y=.55),
        SceneObject(id='B', label='Cargo', kind='character', x=.48, y=.55),
        SceneObject(id='moon', label='Moon', kind='anchor', x=.8, y=.25),
    ], 0)
    # Authored graybox baseline. All requested changes still use real Strands.
    store.install([Rule(kind='relation', source='prop', signal='distance',
                        target='B', effect='attach', when='below', threshold=.1,
                        state_key='attached')], 1, origin='system')
    return store

app = FastAPI(title='CAST Live Playtest', docs_url=None, redoc_url=None, openapi_url=None)
ALLOWED = {'/api/state', '/api/health', '/api/intent', '/api/install', '/api/rollback',
           '/api/replay', '/api/recording', '/api/export', '/api/events'}

@app.middleware('http')
async def isolate(request: Request, call_next):
    path = request.url.path.removeprefix('/cast') or '/'
    if path not in ALLOWED and path != '/' and not path.startswith('/static/'):
        return JSONResponse({'detail': 'This route is not available in the public playtest.'}, status_code=404)
    if request.method not in {'GET', 'HEAD', 'POST'}:
        return JSONResponse({'detail': 'Method not allowed'}, status_code=405)
    if request.method == 'POST':
        origin = request.headers.get('origin')
        if origin and urlsplit(origin).netloc != request.headers.get('host'):
            return JSONResponse({'detail': 'Use the CAST page to make changes.'}, status_code=403)
        body = await request.body()
        if len(body) > 1_048_576:
            return JSONResponse({'detail': 'This play is too long. Record a shorter interaction.'}, status_code=413)
    now = time.monotonic()
    sid = request.cookies.get('cast_session')
    fresh = sid not in sessions
    if fresh:
        if path == '/api/health':
            return JSONResponse({'ok': True, 'product': 'CAST Live Playtest', 'input': 'pointer'})
        if len(sessions) >= 200:
            for key, value in list(sessions.items()):
                if now - value['seen'] > 7200:
                    sessions.pop(key)
            if len(sessions) >= 200:
                return JSONResponse({'detail': 'The live demo is busy. Please try again later.'}, status_code=503)
        persisted = DATA / (sid + '.json') if isinstance(sid, str) and re.fullmatch(r'[A-Za-z0-9_-]{43}', sid) else None
        if persisted is not None and persisted.is_file():
            saved = StageStore(persisted)
        else:
            sid = secrets.token_urlsafe(32)
            saved = new_store(sid)
        used = sum(e.get('type') == 'agent.remote.started' for e in saved.data['events'])
        sessions[sid] = {'store': saved, 'seen': now, 'intents': used, 'calls': deque()}
    session = sessions[sid]
    session['seen'] = now
    recent = session['calls']
    while recent and recent[0] < now - 60:
        recent.popleft()
    if len(recent) >= 90:
        return JSONResponse({'detail': 'Please pause briefly before trying again.'}, status_code=429)
    recent.append(now)
    token = selected.set(session['store'])
    acquired = False
    try:
        if path == '/api/intent' and request.method == 'POST':
            ip = request.client.host if request.client else 'unknown'
            # Trust only the private reverse proxy's overwritten client header.
            if ip in {'172.18.0.1', '127.0.0.1'} or ip.startswith('172.18.'):
                ip = request.headers.get('x-real-ip', ip)
            calls = ip_calls.setdefault(ip, deque())
            while calls and calls[0] < now - 3600:
                calls.popleft()
            if session['intents'] >= 8 or len(calls) >= 20:
                return JSONResponse({'detail': 'Live demo generation limit reached. You can keep playing, replaying and exporting.'}, status_code=429)
            if model_slot.locked():
                return JSONResponse({'detail': 'The Agent is helping another designer. Try again in a few seconds.'}, status_code=429)
            await model_slot.acquire()
            acquired = True
            session['intents'] += 1
            calls.append(now)
        if path == '/':
            html = (core.ROOT / 'static/index.html').read_text()
            html = html.replace('</header>', '</header><style>aside details,.manual,.objects{display:none!important}</style>')
            html = html.replace('Change what the movement means', 'Compare a mechanic change')
            html = html.replace('Play once, then describe how the mechanic should change.', 'Drag Player past Cargo. Release the pointer, then ask for a change and compare the same play.')
            response = HTMLResponse(html)
        else:
            response = await call_next(request)
        if response.status_code >= 500:
            response = JSONResponse({'detail': 'The Agent could not finish this change. Your installed mechanic is unchanged. Please try again.'}, status_code=response.status_code)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'none'"
        if fresh:
            response.set_cookie('cast_session', sid, httponly=True, secure=True,
                                samesite='lax', max_age=86400, path='/cast')
        return response
    finally:
        selected.reset(token)
        if acquired:
            model_slot.release()

app.mount('/cast', core.app)
