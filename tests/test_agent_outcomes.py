"""Exercise tool outcomes without a provider call or camera."""
import sys
from types import SimpleNamespace
import pytest
from cast.agent import RuleAgent, AgentError
from cast.schemas import Rule
from cast.store import StageStore


def setup_agent(tmp_path, monkeypatch, action):
    import cast.agent as module
    monkeypatch.setattr(module, 'create_model', lambda: object())
    class FakeAgent:
        def __init__(self, *, tools, **kwargs):
            self.tools = {t.__name__: t for t in tools}
            self.messages = []
        def __call__(self, prompt):
            return action(self.tools)
    monkeypatch.setitem(sys.modules, 'strands', SimpleNamespace(Agent=FakeAgent, tool=lambda f:f))
    monkeypatch.setitem(sys.modules, 'strands.hooks', SimpleNamespace(BeforeModelCallEvent=object, HookProvider=object))
    store = StageStore(tmp_path/'state.json')
    rule = Rule(kind='binding', source='prop', signal='rotation', target='moon', effect='mask', amount=.75)
    store.install([rule], 0)
    return RuleAgent(store), rule


def test_existing_control_is_an_explicit_success(tmp_path, monkeypatch):
    def action(tools):
        assert tools['keep_current_rules']('The requested mask is already installed')['status']=='unchanged'
        return 'Already installed.'
    agent, rule = setup_agent(tmp_path, monkeypatch, action)
    version = agent.store.data['version']
    assert agent.generate('Keep this control') == [rule]
    assert agent.last_proposal['status'] == 'unchanged'
    assert agent.store.data['version'] == version


def test_refusal_is_not_misrepresented_as_success(tmp_path, monkeypatch):
    agent, _ = setup_agent(tmp_path, monkeypatch, lambda tools: 'Unsupported request.')
    with pytest.raises(AgentError, match='did not produce'):
        agent.generate('An unsupported change')
    assert agent.last_proposal is None


def test_patch_tool_is_registered_and_returns_proposal(tmp_path, monkeypatch):
    def action(tools):
        result = tools['propose_rule_patch']([{'op':'replace','index':0,'rule':{
            'kind':'binding','source':'prop','signal':'rotation','target':'moon','effect':'mask','amount':.5}}])
        assert result['status']=='validated'
        return 'Changed the mask.'
    agent, original = setup_agent(tmp_path, monkeypatch, action)
    result = agent.generate('Show half instead')
    assert result[0].amount == .5
    assert agent.store.data['rules'][0]['amount'] == original.amount
