---
title: AI-NPC 沙盒方案 — 固定地图自由探索/交互 + 会写日记 + 会学习
subtitle: 小世界模型 + 生成式智能体（Generative Agents）的可落地技术方案
date: 2026-06-29
status: draft（方案；代码落 models/experiments/npc_agent/）
basis: Park et al. 2023《Generative Agents》(记忆/反思/日记) + DreamerV3 (可选学习型世界模型)
---

# AI-NPC 沙盒：固定地图 · 自由探索/交互 · 写日记 · 学习

> **一句话**：固定小地图里，LLM 驱动的 NPC 在引擎里自由行动+交互，靠**记忆流+反思**形成"日记"与"学习"。**训练侧极便宜**（自有引擎=免费且自带动作标注的数据、零隐私/IP/具身约束）；**成本大头是 LLM 推理**。

## 0. 目标与成功判据
做一个 NPC，能：① 在固定地图**自由探索**（覆盖、寻路、避障）；② 与物体/其他 NPC**交互**（拾取/使用/对话）；③ **写日记**（每日第一人称总结）；④ **学习**（反思把近期记忆综合成高层洞察，**行为据此可量化地改变**）。
**成功 = M2 退出**：单 NPC 跑通①–④，且"反思 on vs off"的行为差异可测（见 §9）。

## 1. 范围 / 不做什么
**In**：固定地图（先 64×64 tile）；符号状态；LLM 心智；记忆/反思/日记；1→~25 NPC。
**Out（先不做）**：开放世界/程序生成地图；像素生成世界模型（要可视化再加，§3 可选）；真机/具身迁移；多人实时网络同步。

## 2. 架构（两组件，成本结构不同）
```
┌─────────────────────────── 引擎（你拥有）= 真·模拟器 ───────────────────────────┐
│  固定地图(tile grid) + 实体/物体 + 物理/碰撞 + 寻路                              │
│  ▲ 观测(symbolic state)          │ 动作(action vocab)                          │
└──┼───────────────────────────────┼──────────────────────────────────────────┘
   │                               │
   │   ┌─────────────── NPC 心智（生成式智能体，主要是推理）──────────────┐
   └──▶│ 感知 → 记忆流(memory stream, 向量库) → 检索 → 规划 → 动作          │
       │                              │                                       │
       │                    反思(reflection)=「学习」   每日总结=「写日记」    │
       │                    (近期记忆→高层洞察→回写记忆) (top 记忆→日记条目)   │
       └──────────────────────────────────────────────────────────────────────┘
   (可选 Phase 4) 学习型世界模型(Dreamer 式, ~1–20M) ← 引擎日志，用于想象/规划
```
**关键**：LLM 负责认知/记忆/日记/反思；**引擎+寻路/小策略负责"身体"**。PoC **不训世界模型**——引擎本身就是世界模型。

## 3. 环境 / 世界模型
### 3.1 符号状态（不用像素 → 模型/成本缩一个量级）
```python
TileMap   = grid[H][W] of {terrain, walkable, object_id?}        # 先 64×64
Entity    = {id, kind, pos(x,y), state}                          # NPC/物体/可交互物
AgentObs  = {pos, facing, inventory[], nearby:[Entity within R], # NPC 的局部观测
             time, last_action_result}
```
### 3.2 动作空间（离散，引擎可执行、自带标注）
`move(dir)` · `goto(target)`(寻路) · `interact(entity, verb)` · `pickup/drop(item)` · `say(text)` · `wait`。
→ **引擎在生成每一步时天然知道动作** ⇒ **数据自带 (obs, action) 标注，免费无限**（脚本/随机 agent 跑出来即可）。
### 3.3 世界模型：先用引擎，可选再学
- **PoC（推荐）**：**引擎即模拟器**，NPC 直接行动；不训世界模型。
- **可选 Phase 4**：小 **Dreamer 式潜在动力学**（RSSM/小 transformer，**~1–20M 参数**）在符号状态上学，用于**想象式规划**或加速；1 GPU 几小时–1 天。要"看得见的世界"再加小 VQ tokenizer + 像素 decoder（~10–50M，1 GPU 数天）。

## 4. NPC 心智 = 生成式智能体（核心）
### 4.1 记忆节点
```python
Memory = {id, t, kind: observation|reflection|plan, text, embedding,
          importance(1–10), last_accessed}
```
### 4.2 检索（Park et al. 三项加权）
`score = α·recency + β·importance_norm + γ·relevance` ，
`recency = decay^(hours_since_last_accessed)`（decay≈0.99），relevance=query 与记忆 embedding 余弦；三项各归一到 [0,1]，取 **top-k（k≈10–20）** 喂 prompt。
### 4.3 「学习」= 反思（reflection）
**触发**：自上次反思以来 Σimportance > 阈值（≈150）。
**Prompt**：
> 「给定 {agent} 近期记忆：{retrieved}。请提出关于 {agent} 或其世界的 **3 条高层洞察**，每条附支持证据(记忆id)。」
洞察回写为 `kind=reflection` 的高 importance 记忆 → 后续检索/规划会用到 ⇒ **行为随之改变（这就是"学习"）**。
### 4.4 「写日记」= 每日总结
**Prompt（每"日"末）**：
> 「以第一人称写 {agent} 在 {date} 的日记：回顾今日要事与感受。今日关键记忆：{当日 top importance 记忆}。」
日记条目存库（也可作高层记忆）。
### 4.5 规划 + 行动（事件驱动，不必每 tick 调 LLM）
**Prompt**：
> 「身份：{persona}。当前：{pos,time,nearby,inventory,当前计划}。相关记忆：{retrieved}。近期洞察：{reflections}。下一步 {agent} 做什么？输出：action∈{动作表} + target + 一句理由。」
**省钱**：缓存"日计划"→分解为子目标；**仅在事件/每 N tick/反思时调 LLM**，其余 tick 走寻路/脚本执行。
### 4.6 importance 评分 prompt
> 「1–10 给这条记忆的"重要度"打分（1=刷牙这类琐事，10=人生大事）：{observation}。分数：」

## 5. 技术栈（都用现成）
引擎：自建 tile 引擎 / 或 Phaser/Godot/PettingZoo-style gridworld。LLM：**自托管 7–14B（Qwen/Llama 级，量化 vLLM）或 API**。嵌入：bge-small/gte-small。向量库：FAISS/Chroma。RL（可选）：CleanRL PPO / DreamerV3 参考实现。

## 6. 数据（这是最大红利）
**自有引擎生成 → 免费、无限、自带动作标注**；**无隐私/IP/同意闸、无具身 gap**——前面那条世界模型线的所有硬约束这里都不存在。

## 7. 资源 / 预算分档
| | PoC（1–3 NPC） | 小规模（~25 NPC, Smallville 级） |
|---|---|---|
| 硬件 | **1–2 GPU**（24–80GB：可选小模型训练 + 7B 推理；或纯 API） | **1–4 GPU**（瓶颈=并发 LLM 推理）+ 服务器 |
| 训练 | 几乎 0（引擎即模拟器）；可选小策略 ~$50 | 训练不变；可选 LoRA 人设 ~$100–500 |
| 推理/运行（大头） | 低（单 agent） | 自托管 7–14B；或 API（原版 25-agent~2 模拟日**据报数千美元 API**，量级） |
| 数据 | **$0** | $0 |
| 工程 | ~2–6 周 | +数周（并发/记忆/调优） |

## 8. 里程碑
| M | 内容 | 退出标准 | 约期 |
|---|---|---|---|
| **M0** | 引擎 + 符号状态 + 动作 API + 随机/脚本 agent（产数据） | NPC 能在地图移动/交互；日志可回放 | 1–2 周 |
| **M1** | 单生成式智能体闭环（记忆流+检索+LLM 规划/行动） | NPC **自由探索 + 成功交互**（覆盖率↑、目标完成） | 2–3 周 |
| **M2** | **反思(=学习) + 每日日记** | 日记连贯且与记忆一致；**反思 on vs off 行为差异可测** | 2 周 |
| **M3** | 多 NPC（~10–25）+ NPC 间交互 + 推理扩展 | 多 agent 稳定运行；推理成本/延迟在预算内 | 3–4 周 |
| **M4（可选）** | 学习型世界模型(想象规划) / LoRA 人设 / 像素可视化 | 想象规划提升样本效率 或 人设/画面达标 | 按需 |

## 9. 评测
- **探索**：地图覆盖率随时间、novelty/重访比、目标到达率。
- **交互**：成功交互数、任务完成率。
- **日记**：人评/LLM-judge 的连贯性+与记忆一致性评分。
- **学习（关键，要可证伪）**：设一个**反思应当改善表现的受控任务**（如"记住某物在哪→下次更快取到"），**ablate 反思 on/off**，看行为/成功率是否显著变化；或复刻 Smallville 的"可信度"人评。

## 10. 风险与缓解
1. **LLM 推理成本/延迟随 NPC×记忆长度涨** → 计划缓存、事件驱动调用、记忆压缩（反思替代原始记忆）、小模型+LoRA、批量推理(vLLM)。
2. **记忆膨胀/上下文溢出** → 检索 top-k + 周期性压缩/遗忘（低 importance 衰减）。
3. **日记/规划幻觉** → 强制结构化输出、grounding 到记忆 id、动作受动作表约束。
4. **"学习"流于表面** → §9 的受控可证伪任务，别只看"看起来像在学"。

## 11. 与世界模型研究线的协同（顺带的大价值）
这个**自有固定地图沙盒** = Track A LAM / 世界模型方法的**理想受控测试床**：**有 ground-truth 动作、可控注入干扰物、数据免费** ⇒ 可在这里**廉价验证**潜在动作/世界模型/迁移（[`experiments/track_a_lam/`](track_a_lam/) 的探针与配方），再上更难的真实设置。建议把沙盒的日志格式对齐 `track_a_lam` 的 data_contract。

---
## 12. 引擎选型
| 选项 | 何时 | 说明 |
|---|---|---|
| **自建 headless tile 引擎（Python）** | **起步（推荐）** | = 现有 `experiments/npc_agent/` 骨架：最简、全控、RL/sim 友好、数据免费、无渲染开销 |
| **Godot / Phaser / web 渲染** | 要可视化/可交互 demo | 加一层**薄渲染**读引擎状态；**cognition 不耦合重引擎** |
| **PettingZoo / Gymnasium gridworld** | 要标准 (multi-agent) RL API + 学习型世界模型 | 标准接口，方便接 CleanRL/DreamerV3 |
建议：**headless 自建跑 cognition/sim 研究 + 薄渲染做 demo**；别早早绑死重游戏引擎。

## 13. 多 agent 推理预算（精算）
**假设**：sim-day=1440 tick；LLM **非每 tick 调**（事件驱动 + 计划缓存）；每 agent/sim-day ≈ **100–160 次调用**（规划 ~100–150 + 反思 ~5 + 日记 1）；每次 ≈ **1k input / 100 output** token（persona+state+检索 ~10 记忆+洞察）。
**算**：25 agent × ~150 调用 × ~1.1k token ≈ **~4M token / sim-day**（input 为主）。
- **API（便宜小模型 ~$0.1–0.5/M token）**：**~$1–5 / sim-day（25 agent）**；多日 sim ~$10–100。（原版 Smallville 用更贵模型 + 更多调用 → 数千美元；2026 便宜小模型便宜得多。）
- **自托管 7B/vLLM**：单 A100/4090 吞吐 ~数千 token/s → 4M token/sim-day 是分分钟的活；**1 GPU 轻松带 ~25 agent 非实时 sim**；实时交互看单次延迟(~0.5–2s)，跨 agent 批处理 → 1 GPU ~25 够，更多**线性加 GPU**。
- **成本驱动 = agent 数 × 调用频率 × 上下文长度**（检索记忆越多越贵）→ 省钱杠杆：计划缓存、事件驱动调用、记忆压缩（反思替原始）、小模型+LoRA、批量推理。
- **一句话**：**~25 个会写日记会学习的 NPC = API ~$1–5/sim-day 或自托管 1 张 GPU**；扩 N 倍线性涨，**瓶颈在推理不在训练**。

---
*维护：方案稿；代码骨架已落 `models/experiments/npc_agent/`（可跑 demo 验证 explore→交互→反思学习→日记，learning PASS：day1 40 tick → day2 16 tick）。*
