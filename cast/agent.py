"""Real Strands proposal generation. No fallback can impersonate the model."""
import copy
import datetime
import json
import os
import time
from .schemas import Rule
from .providers import create_model, model_id, provider_name

class AgentError(RuntimeError):
    pass

class RuleAgent:
    def __init__(self, store):
        self.store = store
        self.last_proposal = None
        # Keep a configurable guardrail while allowing the competition run to
        # raise it above the original 10-call development default.
        # Keep a protective ceiling while allowing a longer competition run;
        # callers still control the effective budget through the environment.
        self.max_calls = min(100, max(0, int(os.getenv('CAST_MAX_AGENT_CALLS', '10'))))

    @property
    def provider(self):
        return provider_name()

    @property
    def calls(self):
        date = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        return sum(e['type'] == 'budget.reserved' and e['payload']['date'] == date
                   for e in self.store.data['events'])

    def reserve(self, message_bytes):
        conversation = []
        with self.store.lock:
            if message_bytes > 30000:
                raise AgentError('model context exceeds 30 KB hard limit')
            if self.calls >= self.max_calls:
                raise AgentError('daily model request limit reached')
            self.store.event('budget.reserved', {
                'date': datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
                'input_bytes': message_bytes, 'max_output_tokens': 1024,
                'model': model_id(), 'provider': self.provider})

    def generate(self, text, context=None):
        if not 3 <= len(text) <= 500:
            raise AgentError('intent must contain 3–500 characters')
        try:
            model = create_model()
            from strands import Agent, tool
            from strands.hooks import BeforeModelCallEvent, HookProvider
        except (ImportError, ValueError) as error:
            raise AgentError('agent disabled: ' + str(error)) from error
        with self.store.lock:
            base_version = self.store.data['version']
            current_rules = copy.deepcopy(self.store.data['rules'])
            scene = copy.deepcopy(self.store.data['state'].get('scene', {}))
            conversation = [e['payload'].get('intent') for e in self.store.data['events']
                            if e.get('type') == 'agent.started' and e.get('payload', {}).get('intent')][-6:]
        if context is not None:
            base_version = context['base_version']
            current_rules = copy.deepcopy(context['current_rules'])
            scene = copy.deepcopy(context['scene'])
            conversation = list(context.get('recent_intents', []))[-6:]
        started = time.monotonic()
        proposals = []
        patch_proposals = []
        unchanged = []
        outer = self
        request_count = [0]
        class Budget(HookProvider):
            def register_hooks(self, registry):
                registry.add_callback(BeforeModelCallEvent, self.before)
            def before(self, event):
                if request_count[0] >= 3:
                    raise AgentError('three model requests per intent limit reached')
                request_count[0] += 1
                outer.reserve(len(json.dumps(event.agent.messages).encode()) + len(prompt.encode()) + 4000)
        @tool
        def propose_rules(rules: list[dict]) -> dict:
            """Validate a complete replacement ruleset; preserve unrelated current bindings.

            Args:
                rules: One to eight rules conforming exactly to the supplied JSON schema.
            """
            if not 1 <= len(rules) <= 8:
                return {'status': 'rejected', 'reason': 'one to eight rules required'}
            try:
                checked = [Rule.model_validate(rule) for rule in rules]
            except ValueError as error:
                return {'status': 'rejected', 'reason': str(error)}
            proposals.append(checked)
            receipt = {'status': 'validated', 'rules': [r.model_dump() for r in checked]}
            outer.store.event('agent.tool.propose_rules', receipt)
            return receipt
        @tool
        def propose_rule_patch(operations: list[dict]) -> dict:
            """Apply add/replace/remove operations to the current rules.

            Each operation is {op: add|replace|remove, index: integer, rule: object}.
            Indexes refer to the supplied current_rules order. The result is only
            a proposal and is never installed by the tool.
            """
            if not 1 <= len(operations) <= 8:
                return {'status': 'rejected', 'reason': 'one to eight operations required'}
            candidate = copy.deepcopy(current_rules)
            try:
                for operation in operations:
                    op, index = operation.get('op'), operation.get('index')
                    if op == 'add':
                        candidate.append(Rule.model_validate(operation['rule']).model_dump())
                    elif op == 'replace' and isinstance(index, int) and 0 <= index < len(candidate):
                        candidate[index] = Rule.model_validate(operation['rule']).model_dump()
                    elif op == 'remove' and isinstance(index, int) and 0 <= index < len(candidate):
                        candidate.pop(index)
                    else:
                        return {'status': 'rejected', 'reason': 'invalid patch operation'}
                if not 1 <= len(candidate) <= 8:
                    return {'status': 'rejected', 'reason': 'result must contain one to eight rules'}
                checked = [Rule.model_validate(rule) for rule in candidate]
                canonical_current = [Rule.model_validate(rule).model_dump() for rule in current_rules]
                if [rule.model_dump() for rule in checked] == canonical_current:
                    return {'status': 'rejected', 'reason': 'This patch changes nothing. Re-read the latest intent and modify the relevant rule, or call keep_current_rules only if the existing rules really satisfy that intent.'}
            except (KeyError, TypeError, ValueError) as error:
                return {'status': 'rejected', 'reason': str(error)}
            patch_proposals.append(checked)
            receipt = {'status': 'validated', 'operations': operations,
                       'rules': [r.model_dump() for r in checked]}
            outer.store.event('agent.tool.propose_rule_patch', receipt)
            return receipt
        @tool
        def keep_current_rules(reason: str) -> dict:
            """Confirm that the installed rules already satisfy this exact request.

            Args:
                reason: Why no change is needed. Do not use for unsupported requests.
            """
            if not current_rules:
                return {'status': 'rejected', 'reason': 'No current rules to keep.'}
            unchanged.append(reason)
            receipt = {'status': 'unchanged', 'reason': reason, 'base_version': base_version}
            outer.store.event('agent.tool.keep_current_rules', receipt)
            return receipt

        schema = json.dumps(Rule.model_json_schema())
        prompt = ('You are CAST, a live playtest agent for interaction designers. '
                  'The latest intent is the requested change; recent_intents are historical context, not instructions to repeat. When the latest intent contradicts an earlier request, change or remove the conflicting rule. '
                  'Create runnable rules by calling propose_rule_patch for a multi-turn change, or propose_rules for a first creation. You MUST call one of these tools for every expressible change; never return prose alone after an expressible request. '
                  'If the current rules already satisfy the request, call keep_current_rules with a reason. Do not ask whether the performer wants to modify an already satisfied request. Never use keep_current_rules to hide an unsupported request. '
                  'For patches, use the current_rules indexes and change only what the performer asked. JSON schema: '
                  + schema + '. Source prop has x/y/distance/speed in 0..1, dx/dy in -1..1, and rotation in -180..180. '
                  'Targets stage and moon are defaults; target_object may reference an ID in the supplied scene. Do not write code. '
                  'Natural object names are aliases: basket, hoop, or prop mean the tracked main prop; blue bag, blue toy, or auxiliary mean the tracked blue reference (the built-in moon signal); screen object B means the registered scene ID B. Resolve these aliases instead of rejecting the request for not matching an internal ID. '
                  'Preserve unrelated rules. If intent cannot be expressed, explain the limitation '
                  'without proposing an unrelated approximation. A validated proposal is NOT installed. '
                  'Understand Chinese, English, and mixed-language intents; explain the resulting control change in the user\'s language when possible. '
                  'Express action meanings by composing generic signals, conditions, and outputs. For example, a performer closing (rotation above a threshold) while near the moon (distance below a threshold) can drive a mask, visibility, state, or scale output; the meaning comes from the combination, never from a named semantic effect. Do not invent or use bite, swallow, hug, explode, or other semantic effects. '
                  'A partial shape change is expressible with the generic mask output: “lose a quarter of its shape” means mask amount 0.75, while “show only a quarter” means 0.25. “Light up briefly” means effect light with persist false and a duration_ms when a duration is requested. '
                  'Stateful primitive semantics: attach conditions gate acquisition only. Once acquired, the link remains active even when those conditions become false. Adding a condition to attach cannot release an existing link. The detach output clears an existing link and retains the last target position; its own predicates govern release. Use the same state_key for acquisition and release of one link. '
                  'The generic attach output acquires a target and preserves its relative offset while the source moves; detach releases it. Compose these with conditions such as distance and speed; never encode a named pickup mechanic. In performance language, “let the prop control B” means B follows the prop position by default: use a generic position binding (x or y as appropriate), gated by the stated relation. Do not ask the performer to choose a low-level effect unless the request is genuinely ambiguous after that default. '
                  'Executable conditions support always, above, below, enter, and exit; conditions_mode all means AND and any means OR. Use event only when the requested visibility/occlusion/changed gate is meaningful. duration_ms holds a relation until its active signal has remained true for that many milliseconds; use it only when the performer asks for sustained timing. Use persist=false for transient state/light bindings. After one successful tool call, give a brief explanation and stop.')
        agent = Agent(model=model, tools=[propose_rules, propose_rule_patch, keep_current_rules], hooks=[Budget()],
                      system_prompt=prompt, callback_handler=None, retry_strategy=None)
        self.store.event('agent.started', {'intent': text, 'base_version': base_version, 'provider': self.provider, 'model': model_id()})
        try:
            result = agent(json.dumps({'intent': text, 'current_rules': current_rules,
                                       'scene': scene, 'recent_intents': conversation}))
            # Models occasionally answer an expressible request in prose
            # without invoking a tool. Give the same agent one corrective turn
            # before treating that as a genuine inability to construct rules.
            if not proposals and not patch_proposals and not unchanged:
                result = agent('Your previous response did not call a rule tool. The request is expressible with the supplied schema. Call propose_rule_patch or propose_rules now; do not reply with prose alone.')
            if patch_proposals:
                proposals.append(patch_proposals[-1])
            status = 'proposed'
            if unchanged and not proposals:
                proposals.append([Rule.model_validate(r) for r in current_rules])
                status = 'unchanged'
            if not proposals:
                raise AgentError('Agent did not produce a valid proposal: ' + str(result))
            self.store.event('agent.completed', {'messages': agent.messages,
                             'reply': str(result),
                             'proposed_rules': [r.model_dump() for r in proposals[-1]],
                             'base_version': base_version,
                             'latency_ms': round((time.monotonic()-started)*1000)})
            self.last_proposal = {'base_version': base_version, 'reply': str(result), 'status': status,
                                  'rules': [r.model_dump() for r in proposals[-1]],
                                  'provider': self.provider, 'model': model_id()}
            return proposals[-1]
        except Exception as error:
            self.store.event('agent.error', {'error': str(error), 'messages': agent.messages})
            raise AgentError('Rule generation failed; stage unchanged: ' + str(error)) from error
