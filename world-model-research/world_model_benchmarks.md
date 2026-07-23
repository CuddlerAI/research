# 专题：World Model 评测 Benchmark 全景（2024–2026）

> 回答「world model 领域有哪些 bench」。按**评什么**分 6 类编目，每个标注**测什么 / 谁用 / 链接 / 对我们的相关度**。检索 2026-06-29。
> 关联评测口径见 [`../training/training_plan.md`](training_plan.md) §3。

---

## TL;DR

- **没有"唯一的 world model benchmark"**——它按**你在乎什么**碎成几类：视觉质量 / 动作可控性 / 物理正确性 / 下游控制成功率。
- **2025 的关键发现**：**视觉好 ≠ 物理对**。Physics-IQ 显示 Sora/Runway 等画面惊艳但**物理动力学不及格**。→ **FVD 这类视觉指标必要但不充分**。
- **对我们（游戏世界模型→机器人）**：①游戏 WM 阶段看**可控性 + 一致性 + 视觉**；②机器人阶段**下游任务成功率才是真指标**（EWMBench/RoboWM-Bench/真机）；③多数还需**自建 in-domain 评测**（held-out 游戏：动作响应准确度 + rollout 一致时长），WHAM/Genie 都这么做。

---

## A. 统一「世界生成」基准（最新，2025–26）

| Benchmark | 测什么 | 链接 | 对我们 |
|---|---|---|---|
| **WorldScore** | 首个统一「世界生成」基准；3,000 例（静/动、室内外、写实/风格化），三轴：**可控性 / 质量 / 动态性**，按相机轨迹分解为逐场景生成 | arXiv:2504.00983 · [site](https://haoyi-duan.github.io/WorldScore/) | ★ 游戏 WM 的「可控性+动态」可借 |
| **WorldModelBench** | 把视频生成模型当 world model 评判；CVPR'25 workshop + 榜 | [worldmodelbench.github.io](https://worldmodelbench.github.io/) | ★ 关注其指标体系 |
| **WorldArena / 2.0** | **具身** world model 的**感知 + 功能效用**统一评测；2.0 扩 模态/功能/平台 | arXiv:2602.08971 · 2605.17912 | ★★ 偏具身/机器人，贴我们终点 |
| **4DWorldBench** | 4D 世界生成 | （新） | 备注 |

## B. 物理正确性 / 视频可信度

| Benchmark | 测什么 | 链接 | 对我们 |
|---|---|---|---|
| **Physics-IQ** | 396 真实视频，流体/固体力学等；测「能否物理正确地续帧」。**SOTA 普遍不及格** | arXiv:2501.09038（+Verified 2606.18943） | ★★ 一针见血：别被画质骗 |
| **VideoPhy / VideoPhy-2** | T2V 物理常识；V2=3,940 prompt、动作中心、5 分 Likert | arXiv:2503.06800 | ★ 物理合理性 |
| **Physion / ++ / Eval** | 物体碰撞/稳定性，预测结果 + 反推质量/摩擦 | 2603.19607 | ★ 经典物理预测 |
| **PhyWorldBench / PhyGround / PhysicsMind** | 更多物理写实评测 | 2507.13428 / 2605.10806 / 2601.16007 | 备选 |

## C. 动作可控性 / 可交互世界模型

| Benchmark | 测什么 | 链接 | 对我们 |
|---|---|---|---|
| **ACT-Bench** | **动作保真度**：给定轨迹，生成场景是否照做（自动驾驶域）；含 ACT-Estimator + TERRA 基线 | arXiv:2412.05337 · [HF](https://huggingface.co/datasets/turing-motors/ACT-Bench) | ★★ 「给动作→画面是否照做」正是我们 WHAM 式核心评测的思路 |
| **WorldSimBench** | 视频生成模型当世界模拟器；人类偏好打分 + 感知/操作双评 | arXiv:2410.18072 | ★ |
| **iWorld-Bench** | 交互式世界模型 + 统一动作生成框架 | [iworld-bench.com](https://iworld-bench.com/) | ★ 最贴「可玩/可控」 |

## D. 具身 / 机器人世界模型（我们的终点最该看这里）

| Benchmark | 测什么 | 链接 | 对我们 |
|---|---|---|---|
| **EWMBench** | 具身 world model：场景一致性(DINOv2) + 运动正确(HSD/nDTW) + 语义(BLEU/CLIP) + 多样性 | arXiv:2505.09694 | ★★ 机器人 WM 的代表评测 |
| **RoboWM-Bench** | 把生成行为**转成动作序列、真机执行验证** | arXiv:2604.19092 | ★★ 「能不能真控制」闭环 |
| **Genie Envisioner** | 机器人操作的统一世界基础平台（含评测） | arXiv:2508.05635 | ★ |
| **下游机器人基准** | **CALVIN**（操作成功率）/ **LIBERO**（终身学习 4 套件）/ **SIMPLER**（真机策略仿真评）/ Meta-World / RLBench / ManiSkill | 各自官网 | ★★ world-model 策略最终在这些上比成功率 |

## E. 模型基 RL（控制类世界模型经典基准）

| Benchmark | 测什么 | 谁用 | 对我们 |
|---|---|---|---|
| **Atari 100k** | 26 游戏、100k 交互步的样本高效 RL；DIAMOND 人类归一 **1.46** | DreamerV3 / IRIS / STORM / TWM / DIAMOND | ★ 若在「梦里训策略」会用 |
| **DMC（DeepMind Control）** | 连续控制（proprio + vision） | Dreamer 系 | ★ |
| **Crafter / Minecraft** | 开放世界生存 / 从零挖钻 | DreamerV3（Nature 2025, s41586-025-08744-2） | ★ |
| Procgen / Craftax / Atari200M | 泛化 / 长程 | 各家 | 备选 |

## F. 跨切指标（benchmark 用来打分的度量）

- **视觉/生成**：FVD（Fréchet Video Distance）、FID、PSNR/SSIM/LPIPS（逐帧保真）、CLIP。
- **一致性**：DINOv2 特征一致、时序一致性、rollout 漂移时长。
- **可控性**：动作保真度（ACT-Estimator 式：从生成画面反估动作 vs 指令）。
- **物理**：物理合理性评分（人评/判别器）。
- **★ 下游**：控制/操作**任务成功率**、数据效率、规划速度——**对机器人目标最诚实**。

---

## 对我们路线图的取用

| 阶段 | 主看 | 自建补充 |
|---|---|---|
| **Phase 2 游戏 WM**（WHAM 式） | 可控性/动态（WorldScore 思路）、动作保真（ACT-Bench 思路）、FVD/PSNR；物理（Physics-IQ 抽样） | **held-out 游戏评测**：动作响应准确度 + rollout 一致时长 + behavior-policy 匹配 |
| **Phase 3 隐空间/隐动作** | 隐动作可控性、表征探针 | latent rollout 区分好坏动作 |
| **Phase 4 机器人** | **EWMBench / RoboWM-Bench**；下游 **CALVIN/LIBERO/SIMPLER** + 真机（V-JEPA-2-AC 式抓取/放置） | 零样本成功率 + 数据效率 + 规划速度 |

> **务实建议**：别一上来追公开榜。Phase 2 先建**自己的 in-domain held-out 评测**（最能反映"在游戏数据上学没学到动力学"），公开 benchmark 用于**对外可比性 + 物理/可控性抽查**；机器人阶段再切到 EWMBench/真机成功率。

## Sources（检索 2026-06-29）
- WorldScore arXiv:2504.00983 ｜ WorldModelBench https://worldmodelbench.github.io/ ｜ WorldArena 2602.08971 / 2.0 2605.17912
- Physics-IQ 2501.09038（Verified 2606.18943）｜ VideoPhy-2 2503.06800 ｜ Physion-Eval 2603.19607 ｜ PhyWorldBench 2507.13428
- ACT-Bench 2412.05337 ｜ WorldSimBench 2410.18072 ｜ iWorld-Bench https://iworld-bench.com/
- EWMBench 2505.09694 ｜ RoboWM-Bench 2604.19092 ｜ Genie Envisioner 2508.05635 ｜ Awesome-WAM https://github.com/OpenMOSS/Awesome-WAM
- DIAMOND 2405.12399（Atari100k 1.46）｜ DreamerV3 Nature s41586-025-08744-2 ｜ CALVIN / LIBERO / SIMPLER 各官网
