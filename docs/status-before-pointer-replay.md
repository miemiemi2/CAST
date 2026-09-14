# CAST 当前状态

## 当前目标与用户决定

争取 GP，竞争力主要依靠项目本身。优先做强真实道具与多轮自然语言关系创作；不以录屏替代产品，也不要求通用商业产品的全部能力。视觉使用成熟开源组件；基础测试自动完成，不反复要求用户配合。

## 已核验

- Strands 1.55.1 + 官方 GeminiModel + Vertex Gemini 2.5 Flash 已实际调用成功；Bedrock 保留为可选 provider。
- 两轮中文请求得到旋转倍率 1 → 0.5 的模型工具提案。用 +120°、−60° 两组**合成信号**分别验证 Python 与浏览器模块输出一致。原始模型记录：`records/vertex-proof-20260914T174411.json`；行为核验：`records/vertex-proof-behavior.json`。
- Mac `/api/intent` 已通过 SSH 模型网关成功返回 −0.75 倍率提案，返回基础版本号 6；生成期间已安装规则/版本未变。原始记录：`records/vertex-api-probe-20260915T014746.json`。
- 额外真实修改测试通过：主舞台位置规则保持完全一致，月亮旋转倍率修改为 0.5。记录：`records/vertex-preserve-unrelated.json`；完整网关消息副本：`records/vertex-gateway-journal-20260914T1750.json`。
- Vertex 认证留在 VPS 原位置，没有复制到 Mac 或项目。Mac 经回环 SSH 隧道传递意图、规则和场景数据；不传视频。
- Python 26 项测试通过（含远程服务失败、并发编辑后的旧提案拒绝安装、规则 patch CAS）；另有 `records/vertical-probe.json` 覆盖对象注册到导出的纵向流程；这些仍不代表完整产品验收。
- 用户已确认 Mac 摄像头授权并启动。先前日志含颜色检测得到的位置/旋转/距离数值；仅凭这些值不能确认身份准确、无误识别或遮挡恢复。
- OpenCV 在 Mac 可导入；浏览器现可按低频率调用本地 `/api/native-track`，使用可配置 marker ID 的 ArUco 结果并在失败时回退颜色检测。仍缺真实标记身份与遮挡恢复的完整现场证据。

## 当前运行入口

- Mac：`/Users/mixu/Desktop/CAST`，`http://127.0.0.1:8765`。
- VPS 模型网关：`127.0.0.1:8877`，Mac 通过 `127.0.0.1:18765` 访问；详细启动说明见 `docs/VERTEX.md`。
- 模型预算账本：VPS `~/.local/share/cast/model-journal.json`。每日默认 10 次模型请求，单次意图最多 3 次；服务失败可人工创作。预算耗尽不等于模型能力不可用。
- 本轮同步只复制代码文件；Mac records 未覆盖。同步前备份：Mac `before-vertex-20260915T014651.tar.gz`。

## 关键未完成

已新增通用 `conditions` AND/OR 组合与 `mask` 输出：agent 可把旋转/开合与距离等输入组合，再映射到目标的可见遮罩变化；这支持“咬掉一角”等解释，但底层没有语义动作枚举。该行为已有自动化 Python 与浏览器路径基础验证（Python 28 项、Node 7 项），尚未进行最终现场验收。

1. 用户可用的现场预览/确认和连续多轮创作体验；提案生成后现已用当前相机信号执行本地 preview，并在安装前展示解释、diff 与结果，agent 会携带最近意图上下文并可调用结构化 add/replace/remove patch 工具，仍需一次完整现场确认。当前自动探针仅覆盖人工规则及合成输入，不能代替真实 agent + 相机完整流程。
2. 将开源 tracker 接入实际浏览器/本地运行路径、稳定身份映射；用户已经授权复用开源组件，无需重新讨论选型或重复测试颜色 fallback。
3. 运行时当前仍有两套实现；事件、持续时间、持久效果存在声明但行为不完整。模型提示已明确不使用尚未实现字段；仍需实现并做行为核验。
4. 通用多对象绑定、距离/方向组合、对象注册表约束、可带走作品；`target_object` 目前只是目标名称扩展，不能声称完整身份系统。
5. 无效来源的半次安装和审计分页已修复；状态存储失败原子性、遮挡日志输入完整性仍需修正。历史 rsync 曾复制 records，历史日志完整性不能假定。
6. 最终产品整合、文档、开源归属与参赛交付；演示呈现排在可用产品之后。

旧状态及其中过强的阶段性判断保存在 [历史快照](docs/status-before-vertex.md)，不作为当前完成证明。

- 可复现脚本：scripts/start-vps-gateway.sh 启动 localhost Vertex 网关，scripts/start-mac.sh 启动 Mac CAST；两者不写入凭据。
