import copy
import pytest
from fastapi.testclient import TestClient
from cast.store import StageStore
from cast import providers


def test_vertex_uses_strands_and_bounded_client(monkeypatch):
    pytest.importorskip('google.genai')
    monkeypatch.setenv('CAST_PROVIDER','vertex')
    monkeypatch.delenv('CAST_MODEL_ID', raising=False)
    model=providers.create_model()
    assert model.__class__.__name__=='GeminiModel'
    assert model.client_args['vertexai'] is True
    assert model.client_args['http_options']['retry_options']['attempts']==1
    assert model.config['params']['max_output_tokens']==1024


def test_remote_proposal_preserves_snapshot_and_leaves_install_local(tmp_path,monkeypatch):
    import cast.app as module
    import httpx
    store=StageStore(tmp_path/'state.json')
    monkeypatch.setattr(module,'store',store)
    monkeypatch.setenv('CAST_AGENT_URL','http://127.0.0.1:18765')
    snapshot=copy.deepcopy(store.data)
    def remote(url, *, json, timeout):
        assert json['base_version']==0 and json['current_rules']==[]
        # A concurrent edit occurs while the model is thinking.
        store.data['version']=1
        return httpx.Response(200,json={'base_version':0,'provider':'vertex','reply':'Half speed',
            'rules':[{'kind':'binding','source':'prop','target':'moon',
                      'signal':'rotation','effect':'rotation','amount':.5}]},
            request=httpx.Request('POST',url))
    monkeypatch.setattr(module.httpx,'post',remote)
    client=TestClient(module.app)
    response=client.post('/api/intent',json={'text':'Rotate the moon at half speed'})
    assert response.status_code==200
    result=response.json()
    assert result['base_version']==0 and store.data['rules']==snapshot['rules']
    stale=client.post('/api/install',json={'rules':result['rules'],'expected_version':0,'origin':'agent'})
    assert stale.status_code==409 and store.data['rules']==[]


def test_remote_failure_does_not_install(tmp_path,monkeypatch):
    import cast.app as module
    import httpx
    store=StageStore(tmp_path/'state.json')
    monkeypatch.setattr(module,'store',store)
    monkeypatch.setenv('CAST_AGENT_URL','http://127.0.0.1:18765')
    def failed(*args, **kwargs):
        raise httpx.ConnectError('unavailable')
    monkeypatch.setattr(module.httpx,'post',failed)
    response=TestClient(module.app).post('/api/intent',json={'text':'Turn the moon'})
    assert response.status_code==503
    assert store.data['version']==0 and store.data['rules']==[]


def test_paged_event_filter_never_repeats_or_skips(tmp_path,monkeypatch):
    import cast.app as module
    store=StageStore(tmp_path/'state.json'); monkeypatch.setattr(module,'store',store)
    for i,kind in enumerate(['other','other','wanted','other','wanted']):
        store.event(kind,{'index':i})
    client=TestClient(module.app); cursor=0; collected=[]
    for _ in range(5):
        page=client.get(f'/api/events?since={cursor}&type=wanted&limit=2').json()
        collected.extend(e['payload']['index'] for e in page['events'])
        if page['next']==cursor: break
        cursor=page['next']
    assert collected==[2,4] and cursor==5


def test_invalid_origin_has_no_partial_install(tmp_path):
    from cast.schemas import Rule
    store=StageStore(tmp_path/'state.json'); before=copy.deepcopy(store.data)
    rule=Rule(kind='binding',source='prop',target='moon',signal='rotation',effect='rotation')
    with pytest.raises(ValueError,match='origin'):
        store.install([rule],0,'invented')
    assert store.data==before
