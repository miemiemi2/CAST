# CAST current engineering state

## 当前决定

CAST 当前继续推进完整产品目标；目录中的早期限制仍是待完成事项，不代表目标已完成。

## 本轮已完成

- Rule DSL 增加声明式 `when`、`event`、`duration_ms`、`amount` 和 `persist` 字段，仍由 Pydantic 严格校验，禁止执行代码。
- Python 引擎支持阈值条件、效果幅度、边界裁剪与跨帧 flags 持久化；`/api/signal` 保存最后信号和结果。
- 增加 `/api/preview`：在安装前用候选规则和真实/指定信号求值，并写入审计事件，不修改已安装版本。
- 浏览器运行时每 250ms 将相同摄像头信号送入服务端求值，保持前后端语义可比；摄像头帧仍不上传。
- 增加 `SceneObject` 注册表和 `/api/scene` 原子更新接口，支持 prop、character、light、anchor 多对象持久化及版本冲突检测。
- 增加 `/api/scene/replace` 对象替换接口；替换保留对象 ID、返回旧值并写入审计事件，支持识别结果变化时的原子同步。
- 增加独立场景 Undo 栈和 `/api/scene/rollback`，对象替换与整场景更新均可恢复并产生版本化审计记录。
- 增加有界 `/api/events` 游标接口，可按事件类型读取原始执行记录，用于复现和验收。
- Python 引擎现在实际应用 `target=moon` 的 position/rotation/scale/state/light 效果，并保留旧的扁平 flags 兼容字段。
- 浏览器 `applyRules` 已同步支持相同的阈值模式、效果幅度和 moon 目标；新增差分行为回归覆盖。
- 新增场景回滚和审计读取回归覆盖；Python 测试现为 16 项全部通过，Node 运行时测试 6 项全部通过。
- 已将当前版本同步至 Mac `/Users/mixu/Desktop/CAST`；在 Mac 新建虚拟环境并成功安装依赖，启动 Uvicorn 后 `/api/health` 返回 `ok:true`。Mac 已枚举 FaceTime 与 iPhone Continuity 摄像头；浏览器 TCC/真实道具追踪仍待现场验证。
- Mac 端已实测加载包含 Manual authoring 入口的页面，并通过 `/api/scene` 成功注册 `hero` 对象（返回 version 1）；首次测试中的 422 来自请求字段不完整，补齐默认字段后通过。
- Mac 的 FFmpeg AVFoundation 已列出 FaceTime、iPhone Continuity、桌上视角和屏幕采集设备；本轮尚未取得单帧像素，TCC 采集权限仍需在图形会话中验证。
- 已取得 Mac 浏览器真实运行证据：`/api/events?type=signal.applied` 返回连续事件，主标记 `visible:true` 且 x/y/rotation 随画面变化；当前 `distance:0` 说明蓝色辅助标记尚未进入视野，待补第二物体验证。
- 后续 Mac 记录已验证蓝色辅助标记进入视野：连续 `signal.applied` 事件中的 distance 从 0 变为约 0.45，并随物体移动变化，主标记保持 visible=true。
- 前端新增摄像头选择器，可在不移动屏幕的情况下选择桌上视角或 iPhone Continuity；已同步到 Mac 并确认页面包含 `camera-device` 控件。
- 增加可选 `.[cv]` 依赖组和 `cast.tracker` OpenCV ArUco 适配器；基础安装仍使用本地颜色 fallback，视频不上传模型。tracker 后端选择与无 OpenCV 安全 fallback 已有测试覆盖。
- 按比赛竞争力取舍，优先强化核心差异：规则新增 `target_object`，Python 与浏览器引擎都能对场景注册表中的自定义对象应用关系效果；新增自定义目标回归测试。视觉通用性保持为可替换基础设施，不作为主要创新承诺。
- 新增 `/api/explain`，对候选规则生成可读语义说明；Agent 提案界面在安装前展示解释，帮助创作者核对关系含义。
- 新增 `scripts/demo_probe.py` 和 `records/demo-probe.json`，自动跑通预览→解释→人工安装→信号求值→回滚的完整核心差异链路；Python 测试仍为 19 项全部通过。

Goal remains the full GP project described in ../CAST-工程Goal启动说明.md. This is an early incomplete scaffold, not a demonstrated product.

## Verified this turn

- Local editable install succeeds; 8 Python tests and 5 Node pixel/runtime tests pass (`.venv/bin/python -m pytest -q`).
- Store atomically replaces persisted JSON. Undo restores earlier rules, preserves unrelated state and increments revisions monotonically. Corrupt state fails visibly.
- Rule schema forbids extra fields and unregistered sources/targets.
- Removed deterministic keyword parser and fixed-answer Strands tool. Real Strands tool now accepts model-generated rules and validates them. Disabled or failed provider cannot return a pretend generation.
- Persistent UTC daily limit: at most 10 model requests/day; at most 3 per intent, 1024 output tokens/request, 30 KB bounded model input including conservative tool allowance. Retries disabled. One real Strands ConverseStream request was attempted and rejected by AWS account allowlisting before model output; no successful inference or measured fee claim.
- Mac SSH works; Python and ffmpeg are present. AVFoundation lists FaceTime and Continuity cameras. Pixel capture/GUI permission not yet verified.
- AWS identity API and us-east-1 Bedrock model listing work. Free tier API confirms ACTIVE FREE plan and USD 100 remaining credits. Model invocation is blocked by customer verification / Bedrock allowlisting (see records/real-agent-probe.json). User was asked to complete account verification; do not retry before access changes.

## Remaining, in dependency order

1. Camera tracking experiment on Mac: real pixel-derived positions/rotation/distance for one prop and auxiliary object, occlusion/recovery evidence. Browser now derives signals from red/green/blue pixel components and displays camera preview. Five synthetic pixel/runtime tests pass; no physical-marker camera evidence yet. Pointer demo was removed.
2. Replace provisional rule DSL with composable bindings, event conditions and persistent effects supporting arbitrary roles with safe visual primitives. Current schema supports only stage/moon and is insufficient for the full promise.
3. Local browser applies rules before drawing and journals a throttled signal to `/api/signal`; runtime/backend parity still needs differential tests for the richer DSL and scene state persistence. Occlusion freezes main scene; auxiliary distance effects are suppressed on tracking loss.
4. Free plan verified. Resolve account allowlisting externally, then use real Strands after configured limits, capture generated rules/receipts and actual changed motion semantics. Make validated installation an agent tool with version checks.
5. Secure local web mutation boundaries, finish preview/safe switching, visibility freeze/recovery, atomic installation and concurrency tests.
6. Complete reproducible packaging (static assets currently depend on cwd), pinned dependencies, full license, startup on Mac, meaningful browser and integration tests.
7. Perform unguided use, modified relation, undo, occlusion, object swap; record human continued improvisation. Cannot be substituted by simulated pointer inputs or self-evaluation.
8. Publish sanitized GitHub engineering repo, README/architecture/event/test/cost evidence and <=5 min English/subtitled no-face demo video; deliver to Mac desktop and verify.

## Files

Code under cast/, tests under tests/, provisional UI under static/. Desktop Chromium screenshot visually inspected (camera-off state); stored at /tmp/snap-private-tmp/snap.chromium/tmp/cast-stage.png. README still needs full rewrite against completed behavior.
