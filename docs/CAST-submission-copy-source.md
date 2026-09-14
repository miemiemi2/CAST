# CAST｜完整提交文案

定位：Same play. Different rules.

本文件汇总包内 Markdown 文案。纯旁白、SRT、Mermaid 图源、待填信息和许可证请使用同包独立文件。


---

# 文件：00-先看这个.md

# CAST｜提交文案包

本包是可复制的文案、录制脚本和提交检查，不是另一份产品 Goal，也不是已经录好的视频。没有代为发布、上传、修改项目或提交比赛。

## 统一口径

**项目名：CAST**  
**主标语：Same play. Different rules.**  
**定位：A playtest agent for comparing mechanic changes against the same recorded inputs.**  
**赛道建议：Professional Agents**

中文理解：玩一次，提出改动，Agent 实现候选；同一段操作分别在新旧规则下执行，设计师比较后亲手试、决定留哪版。

不再用“预测你会有什么手感”作承诺。同输入比较显示规则带来的结果差异；真正的手感、玩家适应与喜好仍需亲手试玩和后续研究。

## 直接使用顺序

1. `01-Devpost-EN.md`：项目名、短介绍、完整项目故事。
2. `02-表单与评委测试说明.md`：赛道理由、技术说明、测试指引、链接字段。
3. `03-README-EN.md`：仓库正文。启动命令必须由 Codex 在最终代码上复跑。
4. `04-视频分镜与旁白.md`、`05-voiceover-en.txt`、`06-captions-en.srt`：同一条 3 分 30 秒视频的画面、英文旁白及拟定字幕。
5. `07-界面与截图文案.md`、`08-评委问答与短Pitch.md`、`09-视频发布与社媒.md`：页面、截图、问答和视频发布所需文字。
6. `10-架构说明.md`、`10-architecture.mmd`：架构图文案与 Mermaid 图源；还需要从图源导出并核对最终图片。
7. `11-事实边界与发布检查.md`：所有发布前检查、证据边界、官方要求和来源。
8. `12–14`：三篇可选 Builder Center 博文草稿，主题不同；只复制分隔线后的英文正文，标题用文件首标题。不要挤占必须交付的产品和视频。
9. `15-给Codex的执行指令.md`、`16-待填信息.json`：交给 Codex 落地。
10. `17-LICENSE-MIT.template.txt`、`18-项目与素材声明.md`：许可证完整模板及公开披露。

## 这不是“已经全部做完”的声明

最近一次开发者状态报告称：真实 Strands 已生成第一轮 attach 规则和第二轮 detach patch，运行器已得到预期结果；浏览器完整记录、对照、Try/Keep/Revert、第二轮页面验收和录屏仍待收口。本包没有把这些待办改写成已经实测成功。

**01、03、04、05、06、09 中描述完整产品流的发布稿，只有在 11 中对应行为验收通过后才启用。** 未通过时使用 11 中的“当前状态诚实说明”，不要一边保留失败行为，一边上传完整成功叙事。

字幕时间是拟定剪辑时间，不是对尚未提供的视频做过对齐。旁白是录音文字，不是音频文件。

## 只需补实际信息，不需重写正文

Codex 能从最终项目取得的仓库地址、实际按钮名、依赖版本、文件路径和证据路径，由 Codex 自行填；只有公开署名、AWS Builder ID、必要账号授权等确实无法取得的内容再找用户。

公开正文不要出现私有 IP、个人邮箱、ADC 文件、密钥、服务账号或本机路径。所有 `[FILL: ...]` 必须填入真实值或删除对应可选项。

关键事实：本包以最后已给出的状态为依据，不包含新的远程运行验证；原 ZIP 是旧版 Camera CAST，不能用它证明转向后的 UI 已完成。


---

# 文件：01-Devpost-EN.md

# Devpost submission copy

编辑说明：以下为“完整浏览器流程验收通过后”的发布稿。只复制各字段正文；不要复制本说明。未通过的能力不得照稿宣称完成，替代状态段见 11。下列是可复用字段，不代表已经读取登录后的全部比赛表单。

## Project name

CAST

## Elevator pitch

Change a game mechanic with Strands, then replay the same recorded inputs under both versions before deciding what to keep.

## Tagline

Same play. Different rules.

## Project story — copy from the next heading

## Inspiration

A mechanic change is a hypothesis: “This would work better if…” But a new implementation alone does not show what it changes about the moment that prompted the idea.

We wanted to preserve that moment. Instead of asking a designer to recreate a fast pass, a missed pickup, or an awkward release, what if the same recorded inputs could run through both versions?

That became CAST: a Strands-powered playtest agent that turns a requested change into a candidate you can compare, try, and keep.

## What it does

CAST is for game and interaction designers working on small interactive prototypes. It connects three tasks: changing a mechanic, reproducing a recorded interaction, and comparing the result.

In our playable cargo prototype, a fast brush past an object can cause an unwanted pickup. The designer asks CAST to require a slow approach. The agent proposes a rule change, and CAST replays the recorded inputs side by side:

**OLD:** the fast pass picks up the cargo.  
**NEW:** the same fast pass leaves it alone; a slow approach can pick it up.

The designer can try the candidate directly, keep it, or discard it. A second request adds a different release behavior: a fast flick breaks the connection. CAST compares that revision against the previously accepted version.

Each comparison starts from the same scene snapshot and uses the same recorded input. The rule version changes—not the input chosen to make one version look better.

## How we built it

Strands Agents SDK handles the model-driven rule-authoring loop. The agent receives the request, the current rules, and the registered scene objects. It uses constrained tools to propose an initial ruleset or an add/replace/remove patch. An explicit no-change outcome handles requests already satisfied by the current rules.

The demonstrated model configuration uses Gemini through Google Cloud Vertex AI. We use Python, FastAPI and Pydantic for the service and rule validation, and JavaScript with HTML Canvas for the playable interface.

The model proposes a change; it does not generate the comparison footage. CAST’s application runs the candidate and the previous rules against a recorded input sequence. Version-aware acceptance and undo keep a candidate separate from the accepted mechanic.

The runtime provides reusable inputs, conditions and actions, including attachment and release. A specific requested combination is authored through the agent rather than selected by matching the prompt to a complete scripted scene.

## Challenges we ran into

The most important challenge was the boundary between a plausible rule and a working interaction. Assigning a coordinate is not the same as picking up an object: attachment has to preserve an offset, follow across frames, and release without snapping back.

Another challenge was consistency. A rule could pass a component test while the browser or a still-running service used a different state representation. We had to check what happened in the actual product, not just whether an endpoint answered.

We also changed the project’s input direction. Camera-based props introduced tracking instability that obscured the interaction. Pointer-controlled playtesting made the user’s action explicit and recordable, and gave the comparison a clearer purpose.

## Accomplishments that we're proud of

CAST turns an agent’s output into something a designer can challenge immediately. The designer is not asked to trust “I changed it.” They can compare the recorded interaction under both versions, then try the candidate themselves.

The agent takes on the implementation step. The application takes on the repeatable comparison. The designer keeps the judgment about which behavior belongs in the game.

## What we learned

There are three different claims: a model produced a rule; the runtime executed it; a person could understand and use the result. None of those automatically proves the next.

We also learned to be precise about replay. It answers what the same recorded inputs do under a changed mechanic. It does not predict how a player would adapt, prove that a mechanic is more fun, or replace a user study. Direct candidate play remains essential.

## What's next for CAST

The current scope is a purpose-built, small 2D prototype—not a Unity or Unreal integration or a general game engine. Next we want to test the workflow with designers, support additional recorded situations, and investigate an adapter for an existing prototype environment.

We are not claiming measured productivity gains or production adoption. Our immediate contribution is a working, inspectable loop:

**Play. Request a change. Compare the same inputs. Decide what to keep.**


---

# 文件：02-表单与评委测试说明.md

# Form answers and judge instructions

编辑说明：这是字段素材库，实际表单名称及字数限制以登录后的页面为准。完整 UI 流程通过后使用测试说明；未通过不得声称提供 working demo。

## Recommended track

Professional Agents

## Why this track?

CAST helps game and interaction designers evaluate a mechanic change without manually recreating the interaction that prompted it. The agent authors a constrained rule patch; the application replays the same inputs under both versions; the designer makes the final creative decision.

## What repetitive work does the agent take on?

Translating a requested mechanic change into executable rules, revising the relevant behavior, and preserving unrelated rules. CAST then connects that candidate to a repeatable old-versus-new comparison instead of leaving the designer with a code suggestion to apply and test manually.

## How do you use Strands Agents SDK?

CAST uses a Strands Agent with custom rule-authoring tools. The request includes the current rules and scene registry. `propose_rules` creates a candidate ruleset; `propose_rule_patch` proposes add, replace or remove operations; `keep_current_rules` handles a no-change outcome. Pydantic checks rule structure, and CAST’s application controls preview, replay and version-aware acceptance. Model inference uses Gemini through Vertex AI in the demonstrated configuration.

The replay runner is application logic. Do not describe it as a model tool unless the final implementation actually exposes and uses it that way.

## Built with

Strands Agents SDK, Google Gemini, Google Cloud Vertex AI, Python, FastAPI, Pydantic, JavaScript, HTML Canvas, Uvicorn.

不要为了赞助商标签加入未部署的 Amazon Bedrock、AgentCore、Lambda、DynamoDB 或其他服务。旧 Camera 依赖不是本次主路径亮点。

## Platform

Browser-based 2D prototype with a Python service. The development environment includes macOS and a remote model gateway. The final supported setup is documented in the repository.

## Judge testing instructions — public demo route

Open the demo link listed in this submission. No camera or physical props are required.

1. Follow the on-screen objective: move the player and interact with the cargo near the goal. Make a fast pass, then approach slowly. Finish the recording.
2. Ask: “Pick up the cargo only when I approach slowly. Passing it quickly should leave it where it is.”
3. Compare OLD and NEW. They replay the same recorded inputs from the same starting snapshot. Watch the pickup behavior during the fast pass.
4. Try the candidate, then keep it. Record another short interaction that includes a slow pickup followed by a fast movement.
5. Ask: “Keep the slow pickup, but release the cargo when I move quickly.” Compare the previous accepted rules with the new candidate. Try it, keep it or discard it.
6. Open Agent details to inspect the actual proposal or patch and the input/version references.

The demo demonstrates a bounded mechanic-authoring workflow. It does not accept arbitrary game source code, and it is not a commercial game integration. Model access is required to create new candidates.

## Access / credentials field

Demo URL: [FILL: PUBLIC_DEMO_URL_OR_REMOVE_IF_NO_HOSTED_DEMO]

Test build / run instructions: [FILL: PUBLIC_REPO_URL_AND_SETUP_SECTION]

Video: [FILL: PUBLIC_VIDEO_URL]

Contact for access problems: [FILL: PUBLIC_CONTACT_ADDRESS_OR_REPOSITORY_ISSUES_URL]

任何测试凭据只填平台允许的评委访问字段，不放公开项目故事、字幕或截图。没有托管演示时必须提供真正可运行的测试构建与必要访问安排；不要把 `localhost` 或私有 SSH 别名当作公开演示链接。

## Development disclosure

AI coding assistance was used during implementation and debugging, and AI assistance was used to prepare submission copy. The submitted behavior is implemented in the project and must be demonstrated by the actual runtime. Third-party libraries retain their respective licenses. Details of any pre-existing custom work are listed in the repository disclosure.

编辑说明：最后一句必须对应实际披露，不能用它替代披露。若没有旧自有代码，只有确认后才能写“None beyond standard dependencies”。

## Useful shorter descriptions

### One sentence

CAST turns a requested mechanic change into a side-by-side replay of the same recorded inputs, so designers can compare before they commit.

### Compact description

CAST is a Strands-powered playtest agent for small interactive prototypes. Describe a mechanic change, compare the same recorded inputs under the old and new rules, then try and keep the version you prefer. The agent authors the change; the runtime produces the comparison; the designer makes the decision.

### Technical summary

A bounded rule-authoring agent plus a paired replay workflow: current rules and scene context enter Strands, validated proposals become isolated candidates, and the runtime re-executes one recorded input sequence under two rule versions. A second natural-language request revises the accepted mechanic rather than replacing the project.


---

# 文件：03-README-EN.md

<!-- RELEASE DRAFT. Publish the full workflow claims only after the browser path passes the checks in 11. Re-run the setup commands on the release checkout. -->
# CAST

## Same play. Different rules.

CAST is a Strands-powered playtest agent for game and interaction designers. Request a mechanic change, compare the same recorded inputs under the old and new rules, then try the candidate and decide what to keep.

**Scope:** a small, purpose-built 2D interactive prototype. CAST is not a general game engine or a Unity/Unreal integration.

## See it working

- Video: [FILL: PUBLIC_VIDEO_URL]
- Hosted demo: [FILL: PUBLIC_DEMO_URL_OR_DELETE_THIS_LINE]
- Release / tested commit: [FILL: RELEASE_TAG_OR_COMMIT]
- Architecture: see `docs/architecture.md` and the exported diagram supplied with the submission.

No camera or physical props are needed for the pointer-based workflow.

## The workflow

Play a short interaction in the cargo prototype. CAST records its starting snapshot and input sequence. Ask for a change such as requiring a slow approach before pickup. The agent proposes a candidate; CAST compares the original and candidate rules using the same recorded inputs.

Try the candidate directly. Keep it, discard it, or request another change. A second revision can keep the pickup rule and add release on a fast movement.

The comparison is not a video filter and not two separately performed play sessions. It is a paired execution of a recorded input sequence. It shows behavior under fixed inputs; it does not predict player adaptation or establish which mechanic is more fun.

## Architecture

The browser captures pointer input and displays the playable prototype and comparison. The Python service validates rules and provides replay and versioned rule management. A Strands Agent receives the intent, scene registry and current rules, and invokes constrained authoring tools.

The demonstrated model configuration is Gemini via Google Cloud Vertex AI. The current build does not claim an Amazon Bedrock AgentCore deployment.

| Component | Responsibility |
|---|---|
| Strands Agent | Interpret the request and propose a rule change |
| Rule tools | Create a candidate, patch current rules, or report no change |
| Pydantic schema | Reject structurally invalid rule data |
| Runtime | Execute supported conditions and actions |
| Recorder / replay | Preserve input and compare rule versions |
| Versioned state | Keep candidates separate and protect acceptance |
| Designer | Try the result and choose what to keep |

## Run locally

The commands below use the package layout and dependency groups found in the supplied repository archive. Verify them on the final release, which includes the pointer/replay pivot.

Requirements: Python 3.10 or later; a modern browser; authorized Vertex AI access for natural-language creation. Node.js is used for JavaScript tests.

From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[agent,test]'
```

Configure an authorized Google Cloud project and local Application Default Credentials:

```sh
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="global"
gcloud auth application-default login
gcloud auth application-default set-quota-project "$GOOGLE_CLOUD_PROJECT"
export CAST_PROVIDER="vertex"
export CAST_MODEL_ID="gemini-2.5-flash"
```

For a direct local model connection, remove any stale remote-gateway override and start the service:

```sh
unset CAST_AGENT_URL
python -m uvicorn cast.app:app --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765`.

These commands do not create cloud permissions or grant model access. Use your own authorized project. Do not commit credential files or access tokens. ADC credentials used by application libraries are separate from an ordinary `gcloud auth login` session. See the official ADC documentation in the submission source notes.

### Existing remote gateway installation

A development installation can keep model credentials on a remote gateway and connect the local application through an authenticated private tunnel. Set `CAST_AGENT_URL` to the locally reachable tunnel endpoint and keep the gateway and tunnel running.

The private development tunnel is not a public demo URL. Do not expose an unauthenticated model gateway to the Internet.

## Try the comparison

1. Play and finish a recorded interaction.
2. Describe the mechanic change.
3. Inspect OLD / NEW replay before accepting the candidate.
4. Try the candidate with fresh input.
5. Keep or discard it. Request a second revision to continue.

Use the actual button names displayed by the release. A replay with no difference can be valid: the recorded interaction may not exercise the changed condition. Record a relevant interaction rather than inventing a difference.

## What is authored and what is fixed?

The scene, basic engine and supported action primitives are supplied by the application. The agent composes or revises rules within that vocabulary. Attachment and detachment are reusable runtime operations; a full prompt-to-scene answer must not be hardcoded.

A structurally valid proposal is not automatically behaviorally correct. Runtime comparison and direct play are separate checks.

## Evidence

The release should include a small evidence index at [FILL: ACTUAL_EVIDENCE_INDEX_PATH]. For each demonstrated comparison, identify the recorded input, starting snapshot, old rules, candidate rules, model/tool trace and observed result. Include actual references only.

Browser automation may generate pointer events for demonstration and integration testing. Such runs must be labeled as automated demonstrations, not human-user research. Developer-authored rule probes are not evidence of a model-generated change.

## Tests

```sh
python -m pytest -q
node --test tests/tracking.test.mjs
```

The existing `scripts/demo_probe.py` in the earlier archive uses synthetic signals and human-authored rules. Do not present it as proof of the new agent-driven browser workflow. Update this section with the final replay/browser test command only after that command exists and runs.

## Current boundaries

The demonstrated vocabulary is bounded. CAST does not modify arbitrary game code, claim engine integrations it lacks, or measure player enjoyment. Model generation is not guaranteed to succeed for every request. A failed proposal must leave the accepted mechanic unchanged and be reported as a failure.

Paired replay compares fixed inputs—not the actions a player would have chosen after seeing a different world. Direct candidate play is available to make that separate judgment.

## Development and licensing

AI coding assistance was used during development. See the project disclosure for incorporated prior work and third-party components. The package is intended to use the MIT license; include the complete license text and verify the copyright notice before publishing.


---

# 文件：04-视频分镜与旁白.md

# CAST｜3 分 30 秒英文视频执行稿

这是成片脚本，不是已经录制好的视频。总时长目标 03:30；前 00:28 是独立成立的 Hero。根据实际模型等待和行为发生时间调整，不为凑时间填空镜头。

**公开主张：Same play. Different rules.**

全部素材来自真实运行的产品、真实模型调用记录和自制文字/图示。无需 stock footage、人物出镜、商业游戏资产或背景音乐。旁白文本在 05，拟定英文字幕在 06。

## 录制前锁定同一场景

使用已有 PLAYER → CARGO → GOAL 小原型。必须让观众看懂玩家想完成什么，以及“误抓”为什么碍事。几何体可以简单，对象标签、目标区域和状态必须清楚。

第一条记录包含一次快速擦过和一次慢速接近。旧规则允许快速误抓；第一次修改只允许慢速接近抓取。第二次记录包含慢速抓取、拖带、快速甩动；第二次修改添加释放条件。

这是拍摄用例设计，不是把答案写入 Agent。实际请求由模型生成并验收；不得修改录像中的轨迹来迁就候选。自动浏览器操作可以用于录制，但不能称为真人用户研究。

两次建议输入：

> Pick up the cargo only when I approach slowly. Passing it quickly should leave it where it is.

> Keep the slow pickup, but release the cargo when I move quickly.

不在视频中声称“hold two seconds”“fast flick edge”“离开后才重连”等尚未实际实现的细节。以真正生成并执行的规则为准。

## 分镜

| 时间 | 必须出现的实际画面 | 极短屏幕字 | 录制/剪辑要点 |
|---|---|---|---|
| 00:00–00:07 | 快速擦过导致误抓，目标和货物都可见 | Accidental pickup | 第一镜就是产品，不放片头动画 |
| 00:07–00:14 | 输入第一次修改，显示真实生成过程 | Require a slow approach | 若跳剪或加速模型等待，标注 Generation wait shortened |
| 00:14–00:25 | OLD / NEW 同步重放，指针轨迹对应，货物行为不同 | Same input. Different pickup. | 该段不能用不同轨迹或不同起点拼装 |
| 00:25–00:28 | 停留结果与 CAST 标语 | Same play. Different rules. | 先让观众看懂，再进入解释 |
| 00:28–00:48 | 真实产品背景上叠一张小流程：修改后再重现 vs 复用记录 | Reuse the moment | 不声称所有现有工具都必须 rebuild，不造行业时间统计 |
| 00:48–01:13 | 从起点完整演示一次鼠标操作并结束记录 | PLAYER · CARGO · GOAL / Play recorded | 不是自动乱晃的旧 simulation |
| 01:13–01:48 | 请求 → candidate → OLD/NEW → Try candidate → Keep | Compare before you keep | 候选先比较，Keep 后才成为 accepted；短暂展示可操作性 |
| 01:48–02:21 | 第二次真实输入记录、修改请求、真实 patch、对照、Try | Keep pickup. Change release. | OLD 是第一次保留的版本，不退回初始版本冒充二次修改 |
| 02:21–02:44 | 产品占大半画面，旁边显示真实 input ID、snapshot、ruleset 与 tool trace | Same input / Same start / Different rules | ID 从实际记录读取；没有 hash 校验就不写 hash verified |
| 02:44–03:10 | 简洁架构图，最后切回直接试玩候选 | Agent authors. Runtime compares. Designer decides. | 只说实际工具职责；后端 replay 不冒充模型推理 |
| 03:10–03:30 | 最清楚的一组对照和已选版本短试玩 | Same play. Different rules. | 结束，不加一轮未经验证的新功能 |

## 英文旁白

对应分段内容见 05；字幕在 06。建议按段录音，保留行为发生时的无声窗口。旁白不是按钮教程，不要逐个念按钮。

## 无声音轨方案

没有可用英文配音服务时，可用同一份英文字幕和简短屏幕字完成清晰演示；不要因配音阻塞必交视频，也不要假装已生成音频。

有配音时使用有使用权的自然英文声音，不克隆真人身份，不加夸张广告腔。保留一份无声原始产品录屏及未剪辑的关键链路证据。

## 字幕与等待

06 是按本脚本拟定的 SRT，必须贴合最终音频和剪辑重新对齐。不要对尚未录制的画面声称字幕已经同步。

允许压缩等待、剪去空闲操作；不能删掉失败后使用人工规则的过程，却把结果归给 Agent。对照本体可同速加速，但两边时间比例必须一致。

## 不需要第三个大案例

已有“初次修改 + 二次修改 + 真 trace”是本片核心。额外陌生请求仅在已通过且不挤占主流程时加入；不要为拍 anti-preset 镜头另开功能开发。

## 交付文件目标（这些文件本包尚未制作）

`cast-demo.mp4`：最终 03:30 左右成片。  
`cast-hero.mp4`：前 00:28 独立片段。  
`cast-demo.en.srt`：与成片校准后的字幕。  
`raw-capture/`：真实录屏与音频。  
`evidence/`：实际 input、snapshot、rule versions、model trace 的索引。

最终在无声和有声状态各看一遍；确认同输入差异肉眼可见，文字没遮住抓取/释放，旁白没有替一个尚未出现的行为作证。


---

# 文件：07-界面与截图文案.md

# UI, screenshots and cover copy

下面是目标界面文案。由 Codex 对应到已经实现的状态；不存在的按钮不能只加文案冒充功能。

## Landing / header

**CAST**  
**Same play. Different rules.**

Describe a mechanic change. Compare it against your last recorded play.

Secondary line:

Built with Strands Agents SDK. Designed for small interactive prototypes.

## Play panel

**Try the cargo prototype**

Move the player toward the cargo, then toward the goal. Make a fast pass and a slow approach to test pickup behavior.

Labels: **PLAYER · CARGO · GOAL**

Input status: **Pointer input**  
Recording status: **Recording your inputs…**  
Finished: **Play recorded. Describe what you want to change.**

## Change panel

Heading: **What should behave differently?**

Placeholder: **Describe the behavior you want—not the code.**

Action: **Build candidate**

Working: **Strands is proposing a mechanic change. Your accepted version is unchanged.**

Candidate ready: **Candidate ready. Compare it before you keep it.**

## Comparison panel

Heading: **Your recorded play, under two rulesets**

Left: **OLD — accepted version**  
Right: **NEW — candidate**

Shared label: **Same starting scene. Same recorded inputs.**

Replay action: **Replay comparison**

Optional actual status labels: **Free · Attached · Released**

Captions for observed differences:

- **Fast pass: pickup / no pickup**
- **Fast movement: still attached / released**

只有真实状态机支持且当前结果符合时显示这些状态，不得用台词或计时固定切换它们。

## Decision actions

**Try candidate** — Play the candidate with fresh input before accepting it.

**Keep candidate** — Make this the accepted mechanic.

**Discard candidate** — Keep the accepted mechanic unchanged.

**Undo last accepted change** — Restore the previous accepted rules.

Discard 未接受的候选和 Undo 已接受的修改不是一回事。不要用一个含糊的 Revert 同时表示两者。

## Useful empty and failure states

No recording:

> Play a short interaction first. CAST needs recorded inputs to compare the versions.

No change needed:

> The current rules already match this request. Try a different change.

No visible difference:

> These inputs do not show a difference between the versions. Try an interaction that exercises the changed rule.

Unsupported request:

> This change is outside the current prototype’s supported actions. No rules were changed.

Model failure:

> CAST could not create a candidate. Your accepted mechanic is unchanged. Retry or inspect the details.

Stale candidate:

> The accepted version changed after this candidate was created. Build a fresh candidate before keeping it.

Replay failure:

> Comparison could not finish. No candidate was accepted.

Application request limit:

> This demo’s request limit has been reached. Existing play and replay remain available if supported; new AI changes require the limit to be reset by the operator.

不要将应用自身预算写成 Google/AWS 额度耗尽；按真实响应显示。

## Technical details drawer

**Agent details**

Request · Tool call · Candidate patch · Accepted version · Recorded input · Starting snapshot · Comparison result

Run provenance labels, as applicable:

**Human pointer recording** / **Automated browser pointer recording** / **Synthetic input test**

只显示实际类别，不一律标 Human。

## Thumbnail / cover

Main: **SAME PLAY. DIFFERENT RULES.**

Small: **CAST · Built with Strands Agents SDK**

Visual: actual OLD / NEW split screen with a visible pickup or release difference.

不要放假奖章、GP finalist、数字排名或未经证实的性能数字。

## Screenshot captions and alt text

### Screenshot 1 — Play and request

Caption: **Turn a playtest observation into a mechanic change.**

Alt text: **CAST’s cargo prototype beside a natural-language request to change pickup behavior.**

### Screenshot 2 — Comparison

Caption: **The same recorded inputs, executed under the old and candidate rules.**

Alt text: **Two side-by-side replay panels show different cargo behavior under two rule versions.**

### Screenshot 3 — Revision and evidence

Caption: **Revise the accepted mechanic, then inspect the actual patch.**

Alt text: **CAST displays a second mechanic revision and the corresponding agent tool trace.**

截图必须来自最终运行界面。上面是文案，不代表相应截图已经生成。


---

# 文件：08-评委问答与短Pitch.md

# Judge Q&A and short pitches

这些回答沿用同一产品边界；描述完整流程的部分在最终浏览器验收后使用。

## 15-second pitch

CAST lets a designer change a mechanic and replay the same recorded inputs under both versions. The agent implements the candidate; the designer compares, tries, and chooses. Same play. Different rules.

## 45-second pitch

A designer notices a mechanic problem during play: a fast brush past cargo causes an unwanted pickup. CAST preserves that interaction. The designer asks for slow-only pickup, and a Strands Agent proposes the change. CAST runs the same inputs from the same starting scene under the old and candidate rules, side by side. Then the designer tries the candidate and keeps or revises it. We built a small prototype to make that loop inspectable. It is not a claim that AI knows what is fun—it is a way to put a concrete comparison in the designer’s hands.

## What is the actual user problem?

A rule change needs evaluation against a specific interaction, not just an implementation. CAST keeps the inputs that exposed a problem and uses them to compare a candidate with the accepted behavior. It targets that narrow implementation-and-comparison loop.

## Why an agent rather than a settings panel?

A settings panel is better for a fixed set of known adjustments. CAST targets requests that change how conditions and actions are combined, then revise that behavior in context. The agent authors a constrained patch; the application provides the executable comparison. It does not need a model in the per-frame loop.

## Is this a preset demo?

The prototype and runtime vocabulary are prebuilt. The demonstrated request is sent to a real Strands Agent, and the resulting proposal or patch is executed. The evidence should connect that request to the actual tool output and comparison. A single successful example is not proof of unlimited generalization, which we do not claim.

## Is it just an AI game editor?

CAST’s scope is narrower: evaluating a requested change against the recorded interaction that prompted it. Authoring the rule is one step. The paired replay and the ability to try the candidate are the decision surface.

## Is this a real game?

It is a small playable prototype built for the demonstration, with a player, cargo and goal. It is not a commercial game or an existing engine integration. We use a bounded scene to show the authoring-and-comparison workflow without hiding it behind unrelated assets.

## Does replay show how players will actually behave?

No. It holds the recorded inputs fixed to show what those inputs do under another rule version. A player could react differently after seeing the new behavior. Direct candidate play and later human studies are separate parts of evaluating feel and preference.

## Does the model generate both animations?

No. The model proposes rules. The runtime executes the recorded inputs under each version. Both panels must be generated by execution, not by a prompt-specific animation branch.

## What specifically uses Strands?

The agent’s model-driven authoring loop and custom rule tools. It receives current rules and scene context, proposes a ruleset or patch, and can report that no change is needed. The application performs validation, replay and acceptance. The demonstrated provider is Gemini via Vertex AI.

## Why not AgentCore or Bedrock?

The demonstrated build uses Strands with Gemini through Vertex AI. We are not claiming an AgentCore or Bedrock deployment. The submission describes the architecture we actually ran rather than listing services we did not use.

## What happens when the request cannot be expressed?

The request must fail explicitly or explain the limitation; it must not silently install a template. The accepted mechanic remains unchanged. Schema validation is one boundary, not a guarantee that the proposed mechanic is correct.

## How do you know the comparison is fair?

For each comparison, the two runs must share the starting snapshot and recorded input sequence, with isolated runtime state. The evidence identifies those inputs and the two rulesets. Derived world quantities must be recomputed in each version rather than copied from the old outcome. Repeatability checks establish the supported case, not every possible game.

## What impact have you measured?

We have not established a productivity percentage, player-preference result or production adoption. The demonstrated outcome is a rule revision and a repeatable comparison in the small prototype. The next validation step is to observe designers using it on their own interaction problems.

## What is next?

Validate the workflow with designers, support more recorded situations, and investigate an adapter for an existing prototype environment. Those are next steps, not features claimed in the current submission.


---

# 文件：09-视频发布与社媒.md

# Video and launch copy

发布说明：产品行为文案与最终实际成片一致后使用。未生成视频、未取得公开地址时，不得填假 URL。章节时间按 03:30 脚本，剪辑后重新校准。

## YouTube / Vimeo title

CAST — Same Play, Different Rules | Agents for Humans

## Video description

CAST is a Strands-powered playtest agent for game and interaction designers.

Request a mechanic change, then compare the same recorded inputs under the old and candidate rules. Try the candidate directly before deciding what to keep.

This video demonstrates a small cargo prototype: a slow-approach pickup change, followed by a release-on-fast-movement revision. The comparison footage comes from the runtime, not separately scripted before-and-after animations.

The demonstrated model configuration uses Gemini through Google Cloud Vertex AI. Strands handles rule authoring; CAST’s application handles replay and acceptance.

Fixed-input comparison is not a prediction of how a player would adapt. CAST is a bounded prototype, not a general game engine or a Unity/Unreal integration.

Source: [FILL: PUBLIC_REPO_URL]
Demo: [FILL: PUBLIC_DEMO_URL_OR_DELETE_LINE]
Project: [FILL: DEVPOST_PROJECT_URL]

00:00 Same play, different rules
00:28 Why preserve the interaction?
00:48 Record a play
01:13 Generate and compare a candidate
01:48 Revise the accepted mechanic
02:21 Inspect the evidence
02:44 Architecture and scope
03:10 Keep the input. Change the rule.

#AgentsforHumans #StrandsAgents #GameDevelopment

## Pin / short share caption

Same starting scene. Same recorded inputs. A different rule. CAST makes a mechanic change something you can compare—not just something an agent says it implemented.

## Short social post

Same play. Different rules. CAST uses Strands to revise a game mechanic, then replays the same recorded inputs under OLD and NEW. Compare the result, try the candidate, decide what to keep. #AgentsforHumans

## Longer launch post

We built CAST around one question: what would the same recorded inputs do under a different mechanic?

A Strands Agent proposes the change. CAST runs a paired replay. The designer compares the result and tries the candidate before keeping it.

The demo uses a small cargo prototype, not a commercial game integration. The point is the workflow: preserve the interaction that exposed a problem, then use it to evaluate a change.

Source and demo: [FILL: PUBLIC_PROJECT_URL]

## Operator note

视频应按赛事规则设为公开，不要仅未列出或私有。若旁白为合成音，可在实际使用时添加：“Narration uses a licensed synthetic voice. Product footage shows the running application.” 没用合成音就不加。等待被跳剪时在对应画面标注，而不只在简介里藏一句。


---

# 文件：10-架构说明.md

# CAST architecture

发布条件：将图与最终代码核对；图描述批准的产品结构，不是所有路径已独立验收的证明。`10-architecture.mmd` 是图源，导出 SVG/PNG 后再用于提交。

## One-sentence explanation

Strands authors a candidate rule change; CAST executes a recorded interaction under both versions; the designer decides what to keep.

## Runtime flow

The browser captures pointer events and timestamps while the designer plays. The recording is associated with a starting scene snapshot and the accepted ruleset. The natural-language request and rule/scene context enter the Strands Agent, which calls the bounded rule-authoring tools.

The application validates the returned candidate. Its replay runner starts two isolated executions from the recorded starting state: one uses the original rules and one uses the candidate. The resulting state sequences drive the OLD and NEW panels. The designer can test a candidate with new input, accept it, discard it, or undo an accepted change.

## Responsibilities

**Model:** interpret a requested change and construct a proposal within the supported vocabulary.

**Application:** validate structure and object references, execute supported runtime behavior, replay inputs, and manage acceptance/versioning.

**Human:** judge whether the mechanic is desirable. CAST does not assign a universal “better” score.

## Demonstrated service configuration

The authoring service uses Strands Agents SDK and Gemini through Google Cloud Vertex AI. A development setup can place this service behind a private SSH tunnel. That tunnel is a deployment detail, not the product’s differentiator, and not a public judging link.

The actual tools named in the supplied implementation are `propose_rules`, `propose_rule_patch`, and `keep_current_rules`. Do not add a claimed `run_replay` model tool unless it is genuinely registered and called in the final build. The application may orchestrate replay after a proposal without the model invoking replay directly.

## One important comparison boundary

The fixed input is the user’s control stream and its timing, not the old world’s outcome. Cargo distance, attachment state, collisions and other rule-dependent values must be derived within each replay branch. Holding an old result fixed would corrupt the meaning of the comparison.

If a replay uses a synthetic or automated pointer recording, identify it accurately. That still permits an integration demonstration; it is not a human study.


---

# 文件：11-事实边界与发布检查.md

# 事实边界与发布检查

## 当前证据口径

本包没有连接用户的 Mac/VPS，没有执行最新应用，没有生成视频或音频。以本对话最后开发者报告为最新状态；旧 ZIP 只用于核对已知包结构、依赖和许可证。

### 来源层级

**P1｜用户最后转述的开发者状态。** 明确报告：PLAYER → CARGO → GOAL 场景；真实 Strands 第一轮 `distance + slow speed → attach`；第二轮 `speed > threshold → detach`；replay 的未接近、慢速接近跟随、快速释放行为符合预期；浏览器完整操作和录屏仍待整合。它是开发者报告，不是本包独立运行结果。

**P2｜当前对话上传的开发日志。** `粘贴的文本 (1).txt`，版本特征：包含从 Camera 转向 pointer/replay，末尾浏览器验收遇到 429 暂停。转向部分记录 pointer、snapshot、replay、attach/detach 的加入，以及实际服务返回值与本地测试不一致的问题。来源文件中转向实现集中在第 2583–3102 行，实际服务疑点在第 3104–3148 行。最后浏览器验收被 429 中断。历史失败不能自动当作仍存在；历史通过也不能当作最终 UI 通过。

**P3｜旧归档 `CAST.zip`。** 本次直接读取其中 `CAST/pyproject.toml`、`CAST/cast/providers.py`、`CAST/README.md`、`CAST/docs/VERTEX.md` 与 `CAST/LICENSE`。可支持当时 Strands/Gemini/Vertex、FastAPI/Pydantic、依赖组、启动入口。它仍是 Camera 版本，不能证明新 replay UI 的完成度。

**P4｜已约定的产品目标。** 用户明确采用：同初始状态、同输入记录、新旧规则对照；Try/Keep/Revert；真实 Strands 两轮；停掉 Camera 主线。Goal 是设计目标，不是完成证据。

### 文案中的实现状态

| 声明 | 当前可依据什么 | 发布要求 |
|---|---|---|
| 使用 Strands + Gemini/Vertex | P1、P2、P3 | 核对最终运行配置；不添加 Bedrock/AgentCore |
| 首轮 attach 与第二轮 detach 由模型生成 | P1 开发者报告 | 保留对应 raw tool trace；不要只留口头总结 |
| attach/follow/detach runtime 得到预期结果 | P1 报告，P2 有代码/测试过程 | 最终 release 上复跑；区别单元测试与真实 UI |
| 真实 pointer 记录与 OLD/NEW 页面 | P2 记录实现中 | 完整浏览器录像与实际输入/快照/结果对应后启用发布稿 |
| Try candidate、Keep、Discard、Undo | P4 目标与局部旧能力 | 逐项测试当前 UI；不存在的动作删去 |
| 同初始状态、同输入、独立分支 | P4 为验收标准 | 检查实际数据；不能仅凭相同文字标签认定 |
| 确定性、可复现 | replay 的设计目的 | 相同运行重复一致后，只对已测试范围使用该词 |
| 保存时间、提高效率、用户喜好 | 尚无比较研究 | 不写百分比、客户数或偏好结论 |
| 商业游戏/Unity/Unreal 集成 | 没有证据，非当前目标 | 不宣称支持；只作后续计划 |
| 公开仓库、可访问演示、成片 | 本包未取得最终链接 | 用真实 URL 补齐并匿名访问检查 |

## 发布闸门：不扩功能，只确认已承诺的链路

- [ ] 从正常入口进入实际应用，能看懂 PLAYER、CARGO、GOAL 和下一步。
- [ ] 记录来自 pointer 操作；如为浏览器自动化，说明是 automated demonstration，不称 human study。
- [ ] 第一轮请求真实进入 Strands；原始工具记录对应安装/候选内容。
- [ ] OLD 与 NEW 的输入序列和起始 snapshot 确实相同，运行状态互不串扰。
- [ ] 输入记录保留相对时间；runtime 使用记录时间而非回放时墙钟计算必要的速度/计时。
- [ ] distance、附着关系、货物位置等依赖世界状态的量在各分支重算，不把旧世界结果当共同输入。
- [ ] 对照在最终运行服务里得到可见差异，不只在本地测试得到数值。
- [ ] Try candidate 真的允许新输入；Keep 才接受版本；Discard 不改已接受版本。
- [ ] 第二轮以第一次接受版本为起点；真实 patch 保留未请求修改的行为。
- [ ] 重复请求、模型错误和没有可见差异能诚实处理，不偷偷换人工答案。
- [ ] 至少一个能力范围内、未为其专门写答案的请求由真实 Agent 处理；不能只靠反复调过的同一句例子宣称泛化。
- [ ] 最终视频的旁白、字幕、屏幕结果、tool call、版本号一一对应。
- [ ] 任何剪短的模型等待在画面明确标注；不能剪出假的零延迟。

## 当前状态诚实说明（未通过上述闸门时使用）

> CAST is a Strands-powered playtest prototype. Development runs have exercised agent-generated pickup and release rules and their runtime behavior. The complete browser workflow for recording, side-by-side comparison, candidate trial and acceptance is still undergoing end-to-end validation. The current evidence should not be read as a finished public demo or a production game integration.

这段不能替代赛事对可运行作品的要求。未完成时应如实判断能交付什么，不能靠删掉状态段制造完成。

## 统一修正的说法

**不用：** “It shows what your last play would have felt like.”  
**用：** “It shows what the same recorded inputs do under a different rule.”

**不用：** “The agent determines the better mechanic.”  
**用：** “The agent proposes the change; the designer decides what to keep.”

**不用：** “Real game integration” 或 “works with any game.”  
**用：** “A small playable prototype demonstrating the workflow.”

**不用：** “A/B user study,” “proven productivity improvement,” “first ever,” “GP favorite.”  
**用：** “Paired replay,” “bounded prototype,” “demonstrated behavior.”

**不用：** “Fully built on AWS” / “powered by Bedrock / AgentCore”——除非最终实际如此。  
**用：** “Built with Strands Agents SDK; the demonstrated model configuration uses Gemini via Vertex AI.”

## 官方硬要求核对

以下是官方页面的简要核对，不代替原规则或身份审核。来源 R1、R2。

截止：**2026-09-15 08:00（UTC+8）**，即 2026-09-14 17:00 PDT。公开源码需带 README、完整 MIT/Apache 许可和架构图；提交须含工作演示，视频最多五分钟，在 YouTube/Vimeo 公开。还需 AWS Builder ID；材料需英文或英文翻译。评委必须有可运行、免费访问的测试途径；公开 live demo 本身为可选加分因素。

资格：规则列出不开放新加坡居民。当前位置或时区不等于居住资格，不能替本人确认。

可选 Builder Center 文章须公开并用 `#AgentsforHumans`；按规则每篇可能加 0.2，最多 0.6。是否合格由主办方决定，Strands + Vertex 的真实配置不能为加分改写成 AWS 托管部署。先保必交项目和视频，再处理博客。

提交后无确认回执不算完成；不要假设截止后仍能补改参赛材料。

## 本次发现的许可证问题

旧 `CAST.zip` 中 `LICENSE` 以简短 “AS IS” 句子结束，缺少标准 MIT 文本的完整免责段。17 提供完整常见 MIT 模板，版权行沿用归档的 `CAST contributors`。由权利人核实后使用；保留第三方声明。不要把本包模板的存在当作最终公开仓库已经有合格许可证。标准参考 R5。

## 发布前应填的信息

统一见 16。最重要的是可访问仓库、公开视频、实际 release、评委运行途径、AWS Builder ID、公开署名。其余为可选链接和真实证据标识。

含 `[FILL: ...]` 或 `[VERIFY: ...]` 的文件不得直接公开；README 的 `YOUR_PROJECT_ID` 是面向读者的运行参数示例，可以保留，但作者个人 project ID、密钥和账号不应混入公共文案。

## 来源（供内部核对，不必贴进 Devpost 故事）

R1 — Agents for Humans Official Rules，§1、§3、§4、§5、§6：  
`https://agentsforhumans.devpost.com/rules`

R2 — 官方赛道与交付概览，Professional Agents / What to Submit：  
`https://agentsforhumans.devpost.com/`

R3 — Strands 官方 Google/Gemini provider 及 API：  
`https://strandsagents.com/docs/user-guide/concepts/model-providers/google/`  
`https://strandsagents.com/docs/api/python/strands.models.gemini/`

R4 — Google Cloud ADC：  
`https://docs.cloud.google.com/docs/authentication/application-default-credentials`

R5 — SPDX 标准 MIT 文本：  
`https://spdx.org/licenses/MIT.html`

官方网页核对日期：2026-09-15。FAQ/resources 和登录后具体提交表单未成功读取，本包没有编造其字段、限制或额外规则。标题/短介绍/故事等是可映射的素材，不声称表单完整复刻。


---

# 文件：12-Builder博客1-EN.md

# From rule generation to a design decision: building CAST with Strands Agents

编辑说明：可选 Builder Center 博文草稿。正文明确区分开发结果与仍在收口的界面；最终状态变化后按实际改一处，不补虚构性能数字。公开文章中的 AWS 技术使用只写 Strands，不冒充 Bedrock/AgentCore 部署。是否计入奖励由主办方判定。

---

A generated rule is an implementation proposal, not a design decision.

That distinction became the central lesson of building CAST for Agents for Humans. We started with natural-language control changes: describe a relationship, let an agent write rules, and run them. But a person still needed a way to answer a more important question: did this change improve the interaction that made me ask for it?

CAST’s revised focus is paired playtest replay. Preserve an interaction, propose a mechanic change, and execute the same recorded inputs under both versions. The designer can compare the result before trying and accepting a candidate.

## Giving Strands a bounded job

We use Strands Agents SDK for the authoring loop. The agent receives a natural-language request, the current rules and a registry of scene objects. It is not asked to produce arbitrary JavaScript or rewrite a project directory.

Its tools have narrower responsibilities. One proposes a ruleset. Another proposes add, replace or remove operations against the current rules. A third reports that the installed behavior already satisfies the request.

That last outcome matters. During development, repeating a request could look like a failure simply because the agent did not produce a new proposal. Treating “no change needed” as an explicit outcome made the application’s responsibility clearer.

## A valid structure is only the first check

Pydantic checks the rule structure. That does not establish that a mechanic behaves correctly.

Attachment made the difference concrete. Setting the cargo’s coordinate equal to the player’s coordinate is not a complete pickup mechanic. The runtime must preserve an offset across frames and release without resetting the object. A model can choose a valid action name while the implementation underneath still has a state bug.

We therefore separate three questions: did the agent produce a proposal, did the runtime execute it, and did the product make the result usable?

## Keeping the human decision

The agent authors the change. The application runs the comparison. The designer judges the result. This is intentionally not an agent that announces which game is more fun.

A first rule request can require a slow approach before attachment. A later request can preserve that pickup condition and add release during fast movement. Development runs have exercised model-generated changes and runtime behavior; the complete browser comparison and acceptance path must be validated separately before being described as finished.

## The configuration we actually used

Our model configuration uses Gemini through Google Cloud Vertex AI with the Strands Gemini provider. We are not claiming an Amazon Bedrock AgentCore deployment. The browser and Python application manage play, rule validation and replay around the Strands authoring loop.

The useful division is not “AI everywhere.” It is a model where interpretation is needed, ordinary execution where repeatability is needed, and a human where preference and intent matter.

CAST is still a small prototype. Its contribution is the shape of the workflow: do not stop at a plausible patch. Put the consequence of that patch next to the original interaction, where the designer can inspect it.

#AgentsforHumans


---

# 文件：13-Builder博客2-EN.md

# Same inputs are not the same outcome: designing CAST’s paired replay

编辑说明：可选 Builder Center 博文草稿，技术设计文章；以下“不变量”是需要验证的设计要求，不是已测全覆盖的宣称。

---

“Replay the same play under a different rule” sounds simple until you ask what must remain the same.

For CAST, the answer is the starting scene and the recorded control inputs. It is not the old object positions, attachment states or collision results. Those are consequences of the rule and must be allowed to differ.

That distinction matters because CAST combines a Strands rule-authoring agent with a small interactive prototype. A designer requests a mechanic change; the application compares the accepted and candidate rules against a recorded interaction.

## Freeze the cause, recompute the consequence

Suppose a fast pass near cargo picks it up under the old rules. The designer asks for slow-only pickup.

Replaying the same pointer events can show the cargo moving in one version and remaining still in the other. But if the recording also forces the old cargo-to-player distance into the new branch, later conditions may use a world that no longer exists.

The design requirement is to preserve the external control stream and derive world-dependent quantities inside each branch. The two runs need isolated state, including attachment offsets, flags and timers. Shared mutable state would make one candidate affect the other.

## Time is part of the input

A sequence of positions without timing cannot distinguish a slow approach from a fast pass. A comparison involving speed must preserve relative event times and use a consistent definition of speed.

Likewise, rendering speed should not change the simulated rule outcome. A paused browser tab or a sped-up video should not secretly turn a slow pickup into a fast one. These are replay correctness requirements to test, not benefits that come automatically from having an endpoint named replay.

## The role of Strands

Strands handles the mechanic-authoring step. It receives current rules and scene context, then proposes a constrained change through custom tools. The application takes that candidate into the replay runner.

This separation is useful: the model can interpret an instruction such as changing pickup or release behavior without being responsible for producing frame-by-frame results. The comparison comes from the runtime, not an explanation written by the model.

The model configuration used during development is Gemini via Vertex AI. We describe that configuration directly rather than claiming an AWS deployment that we have not performed.

## What the comparison does not prove

Fixed-input replay is a controlled comparison of a recorded action sequence. It is not a prediction of how a player would react to the changed mechanic.

Once the world behaves differently, a player might move differently too. That is why trying the candidate with fresh input remains a separate step. A useful replay can expose an accidental pickup or an unexpected release; it cannot establish that a game is more fun.

We also need to allow honest no-difference results. A recorded interaction may never reach the changed condition. The correct response is to capture a relevant interaction, not manufacture a more dramatic side-by-side video.

CAST’s goal is to make a design hypothesis inspectable. Same starting scene. Same inputs. Different rules. Then let the designer decide what to try next.

#AgentsforHumans


---

# 文件：14-Builder博客3-EN.md

# Why CAST moved from camera props to a recorded playtest

编辑说明：可选 Builder Center 博文草稿，基于开发日志的转向过程；不将 prototype 的参与者称为客户或用户研究样本。

---

Our first version of CAST tried to turn physical props into live controls. A camera tracked colored objects; a Strands Agent translated a new interpretation into rules; a digital scene responded.

The prototype could produce model proposals and runtime changes, but the experience exposed a problem that component tests did not capture. The person using it could not reliably tell what their movement controlled or why the result mattered.

## The input was consuming the product

Colored-object tracking jumped between regions, lost markers and needed repeated adjustment. We tried smoothing and short loss-recovery windows. Those were legitimate engineering changes, but they did not answer the product question: what worthwhile task was the user actually completing?

A triangle moving near a circle could demonstrate a rule. It did not, by itself, demonstrate a useful creative workflow.

The growing number of green tests was not a substitute for a person understanding the page.

## Keeping the useful work

We did not discard the whole project. The useful parts were the Strands authoring loop, constrained rules, candidate handling, versioning, runtime state and undo.

We changed the input and the task. Pointer-controlled play made the action explicit. A small player-cargo-goal prototype made the interaction legible. Recording that action created a new result the application could provide: a comparison of the same inputs under two mechanic versions.

The new question was no longer “Can AI change what this prop means?” It was “What does this proposed rule change do to the interaction I just recorded?”

## What the agent owns

The Strands Agent reads the request and current rule context, then proposes a candidate or patch through tools. In development, the model configuration uses Gemini through Google Cloud Vertex AI.

The model does not own the designer’s preference. It also does not generate the two comparison animations. The runtime executes the recorded inputs. The designer tries and selects the candidate.

This gave us a cleaner division of responsibility and a more meaningful reason to preserve the interaction instead of merely changing a parameter.

## What changed in our definition of done

A health response means the process answered. A unit test means a specific assertion passed. A generated patch means the authoring step produced data. None proves the whole browser experience works.

We started treating the recorded play, generated candidate, paired replay and acceptance flow as separate evidence requirements. Development runs have exercised the new attachment and release behavior; the final browser workflow still needs its own uninterrupted acceptance evidence.

The lesson is not that camera interaction is bad or that simple graphics are automatically enough. It is that an input method and a technical capability need a coherent task around them.

CAST now focuses on a narrow designer decision. Preserve the input that exposed the problem. Ask for a change. Compare what actually happens. Then try the candidate yourself.

#AgentsforHumans


---

# 文件：15-给Codex的执行指令.md

# 将文案包落地到最终项目与提交

这不是新的产品转向。沿用现有 CAST same-input OLD/NEW 目标，不再重写长 Goal。

1. 将本包当作提交文字和视频录制素材库；不要整包覆盖应用源码或旧 records。先读取 11 的事实边界。
2. 完成真实浏览器中“记录 → 真 Strands candidate → OLD/NEW → Try → Keep → 第二轮 patch → 再比较”的验收。只报告实际结果，不用 endpoint 在线或测试计数替代。
3. 对最终行为与文字逐项核对。不存在的功能删掉相关句子；不要为了保住旁白临时造一个假路径。任何提示词示例映射、人工 fallback 或录制自动化来源都如实标注。
4. 把 01 填入 Devpost 草稿；02 映射到实际表单字段；03 安全合入 README。不要声称已提交，除非真的完成平台提交并取得确认。
5. 从实际环境获取 PUBLIC_REPO_URL、release commit、模型配置、视频地址、证据路径。不要虚构 input ID/hash、延迟、成功率、用户人数、收入、AWS 服务或基准结果。
6. 从 10 的 Mermaid 图源导出图片，对照最终代码核验。Agent tools 与应用 replay 的职责不得混画。
7. 按 04 在运行产品中录制真实 pointer 操作和两轮模型流程。05 用于配音，06 是拟定字幕，必须和真实音频/剪辑对齐。可自行使用有权限的配音与剪辑工具；无法生成音频时用英文字幕版本，不让用户另找素材。
8. 应用必须允许逐帧检查每个比较：同外部输入、同起始快照、独立状态、正确计时。distance、cargo 位置、attached 等受规则影响的值应在各分支重算。不是把旧版计算好的世界状态作为新版的“输入”照抄。
9. 按 07 截取真实界面并填图注；按 09 发布已完成视频。公开发布前确认账号权限和可见性；需要用户授权的动作再请求，不索要密钥。
10. 必交项已准备好后，再考虑 12–14 的可选博客。正文明确实际 Strands/Vertex 配置，不伪称 Bedrock/AgentCore。博文是否计分不保证。
11. 检查仓库完整 MIT 许可、第三方 notices、AI/旧工作披露、secret scan、无登录访问、能运行的测试构建。17 是完整 MIT 模板，不擅自改作者版权归属或移除第三方版权。
12. 最后输出实际产物位置和仍未解决事项。不要再让用户摆物体、点按钮、重输提示词、抄 API 错误。

给用户最多收集一次真正无法自动获得的信息：公开署名、AWS Builder ID、账号授权及权利/资格事实。产品操作、截图、录屏、字幕、文案和普通调试由你完成。

如果应用或录像尚未通过，不要写“核心比赛项目已做完”。即使文案齐全，未运行或不符合描述的产品也不能被文字补成完成。


---

# 文件：18-项目与素材声明.md

# Project and asset disclosure

该文件需按真实情况补齐；不是对作者权利、参赛资格或开发日期的代替声明。

## Public English disclosure

### Development assistance

AI coding assistants were used during implementation and debugging. AI assistance was also used to prepare submission text. The submitted runtime behavior and the recorded demonstration must match the actual release.

### Pre-existing work

Pre-existing custom code or project work incorporated into this submission:

[FILL: actual description and boundaries; use “None beyond standard development dependencies” only after verification.]

Work built during the hackathon period:

[FILL: factual scope and dates supported by the project history. Do not claim earlier work was newly created.]

### Libraries and model services

The implementation uses Strands Agents SDK, Python, FastAPI, Pydantic, JavaScript/HTML Canvas and a Gemini model through Google Cloud Vertex AI in the demonstrated configuration. Dependencies retain their own licenses. List any additional retained component in the repository notices.

### Visual and audio assets

[FILL: actual ownership/license statement for geometry, fonts, screenshots, diagrams and narration.]

Optional, only if true:

> The prototype uses original simple geometric visuals. Product screenshots and recordings show the application. Narration uses a licensed synthetic voice; no identifiable person's voice was cloned.

### Demonstration provenance

[FILL: “The demonstration uses automated browser pointer input recorded by the application,” or an accurate human-operated description.]

Model waiting periods edited for length are marked on screen. OLD and NEW behavior is generated by the runtime using matched inputs and starting snapshots. Developer-authored fixtures are labeled separately and are not presented as model-generated changes.

### Scope

CAST is a prototype demonstrating a bounded authoring-and-comparison workflow. It is not an existing commercial game integration, a prediction of player behavior, a study of player preference, or evidence of measured productivity gains.

## Private submission fields

AWS Builder ID、真实身份、居住资格、组织信息和平台要求的声明应按本人真实情况填写。不要把这些信息写进公开代码或演示截图。需要的账号授权由账号本人完成；不把 access key 当 Builder ID。
