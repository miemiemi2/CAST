import pytest
from cast.schemas import Rule,Signal,SceneObject
from cast.store import StageStore
from cast.engine import StageEngine
from cast.agent import RuleAgent

def make(tmp_path): return StageStore(str(tmp_path/'s.json'))
def test_schema_rejects_unsafe_signal():
 with pytest.raises(Exception): Signal(x=2,y=.2)
def test_install_version_idempotence_and_conflict(tmp_path):
 s=make(tmp_path); r=Rule(kind='binding',source='prop',signal='rotation',target='stage',effect='state')
 assert s.install([r],0)['version']==1
 assert s.install([r],1)['status']=='idempotent'
 with pytest.raises(ValueError): s.install([r],0)
def test_state_survives_rule_update(tmp_path):
 s=make(tmp_path); r=Rule(kind='relation',source='prop',signal='rotation',target='moon',effect='light',threshold=.5,state_key='lit'); s.install([r],0)
 out=StageEngine().apply(Signal(x=.2,y=.3,rotation=90),s.data['rules']); assert out['flags']['lit']
 assert s.data['state']=={'objects':{},'flags':{}}
def test_disabled_agent_cannot_fake_generation(tmp_path,monkeypatch):
 monkeypatch.delenv('CAST_USE_BEDROCK',raising=False)
 a=RuleAgent(make(tmp_path))
 with pytest.raises(Exception,match='disabled'): a.generate('when prop turns moon lights')
 assert a.calls==0

def test_budget_survives_restart(tmp_path,monkeypatch):
 monkeypatch.setenv('CAST_MAX_AGENT_CALLS','1')
 a=RuleAgent(make(tmp_path)); a.reserve(100)
 b=RuleAgent(make(tmp_path))
 assert b.calls==1
 with pytest.raises(Exception,match='limit'): b.reserve(100)


def test_undo_restores_rules_and_preserves_state_across_restart(tmp_path):
 s=make(tmp_path)
 first=Rule(kind='binding',source='prop',signal='rotation',target='stage',effect='rotation')
 second=first.model_copy(update={'effect':'scale'})
 s.install([first],0)
 s.data['state']['flags']['story']='unfinished'
 s.install([second],1)
 receipt=s.rollback()
 assert receipt['version']==3
 assert receipt['rules']==[first.model_dump()]
 reopened=make(tmp_path)
 assert reopened.data['state']['flags']['story']=='unfinished'
 assert reopened.data['version']==3
 with pytest.raises(ValueError): reopened.install([second],1)
 assert reopened.rollback()['rules']==[]
 assert reopened.rollback()['status']=='empty'

def test_corrupt_store_is_not_silently_reset(tmp_path):
 (tmp_path/'s.json').write_text('{broken')
 with pytest.raises(ValueError): make(tmp_path)

def test_rule_rejects_unregistered_objects_and_code():
 base=dict(kind='binding',source='prop',signal='rotation',target='stage',effect='rotation')
 for patch in ({'source':'camera/files'}, {'target':'shell'}, {'code':'exec(1)'}, {'threshold':float('nan')}):
  with pytest.raises(ValueError): Rule(**(base|patch))

def test_disabled_provider_is_unavailable_not_rate_limited(monkeypatch, tmp_path):
 monkeypatch.delenv('CAST_USE_BEDROCK', raising=False)
 from fastapi.testclient import TestClient
 import cast.app as appmod
 old=appmod.store
 appmod.store=make(tmp_path); appmod.agent=RuleAgent(appmod.store)
 try:
  response=TestClient(appmod.app).post('/api/intent',json={'text':'make moon light'})
  assert response.status_code==503
 finally: appmod.store=old; appmod.agent=RuleAgent(old)

def test_engine_supports_threshold_and_persistent_state():
 r=Rule(kind='binding',source='prop',signal='distance',target='stage',effect='state',
        threshold=.5,state_key='near',when='above',amount=1)
 e=StageEngine(); first=e.apply(Signal(x=.2,y=.2,distance=.8),[r.model_dump()])
 assert first['flags']['near'] is True
 second=e.apply(Signal(x=.2,y=.2,distance=.2),[r.model_dump()],first)
 assert second['flags']['near'] is True

def test_engine_applies_targeted_moon_relation():
 r=Rule(kind='relation',source='prop',signal='rotation',target='moon',effect='rotation',amount=.5)
 out=StageEngine().apply(Signal(x=.2,y=.2,rotation=120),[r.model_dump()])
 assert out['moon']['rotation']==60 and out['rotation']==120

def test_engine_supports_registered_custom_target_object():
 r=Rule(kind='relation',source='prop',signal='x',target='stage',target_object='hero',effect='position')
 out=StageEngine().apply(Signal(x=.7,y=.2),[r.model_dump()])
 assert out['objects']['hero']['x']==.7

def test_generic_and_conditions_change_relation_meaning(tmp_path):
 rule=Rule(kind='relation',source='prop',signal='distance',target='moon',effect='mask',when='below',threshold=.3,amount=.25,conditions=[{'signal':'rotation','when':'above','threshold':30}])
 engine=StageEngine(); near_closed=engine.apply(Signal(x=.5,y=.5,rotation=60,distance=.2),[rule.model_dump()]); near_open=engine.apply(Signal(x=.5,y=.5,rotation=10,distance=.2),[rule.model_dump()])
 assert near_closed['moon']['mask']==.25 and near_open['moon']['mask']==1.0

def test_generic_any_conditions_trigger_on_either_signal():
 rule=Rule(kind='relation',source='prop',signal='distance',target='moon',effect='mask',when='below',threshold=.3,amount=.5,conditions_mode='any',conditions=[{'signal':'rotation','when':'above','threshold':30}])
 out=StageEngine().apply(Signal(x=.5,y=.5,rotation=10,distance=.8),[rule.model_dump()])
 assert out['moon']['mask']==1.0
 out=StageEngine().apply(Signal(x=.5,y=.5,rotation=40,distance=.8),[rule.model_dump()])
 assert out['moon']['mask']==.5

def test_distance_condition_pauses_when_auxiliary_is_missing(tmp_path):
 rule=Rule(kind='relation',source='prop',signal='distance',target='moon',effect='mask',when='below',threshold=.3,amount=.25)
 out=StageEngine().apply(Signal(x=.5,y=.5,distance=0,auxVisible=False),[rule])
 assert out['moon']['mask']==1.0

def test_occluded_event_can_update_state_while_tracking_is_lost(tmp_path):
 rule=Rule(kind='binding',source='prop',signal='rotation',target='stage',effect='state',event='occluded',state_key='lost')
 out=StageEngine().apply(Signal(x=.5,y=.5,rotation=0,visible=False),[rule])
 assert out['visible'] is False and out['stage']['flags']['lost'] is True

def test_named_semantic_effects_are_rejected():
 import pytest
 with pytest.raises(Exception):
  Rule(kind='relation',source='prop',signal='distance',target='moon',effect='bite')

def test_enter_exit_are_threshold_edges_not_level_aliases():
 rule=Rule(kind='binding',source='prop',signal='rotation',target='moon',effect='mask',when='enter',threshold=30,amount=.2)
 engine=StageEngine(); before=engine.apply(Signal(x=.5,y=.5,rotation=10),[rule.model_dump()])
 crossed=engine.apply(Signal(x=.5,y=.5,rotation=40),[rule.model_dump()],before)
 held=engine.apply(Signal(x=.5,y=.5,rotation=50),[rule.model_dump()],crossed)
 assert before['moon']['mask']==1.0 and crossed['moon']['mask']==.2 and held['moon']['mask']==1.0


def test_preview_does_not_install(tmp_path):
 from fastapi.testclient import TestClient
 import cast.app as appmod
 old=appmod.store; appmod.store=make(tmp_path)
 try:
  rule=Rule(kind='binding',source='prop',signal='x',target='stage',effect='position')
  response=TestClient(appmod.app).post('/api/preview',json={'rules':[rule.model_dump()], 'signal':{'x':.7,'y':.2}})
  assert response.status_code==200 and response.json()['result']['x']==.7
  assert appmod.store.data['version']==0 and appmod.store.data['rules']==[]
 finally: appmod.store=old

def test_rules_diff_and_unregistered_target_are_explicit(tmp_path):
 from fastapi.testclient import TestClient
 import cast.app as appmod
 old=appmod.store; appmod.store=make(tmp_path)
 try:
  base=Rule(kind='binding',source='prop',signal='x',target='stage',effect='position')
  changed=Rule(kind='binding',source='prop',signal='rotation',target='moon',effect='rotation',amount=.5)
  response=TestClient(appmod.app).post('/api/rules/diff',json={'rules':[changed.model_dump()]})
  body=response.json(); assert len(body['added'])==1 and len(body['removed'])==0
  assert TestClient(appmod.app).post('/api/install',json={'rules':[base.model_dump()], 'expected_version':0}).status_code==200
  unknown=Rule(kind='relation',source='prop',signal='x',target='stage',target_object='missing',effect='position')
  rejected=TestClient(appmod.app).post('/api/install',json={'rules':[unknown.model_dump()], 'expected_version':1})
  assert rejected.status_code==409 and 'not registered' in rejected.json()['detail']
 finally: appmod.store=old

def test_rule_patch_is_atomic_and_versioned(tmp_path):
 from fastapi.testclient import TestClient
 import cast.app as appmod
 old=appmod.store; appmod.store=make(tmp_path)
 try:
  client=TestClient(appmod.app)
  rule=Rule(kind='binding',source='prop',signal='x',target='stage',effect='position').model_dump()
  assert client.post('/api/rules/patch',json={'expected_version':0,'operations':[{'op':'add','rule':rule}]}).status_code==200
  changed={**rule,'signal':'rotation','effect':'rotation'}
  assert client.post('/api/rules/patch',json={'expected_version':1,'operations':[{'op':'replace','index':0,'rule':changed}]}).status_code==200
  assert appmod.store.data['rules'][0]['signal']=='rotation'
  assert client.post('/api/rules/patch',json={'expected_version':1,'operations':[{'op':'remove','index':0}]}).status_code==409
 finally: appmod.store=old

def test_provider_failure_never_fakes_output(monkeypatch, tmp_path):
 monkeypatch.setenv('CAST_PROVIDER','vertex')
 def unavailable():
  raise ValueError('Vertex credentials unavailable')
 monkeypatch.setattr('cast.agent.create_model', unavailable)
 store=make(tmp_path)
 with pytest.raises(Exception, match='Vertex credentials unavailable'):
  RuleAgent(store).generate('make the moon glow')
 assert store.data['rules']==[] and store.data['version']==0


def test_scene_objects_are_atomically_registered(tmp_path):
 s=make(tmp_path)
 receipt=s.update_scene([SceneObject(id='hero',label='Hero',kind='character'), SceneObject(id='lamp',label='Lamp',kind='light')],0)
 assert receipt['version']==1 and set(s.data['state']['scene'])=={'hero','lamp'}
 with pytest.raises(ValueError, match='version conflict'):
  s.update_scene([SceneObject(id='hero',label='Hero')],0)

def test_object_replacement_keeps_identity_and_audits_previous(tmp_path):
 s=make(tmp_path); s.update_scene([SceneObject(id='hero',label='Hero')],0)
 receipt=s.replace_object(SceneObject(id='hero',label='Replaced hero',kind='character',x=.8),1)
 assert receipt['status']=='object_replaced' and receipt['previous']['label']=='Hero'
 assert s.data['state']['scene']['hero']['x']==.8
 restored=s.rollback_scene()
 assert restored['status']=='scene_rolled_back' and restored['objects']['hero']['label']=='Hero'

def test_events_endpoint_supports_bounded_filtered_replay(tmp_path):
 from fastapi.testclient import TestClient
 import cast.app as appmod
 old=appmod.store; appmod.store=make(tmp_path)
 try:
  appmod.store.event('custom', {'ok': True}); appmod.store.event('other', {})
  response=TestClient(appmod.app).get('/api/events?type=custom&limit=1')
  body=response.json(); assert len(body['events'])==1 and body['events'][0]['type']=='custom' and body['next']==1
 finally: appmod.store=old

def test_tracker_has_safe_optional_backend():
 from cast.tracker import backend_name, detect
 assert backend_name() in ('opencv-aruco','colour-fallback')
 assert detect(None, 1, 1) == []

def test_explain_returns_human_readable_rule_semantics(tmp_path):
 from fastapi.testclient import TestClient
 import cast.app as appmod
 old=appmod.store; appmod.store=make(tmp_path)
 try:
  rule=Rule(kind='relation',source='prop',signal='distance',target='stage',target_object='hero',effect='light',when='above',threshold=.4)
  body=TestClient(appmod.app).post('/api/explain',json={'rules':[rule.model_dump()]}).json()
  assert 'hero' in body['explanation'][0] and 'distance' in body['explanation'][0]
 finally: appmod.store=old

def test_explain_surfaces_composed_conditions(tmp_path):
 from fastapi.testclient import TestClient
 import cast.app as appmod
 old=appmod.store; appmod.store=make(tmp_path)
 try:
  rule=Rule(kind='relation',source='prop',signal='distance',target='moon',effect='mask',when='below',threshold=.3,conditions=[{'signal':'rotation','when':'above','threshold':30}])
  body=TestClient(appmod.app).post('/api/explain',json={'rules':[rule.model_dump()]}).json()
  assert 'also rotation above 30' in body['explanation'][0]
 finally: appmod.store=old

def test_attach_follows_and_detaches(tmp_path):
 from cast.engine import StageEngine
 from cast.schemas import Signal
 e=StageEngine(); rules=[{"kind":"binding","source":"prop","signal":"distance","target":"stage","target_object":"B","effect":"attach","when":"below","threshold":.5}]
 first=e.apply(Signal(x=.2,y=.2,distance=.2,visible=True,auxVisible=True),rules,{'objects':{'stage':{'x':.2,'y':.2},'B':{'x':.3,'y':.2}},'last_signal':{}})
 second=e.apply(Signal(x=.6,y=.2,distance=.2,visible=True,auxVisible=True),rules,first)
 assert second['objects']['B']['x'] > .5

def test_replay_rejects_target_missing_from_snapshot(tmp_path):
 from fastapi.testclient import TestClient
 import cast.app as appmod
 old=appmod.store; appmod.store=make(tmp_path)
 try:
  response=TestClient(appmod.app).post('/api/replay',json={
   'initial':{'objects':{'stage':{'x':.2,'y':.5}}},
   'frames':[{'t':0,'signal':{'x':.2,'y':.5}}],
   'rules':[{'kind':'relation','source':'prop','signal':'x','target':'stage',
             'target_object':'missing','effect':'position'}]})
  assert response.status_code==422 and 'not registered' in response.json()['detail']
 finally: appmod.store=old

def test_replay_resolves_scene_label_to_stable_id(tmp_path):
 from fastapi.testclient import TestClient
 import cast.app as appmod
 old=appmod.store; appmod.store=make(tmp_path)
 try:
  appmod.store.data['state']['scene']={}
  response=TestClient(appmod.app).post('/api/replay',json={
   'initial':{'objects':{'stage':{'x':.2,'y':.5},'B':{'x':.3,'y':.5,'label':'Cargo'}}},
   'frames':[{'t':0,'signal':{'x':.2,'y':.5,'speed':.8}}],
   'rules':[{'kind':'binding','source':'prop','signal':'speed','target':'Cargo','effect':'detach'}]})
  assert response.status_code==200
 finally: appmod.store=old

def test_recording_is_persisted_and_exported(tmp_path):
 from fastapi.testclient import TestClient
 import cast.app as appmod
 old=appmod.store; appmod.store=make(tmp_path)
 try:
  payload={'id':'play-check','initial':{'objects':{'stage':{'x':.2,'y':.5}}},
   'frames':[{'t':0,'signal':{'x':.2,'y':.5}}], 'rules':[], 'version':0}
  # A recording may be captured before any rule exists; validate and persist it.
  response=TestClient(appmod.app).post('/api/recording',json=payload)
  assert response.status_code==200
  exported=TestClient(appmod.app).get('/api/export').json()
  assert exported['recordings'][0]['id']=='play-check'
 finally: appmod.store=old

def test_object_replace_and_remove_sync_runtime_namespace(tmp_path):
 s=make(tmp_path); s.update_scene([SceneObject(id='hero',label='Hero')],0)
 s.data['state']['runtime']['objects']['hero']['flags']['attached']=True
 s.replace_object(SceneObject(id='hero',label='New Hero',kind='character',x=.8,y=.2),1)
 live=s.data['state']['runtime']['objects']['hero']
 assert (live['x'],live['y'],live['visible'])==(.8,.2,True)
 assert live['flags']['attached'] is True
 s.remove_object('hero',2)
 assert 'hero' not in s.data['state']['runtime']['objects']

def test_scene_rollback_syncs_runtime_namespace(tmp_path):
 s=make(tmp_path); s.update_scene([SceneObject(id='hero',label='Hero')],0)
 s.update_scene([SceneObject(id='lamp',label='Lamp',kind='light')],1)
 s.data['state']['runtime']['objects']['lamp']['flags']['lit']=True
 s.rollback_scene()
 assert 'lamp' not in s.data['state']['runtime']['objects']
 assert s.data['state']['runtime']['objects']['hero']['x']==.5
