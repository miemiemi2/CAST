from typing import Literal, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator

class Signal(BaseModel):
    # A temporarily occluded frame remains a valid invisible signal.
    x: float = Field(default=.5, ge=0, le=1); y: float = Field(default=.5, ge=0, le=1)
    rotation: float = Field(default=0, ge=-180, le=180)
    distance: float = Field(default=0, ge=0, le=1)
    speed: float = Field(default=0, ge=0, le=1)
    dx: float = Field(default=0, ge=-1, le=1)
    dy: float = Field(default=0, ge=-1, le=1)
    visible: bool = True
    auxVisible: bool = True
    time_ms: float | None = Field(default=None, ge=0)
    distance_object: str | None = Field(default=None, pattern=r'^[A-Za-z][A-Za-z0-9_-]{0,31}$')

class SceneObject(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    id: str = Field(pattern=r'^[A-Za-z][A-Za-z0-9_-]{0,31}$')
    label: str = Field(min_length=1, max_length=80)
    kind: Literal['prop', 'character', 'light', 'anchor'] = 'prop'
    x: float = Field(default=.5, ge=0, le=1)
    y: float = Field(default=.5, ge=0, le=1)
    rotation: float = Field(default=0, ge=-180, le=180)
    visible: bool = True

class SceneUpdate(BaseModel):
    expected_version: int = Field(ge=0)
    objects: list[SceneObject] = Field(min_length=1, max_length=32)

class Condition(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    signal: Literal['x','y','rotation','distance','speed','dx','dy']
    when: Literal['always', 'above', 'below', 'enter', 'exit'] = 'always'
    threshold: float = Field(default=.5, ge=-180, le=180)

class ObjectReplace(BaseModel):
    expected_version: int = Field(ge=0)
    object: SceneObject

class ObjectRemove(BaseModel):
    expected_version: int = Field(ge=0)
    id: str = Field(pattern=r'^[A-Za-z][A-Za-z0-9_-]{0,31}$')

class Rule(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    kind: Literal['binding','relation']
    source: Literal['prop']
    signal: Literal['x','y','rotation','distance','speed','dx','dy']
    # Built-in actors are stage/moon; registered scene objects (for example
    # cargo) may also be addressed directly. The store validates object IDs.
    target: str = Field(pattern=r'^[A-Za-z][A-Za-z0-9_-]{0,31}$')
    target_object: str | None = Field(default=None, pattern=r'^[A-Za-z][A-Za-z0-9_-]{0,31}$')
    effect: Literal['position','rotation','scale','visibility','mask','state','light','attach','detach']
    threshold: float = Field(default=0.5, ge=-180, le=180)
    state_key: str = Field(default='active', max_length=32)
    version: int = Field(default=1, ge=1)
    # Optional declarative controls.  They remain data-only so a model can
    # propose rules without ever injecting executable code.
    when: Literal['always', 'above', 'below', 'enter', 'exit'] = 'always'
    event: Literal['frame', 'visible', 'occluded', 'changed'] = 'frame'
    duration_ms: int = Field(default=0, ge=0, le=600000)
    amount: float = Field(default=1.0, ge=-10, le=10)
    persist: bool = True
    # Additional predicates are generic logic, not named actions. All must be
    # true for the rule to run (an empty list preserves legacy semantics).
    conditions: list[Condition] = Field(default_factory=list, max_length=4)
    conditions_mode: Literal['all', 'any'] = 'all'

    @model_validator(mode='after')
    def validate_target(self):
        # Built-ins use lowercase names; registered scene IDs conventionally
        # use an uppercase leading character (for example B or Cargo).
        if self.target not in {'stage', 'moon'} and not self.target[:1].isupper():
            raise ValueError('target must be stage, moon, or a registered scene object ID')
        return self

class Intent(BaseModel):
    text: str = Field(min_length=3, max_length=500)

class InstallRequest(BaseModel):
    rules: list[Rule] = Field(min_length=1, max_length=8)
    expected_version: int = Field(ge=0)
    origin: Literal['human', 'agent', 'system'] = 'human'

class Event(BaseModel):
    type: str; timestamp: float; payload: dict[str, Any]
