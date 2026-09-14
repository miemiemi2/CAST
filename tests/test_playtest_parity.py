"""Same pointer input must obey conjunction and detach in both runtimes."""
import json
from pathlib import Path
import subprocess
from cast.engine import StageEngine
from cast.schemas import Signal, Rule


def test_pointer_attach_detach_matches_browser():
    initial = {'stage': {'x': .1, 'y': .5}, 'B': {'x': .5, 'y': .5}}
    rules = [Rule(kind='binding', source='prop', signal='distance', target='B', effect='attach',
                  conditions=[{'signal': 'distance', 'when': 'below', 'threshold': .1},
                              {'signal': 'speed', 'when': 'below', 'threshold': .2}]).model_dump(),
             Rule(kind='relation', source='prop', signal='speed', target='B', effect='detach',
                  when='above', threshold=.5).model_dump()]
    # Far+slow, near+fast, near+slow, continued follow, fast release, remain released.
    inputs = [( .1,.1), (.48,.8), (.5,.1), (.6,.1), (.75,.8), (.9,.1)]
    signals = [Signal(x=x,y=.5,speed=speed,time_ms=i*100,distance_object='B').model_dump()
               for i,(x,speed) in enumerate(inputs)]
    engine=StageEngine(); state={'objects':initial}; expected=[]
    for signal in signals:
        state=engine.apply(Signal(**signal),rules,state)
        expected.append(state['objects']['B']['x'])
    assert expected == [.5,.5,.5,.6,.6,.6]
    module=(Path(__file__).resolve().parents[1]/'static/tracking.mjs').as_uri()
    script=f"""import {{applyRules}} from {json.dumps(module)};
    const data=JSON.parse(process.argv[1]);let state=data.initial;let results=[];
    for(const signal of data.signals){{state=applyRules(signal,data.rules,state);results.push(state.B.x)}}
    console.log(JSON.stringify(results));"""
    result=subprocess.run(['node','--input-type=module','-e',script,json.dumps({'initial':initial,'signals':signals,'rules':rules})],capture_output=True,text=True,check=True)
    assert json.loads(result.stdout)==expected
