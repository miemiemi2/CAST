"""Localhost-only Strands gateway for a Mac connected through SSH.

Only intent and scene data cross the tunnel. Video stays in the browser and
installation stays in the Mac's versioned store.
"""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from .agent import RuleAgent, AgentError
from .schemas import Rule, SceneObject
from .store import StageStore


class ProposalInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    text: str = Field(min_length=3, max_length=500)
    base_version: int = Field(ge=0)
    current_rules: list[Rule] = Field(default_factory=list, max_length=8)
    scene: dict[str, SceneObject] = Field(default_factory=dict, max_length=32)
    recent_intents: list[str] = Field(default_factory=list, max_length=6)


app = FastAPI(title='CAST Strands gateway')
store = StageStore(os.getenv('CAST_GATEWAY_STORE', str(Path.home()/'.local/share/cast/model-journal.json')))


@app.get('/health')
def health():
    agent = RuleAgent(store)
    return {'ok': True, 'provider': agent.provider, 'calls': agent.calls, 'max_calls': agent.max_calls}


@app.post('/propose')
def propose(req: ProposalInput):
    agent = RuleAgent(store)
    try:
        rules = agent.generate(req.text, {
            'base_version': req.base_version,
            'current_rules': [rule.model_dump() for rule in req.current_rules],
            'scene': {key: obj.model_dump() for key, obj in req.scene.items()},
            'recent_intents': req.recent_intents,
        })
        return {'rules': [rule.model_dump() for rule in rules], **agent.last_proposal,
                'calls': agent.calls, 'origin': 'agent'}
    except AgentError as error:
        raise HTTPException(503, str(error)) from error
