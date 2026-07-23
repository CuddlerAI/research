---
title: World Model Research — A Comprehensive Survey (June 2026)
subtitle: 现状、方法谱系，与「无标注交互视频 → 世界模型 → 具身控制」路线综述 / State of the field & the unlabeled-video → world-model → embodied-control thesis
date: 2026-06-29
as_of: 2026-06-29
license: CC BY 4.0
authors: Diogenes Lab
note: 本文由内部完整版泛化清洗而来（去产品品牌 / 内部链接 / 内部战略段）。Generalised from an internal edition.
---

# 世界模型研究全景调研（2026-06）
# World Model Research — A Comprehensive Survey (June 2026)

> **怎么读 / How to read.** 本报告中文为主、英文并行；**方法目录表、参考文献用英文**（名词/链接本就是英文）。§0–§6 是领域综述（每节：导览 → 方法表 → 趋势 → 开放问题），§8 参考文献，§9 不确定性与待核实项。
> Chinese-primary with parallel English; **catalog tables & references are in English**. §0–§6 survey the field; §8 references; §9 caveats.

---

## 摘要 / Executive Summary

**中文.** 截至 2026 年 6 月，"世界模型"已从一个 RL 子领域膨胀为横跨生成式视频、具身智能、自动驾驶与消费产品的主战场（2026 Q1 一个季度即有 **>$20 亿**风险投资涌入）。全局看有七条主线结论：

1. **范式二分**：*像素生成派*（Sora/Veo/NVIDIA Cosmos/DeepMind Genie/各类神经游戏引擎）画面惊艳、可实时交互，但**物理脆弱、规划昂贵**；*预测潜在派*（Meta 的 JEPA 系）不生成像素、**省标注、可廉价用于控制**（V-JEPA 2-AC 的规划比 Cosmos 快约 15×）。这是当前最核心的架构分歧。
2. **正在合流**：传统基于模型的强化学习（MBRL，Dreamer 系）与生成式视频世界模型正融为一体——**Dreamer 4**（2025-09）从无标注视频学知识、纯离线想象训练拿到 Minecraft 钻石；**DIAMOND** 的世界模型同时就是一台可玩的 CS:GO 神经引擎。"智能体模型 vs 模拟器"的旧二分正在消失。
3. **通往真机的桥已被验证，但从不是"零数据"**：**V-JEPA 2-AC** 用 **≤62 小时无标注**机器人视频即零样本驱动真实 Franka 机械臂；LAPA/UniVLA 只需"小规模"标注就超过用全标注训练的 OpenVLA。**但没有任何公开系统能用 0 真机动作数据做到无标注视频 → 真机控制。**
4. **潜在动作（latent action）是"无标注视频可学控制"的关键机制，但它在"动作相关的干扰物"下会崩**——即 reconstruction 把背景/镜头/HUD 等可预测但不可控的运动当成了"动作"（"future leakage"）。**游戏画面恰恰塞满了这类干扰物。**好在 2025–2026 的修法很便宜：在 DINO 语义空间里学 LAM、用语言/VLM 屏蔽无关运动、用光流等"外生鲁棒"目标替代逐像素重建、**早期注入 2.5% 标注即可换 4.3× 下游提升**。
5. **评测正经历信任危机**：FVD 已被证伪（→ 改用 JEDi）；像素指标（PSNR/SSIM/LPIPS）测不出动力学；**唯一被认可的"世界模型级"评测是下游控制成功率**；物理基准（Physics-IQ / WorldModelBench / VideoPhy-2）一致显示"画面真实 ≠ 懂物理"。
6. **产业格局**：DeepMind（Genie 3 → 2026-01 消费级 Project Genie）、World Labs（李飞飞，"空间智能"，Marble，$1B）、NVIDIA Cosmos（开源平台）、微软（Muse/WHAM，Nature 2025）、Meta（V-JEPA 2）、Wayve（GAIA-1→3，已把世界模型从"生成"推向"安全验证"）、Decart/Runway/Luma（均 ~$4–5B 估值）。世界模型的兑现路径正从"生成"转向**合成数据生产**与**策略评测**。
7. **对 Diogenes Lab 的启示**：thesis 的*机制*（无标注交互视频 → 潜在动作 → 具身控制）已被逐块验证；但**"游戏/交互录屏 → 潜在动作 → 真机"这条完整链路尚无任何公开系统打通**——这是当前的 whitespace。真正的活**不是建模创新，而是**：数据合规、坚持**一方自有/已授权数据**以规避第三方 IP、一条**抗干扰物的潜在动作管线**、以及一套**控制成功率评测 harness**。务实预期：需要"小但非零"的真机数据（量级：几十小时无标注真机视频，或几百条标注轨迹），**"纯游戏视频零样本上真机"是过度承诺**。

**English.** As of June 2026, "world models" have grown from an RL sub-topic into a main battleground spanning generative video, embodied AI, autonomous driving and consumer products (**>$2B** of VC in Q1 2026 alone). Seven cross-cutting conclusions:

1. **A paradigm split.** *Pixel-generative* world models (Sora/Veo/NVIDIA Cosmos/DeepMind Genie/neural game engines) are visually stunning and interactive but **physics-brittle and expensive to plan with**; *predictive-latent* models (Meta's JEPA line) don't render pixels, are **label-free and cheap for control** (V-JEPA 2-AC plans ~15× faster than a Cosmos baseline). This is the central architectural debate.
2. **Convergence.** Classic model-based RL (Dreamer line) and generative-video world models are merging: **Dreamer 4** (Sep 2025) mines Minecraft diamonds **offline**, learning mostly from unlabeled video; **DIAMOND**'s world model doubles as a playable CS:GO engine. The "agent-model vs simulator" split is dissolving.
3. **The bridge to robots is validated but never zero-data.** **V-JEPA 2-AC** drives a real Franka arm zero-shot from **≤62h of *unlabeled* robot video**; LAPA/UniVLA beat fully-action-labeled OpenVLA with only a "small" labeled set. **No public system goes unlabeled-video → real control with zero action data.**
4. **Latent action is the key label-free mechanism — and it collapses under action-correlated distractors** ("future leakage": reconstruction encodes background/camera/HUD motion as "action"). **Game footage is worst-case for this.** Cheap 2025–2026 fixes: build the latent-action model in DINO feature space, language/VLM masking, optical-flow (exogenous-robust) targets, and **2.5% early labels → 4.3× downstream gain**.
5. **Evaluation is in crisis.** FVD is broken (→ JEDi); pixel metrics miss dynamics; **downstream control success is the only accepted "world-model-grade" test**; physics benchmarks show realism ≠ physical understanding.
6. **Industry.** DeepMind (Genie 3 → consumer Project Genie Jan 2026), World Labs (Fei-Fei Li, "spatial intelligence", Marble, $1B), NVIDIA Cosmos (open platform), Microsoft (Muse/WHAM, Nature 2025), Meta (V-JEPA 2), Wayve (GAIA-1→3, shifting world models from generation to **safety validation**), Decart/Runway/Luma (all ~$4–5B). The payoff is shifting from generation toward **synthetic-data generation** and **policy evaluation**.
7. **For Diogenes Lab.** The thesis *mechanism* is validated piecewise, but **no public system chains screen/game-capture video → latent action → real robot** — that is our whitespace. The real work is **not modeling novelty** but: data-use consent, first-party data to dodge third-party game IP, a **distractor-robust latent-action pipeline**, and a **control-success eval harness**. Expect a **small but nonzero** real-robot set; "zero-shot to a robot from pure game video" would be over-claiming.

---

## §0. 术语与分类 / What is a "world model"? Taxonomy

**中文.** 一个**世界模型**是对环境动态的可学习预测模型：给定（潜在）状态与动作，预测下一个（潜在）状态、观测与/或回报。这个词跨越三种研究文化：

- **(A) RL 智能体模型 / MBRL** —— 为*控制*而学的模型，用于规划（前瞻）或"想象"rollout 来少样本地训练策略。根在 Sutton 的 **Dyna(1991)**；Dreamer/PlaNet/MuZero/TD-MPC 都属此类。
- **(B) 生成式模拟器 / 视频世界模型** —— 动作条件（或潜在动作）的生成式视频模型，*渲染*出可控环境（Genie、把世界模型当游戏引擎的 DIAMOND、Sora/Veo/Cosmos 等）。重画面保真与可交互。
- **(C) 预测式表征模型** —— 自监督地预测未来*表征*（而非像素）来学状态（JEPA 系）。重可迁移的语义表征、廉价的控制。

**两条正交设计轴**贯穿全表：① **潜在 vs 重建**（MuZero/TD-MPC 不解码像素、只让回报塑造潜在；Dreamer/IRIS/DIAMOND 重建像素）；② **规划 vs 想象**（在决策时在线前瞻 vs 离线生成长 rollout 训练 actor-critic）。**核心张力**——"视频生成模型到底算不算世界模型？"——贯穿 §2/§3/§6：能渲染逼真画面，不等于学到了可外推的动力学/物理。

**English.** A **world model** is a learned predictive model of environment dynamics — given (latent) state + action, predict the next (latent) state, observation and/or reward. The term spans three cultures: **(A) MBRL agent models** (learned *for control*, used for planning/imagination; root: Sutton's Dyna 1991; Dreamer/MuZero/TD-MPC); **(B) generative simulators / video world models** (action- or latent-action-conditioned generative video that *renders* a controllable environment; Genie, DIAMOND, Sora/Veo/Cosmos); **(C) predictive representation models** (self-supervised prediction of future *representations*, not pixels; the JEPA line). Two orthogonal axes organize everything: **latent vs reconstruction** and **planning vs imagination**. The recurring tension — *"is a video generator actually a world model?"* — runs through §2/§3/§6: photorealistic rendering ≠ learning extrapolable dynamics/physics.

## §1. 基础与基于模型的强化学习 / Foundations & Model-Based RL

**导览 / Overview.** 这是世界模型的历史主干：从 Ha & Schmidhuber 的 V-M-C（2018）到 Dreamer 系、MuZero/TD-MPC 系。2024–2026 的两大信号是：**(i) DreamerV3 登上 *Nature*（2025-04）**，证明一套固定超参可泛化到 150+ 任务且有 LLM 式 scaling；**(ii) Dreamer 4（2025-09）纯离线、从无标注视频学知识**拿到 Minecraft 钻石——这是目前与该 thesis 最贴合的单一成果。
*This is the historical spine. The 2024–2026 signals: DreamerV3 in Nature (Apr 2025) — one config across 150+ tasks with LLM-like scaling — and Dreamer 4 (Sep 2025), offline diamonds learned mostly from unlabeled video, the most thesis-aligned MBRL result to date.*

| Method | Org | Year | Type | Contribution | Link |
|---|---|---|---|---|---|
| **World Models (V-M-C)** | Ha & Schmidhuber | 2018 | recon. latent, imagination | VAE+MDN-RNN+evolved controller; policy trained *inside the dream* | [1803.10122](https://arxiv.org/abs/1803.10122) |
| **PlaNet** | Google | 2018 | recon. latent, planning | RSSM latent + online CEM planning from pixels | [1811.04551](https://arxiv.org/abs/1811.04551) |
| **Dreamer / V2** | Google/DeepMind | 2019/2020 | recon. latent, imagination | Actor-critic by backprop through imagined rollouts; V2 = discrete latents, human-level Atari | [2010.02193](https://arxiv.org/abs/2010.02193) |
| **MuZero** | DeepMind | 2019 (Nature 2020) | decoder-free, MCTS | Value-equivalent model + MCTS; masters Go/chess/Atari **without rules** | [1911.08265](https://arxiv.org/abs/1911.08265) |
| **EfficientZero** | Ye et al. | 2021 | decoder-free, MCTS | First super-human Atari-100k (194% mean) | [2111.00210](https://arxiv.org/abs/2111.00210) |
| **TD-MPC / TD-MPC2** | UCSD (Hansen et al.) | 2022/2023 | decoder-free, MPC | Task-oriented latent + latent MPC; **one 317M agent → 80 tasks**, scales w/ size+data | [2310.16828](https://arxiv.org/abs/2310.16828) |
| **DayDreamer** | UC Berkeley | 2022 | recon. latent, **real robot** | Dreamer on hardware: quadruped walks from scratch in ~1h, no sim | [2206.14176](https://arxiv.org/abs/2206.14176) |
| **Diffuser / Decision Diffuser** | MIT | 2022 | diffusion planner | Plan by denoising whole trajectories; constraint-conditioned decisions | [2205.09991](https://arxiv.org/abs/2205.09991) |
| **IRIS / STORM** | Geneva / — | 2022/2023 | recon. latent (Transformer), imagination | Tokenized/transformer world models; strong Atari-100k w/o search | [2209.00588](https://arxiv.org/abs/2209.00588) |
| **DreamerV3** | DeepMind | 2023; **Nature 2025** | recon. latent, imagination | One config / 150+ tasks; **first Minecraft diamond w/o human data**; favorable scaling | [2301.04104](https://arxiv.org/abs/2301.04104) · [Nature](https://www.nature.com/articles/s41586-025-08744-2) |
| **DIAMOND** | Geneva/Edinburgh/MSR | 2024 (NeurIPS) | **diffusion** WM, imagination | Agent trained inside a diffusion WM; 1.46 Atari-100k; doubles as CS:GO engine | [2405.12399](https://arxiv.org/abs/2405.12399) |
| **Dreamer 4** | DeepMind | 2025-09 | transformer-diffusion, **offline** imagination | **First offline Minecraft diamonds**; knowledge from *unlabeled* video, action-conditioning from *small* labeled set; real-time on 1 GPU | [2509.24527](https://arxiv.org/abs/2509.24527) |

**趋势 / Trends.** ① DreamerV3 的"一套超参打天下"+ Nature 背书，使 MBRL 重获可信度，并证明**模型越大越快越省数据**（TD-MPC2 同结论）。② 世界模型骨干从 RNN/VAE → Transformer（IRIS/STORM）→ 扩散（DIAMOND、Dreamer 4），DIAMOND 的论点"token 压缩会丢掉控制相关的视觉细节"把前沿推回高保真生成式。③ **离线/纯想象训练**成为新硬指标（Dreamer 4），动机正是机器人——真实交互不安全、慢。
*DreamerV3's "one config" + Nature gave MBRL renewed credibility and confirmed favorable scaling (echoed by TD-MPC2). Backbones moved RNN→Transformer→diffusion. Offline/imagination-only training (Dreamer 4) is the new hard target, motivated by robotics.*

**开放问题 / Open problems.** 复合模型误差/想象漂移；保真 vs 紧凑的张力（解码器自由的潜在不能当模拟器）；长程稀疏奖励；离线分布漂移；扩散/大 Transformer 世界模型的算力与实时延迟。
*Compounding rollout error; the fidelity-vs-compactness tension; long-horizon sparse reward; offline distribution shift; the compute/latency of diffusion & large-transformer world models.*

**与 thesis 关联 / Relevance.** **Dreamer 4 是整条 thesis 最接近的概念验证**（无标注视频学知识 + 小标注学动作 + 纯离线想象 + 面向机器人）；**DayDreamer** 证明 Dreamer 式世界模型能快速迁移到真机；**DreamerV3/TD-MPC2** 提供"规模化喂数据→更强世界模型"的前提证据。

---

## §2. 交互式 / 生成式游戏世界模型 / Interactive & Generative Game World Models

**导览 / Overview.** 这是离 thesis 数据形态最近的一支：**用游戏/录屏视频学出一台可实时游玩的"神经游戏引擎"**。两个关键事实：**Genie（2024-02, ICML 最佳论文）证明可从完全无标注视频学出"可玩、可控"的世界模型，动作作为潜在量被无监督发现**；而几乎所有*高保真*引擎（GameNGen/DIAMOND/Oasis/WHAM/Yan）都用**有标注**动作 + **单一游戏**——它们是引擎/解码策略的参考，但不是 thesis 的数据情形。
*The closest data-form to the thesis: learn a real-time playable "neural game engine" from gameplay video. Two facts: **Genie (Feb 2024, ICML Best Paper) proves a playable, controllable world model can be learned from fully unlabeled video, with actions discovered as latents**; but nearly all high-fidelity engines use labeled actions on a single title — useful as engine references, not as thesis precedents.*

| Name | Org | Date | Approach | Real-time? | Action source | Link |
|---|---|---|---|---|---|---|
| **Genie 1** | DeepMind | 2024-02 | tokenizer + AR dynamics + **latent action model** (11B) | No | **Latent / unlabeled** internet video | [2402.15391](https://arxiv.org/abs/2402.15391) |
| **Genie 2** | DeepMind | 2024-12 | AR latent diffusion; image-prompted 3D | No (research) | keyboard→character (latent lineage) | [blog](https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/) |
| **Genie 3** | DeepMind | 2025-08 | real-time world model | **Yes — 720p/24fps** | navigation + "promptable world events" | [blog](https://deepmind.google/blog/genie-3-a-new-frontier-for-world-models/) |
| **Project Genie** | DeepMind/Google Labs | **2026-01-29** | Genie-3 consumer product | Yes | text/image world-sketching; 60s cap | [blog](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/project-genie/) |
| **GameNGen** | Google/TAU | 2024-08 | diffusion (SD adapted) | **Yes — ~20fps, 1 TPU** | labeled (RL-agent actions) | [2408.14837](https://arxiv.org/abs/2408.14837) |
| **Oasis** | Decart + Etched | 2024-10 | diffusion transformer, AR | **Yes — ~20fps** | labeled (Minecraft kb/mouse) | [site](https://oasis-model.github.io/) |
| **WHAM / Muse** | Microsoft + Ninja Theory | **Nature 2025-02** | AR transformer (VQGAN), 1.6B | No (~1 img/s) | labeled (Bleeding Edge controller) | [Nature](https://www.nature.com/articles/s41586-025-08600-3) |
| **WHAMM** | Microsoft | 2025-04 | MaskGIT (parallel decode) | **Yes — 10+fps** | labeled (Quake II); **1 week of data** | [MSR](https://www.microsoft.com/en-us/research/articles/whamm-real-time-world-modelling-of-interactive-environments/) |
| **The Matrix** | Alibaba/HKU | 2024-12 | diffusion + Swin-DPM (infinite-horizon) | **Yes — up to 16fps, 720p** | labeled game + unlabeled real footage; sim→real | [2412.03568](https://arxiv.org/abs/2412.03568) |
| **Matrix-Game 1/2/3** | Skywork AI | 2025-05→late | diffusion (17B) → few-step AR streaming → +long-horizon memory | **Yes (v2/3)** | labeled Minecraft | [2506.18701](https://arxiv.org/abs/2506.18701) |
| **Yan** | Tencent | 2025-08 | 3D-VAE sim + AR gen + edit | **Yes — 1080p/60fps** | labeled (Tencent game, 400M frames) | [site](https://greatx3.github.io/Yan/) |
| **Mirage / Mirage 2** | Dynamics Lab | 2025 | transformer+diffusion, cloud-streamed | **Yes — ~200ms, 10+min** | any image/sketch + live text edits | [decoder](https://the-decoder.com/mirage-2-allows-users-to-turn-sketches-and-photos-into-interactive-game-worlds/) |
| **Runway GWM-1** | Runway | 2025-12 | general world model | **Yes — 720p/24fps** | camera + **robot actions** + audio | [news](https://mlq.ai/news/runway-launches-gwm-1-world-model-with-real-time-interaction-capabilities/) |

**趋势 / Trends.** ① 2024 下半年扩散神经引擎落地（GameNGen/DIAMOND/Oasis）；②2025-02 微软 WHAM/Muse 上 *Nature*，首个显式**同时生成"人类动作"**的世界模型；③2025 中后段**中国开源潮 + 产品化**（Skywork Matrix-Game、腾讯 Yan 1080p60、Dynamics Lab Mirage）；④2025-08 **Genie 3** 成为实时质量标杆；⑤2025-11→2026-01 **闭环到智能体/机器人**（SIMA 2 在 Genie-3 世界里自我提升、Runway GWM-Robotics、Project Genie 消费级）。
*H2-2024 diffusion engines (GameNGen/DIAMOND/Oasis); Feb-2025 WHAM/Muse in Nature (first to co-generate human actions); mid-late-2025 Chinese open-source surge + productization (Matrix-Game, Yan 1080p60, Mirage); Aug-2025 Genie 3 sets the real-time bar; late-2025→Jan-2026 the loop closes to agents/robots (SIMA 2 self-improving inside Genie-3 worlds, Runway GWM-Robotics, consumer Project Genie).*

**开放问题 / Open problems.** **长程一致性/记忆**是定义性瓶颈（Genie 3 ~1 分钟、Project Genie 硬上限 60s、WHAMM 仅 ~0.9s）；**动作空间太浅**（Genie 3 能导航、不能精细操作——这正是机器人迁移的坎）；物理可信（演示好看、细究就破）；算力/延迟/成本（Odyssey 称 ~$1–2/用户·小时）；**IP/数据来源**（多数引擎训练于单一商业游戏）。
*Long-horizon consistency/memory is the binding constraint (Genie 3 ~1 min, Project Genie 60s cap, WHAMM ~0.9s); the action space is shallow (Genie 3 navigates but can't manipulate — the robotics-transfer gap); physics breaks under scrutiny; compute/latency/cost; IP/provenance (most engines train on a single commercial game).*

**与 thesis 关联 / Relevance.** **Genie 1 是最强概念先例**（无标注视频→可玩可控世界模型，动作=无监督潜在量），其三段式架构（tokenizer → AR 动力学 → 潜在动作模型）应整篇精读；**WHAM 的可复用资产是开源的 Bleeding Edge 数据 + 权重**（一方自有游戏遥测——正是规避第三方 IP 的范式）；其余高保真引擎作为**解码加速（MaskGIT/少步扩散蒸馏）参考**。

## §3. 视频预测与 JEPA 预测式世界模型 / Video-Prediction & JEPA Predictive World Models

**导览 / Overview.** 本节是"范式之争"的主场：**预测潜在派（JEPA）**——预测被遮挡/未来状态的*表征*而非像素，主张像素生成把算力浪费在不可预测的细节上；**像素生成派（Cosmos/Sora/Veo/Genie）**——赌"把世界渲染出来"能 scale 成世界模型。2025 年的两个实证把天平拨向"二者各有其用、但控制场景里预测潜在更省"。
*The home of the paradigm debate: predictive-latent (JEPA) — predict *representations* of masked/future state, not pixels — vs pixel-generative (Cosmos/Sora/Veo/Genie). Two 2025 results tilt it: V-JEPA 2-AC plans ~15× cheaper for control, while physics benchmarks show pixel realism ≠ physical understanding.*

| Name | Org | Date | Paradigm | Gen. or repr.? | Note | Link |
|---|---|---|---|---|---|---|
| **I-JEPA / V-JEPA** | Meta FAIR | 2023 / 2024-02 | latent-predictive (masked) | **representation** | Predict masked features, no pixel recon, no augmentations | [2301.08243](https://arxiv.org/abs/2301.08243) |
| **V-JEPA 2** | Meta FAIR | 2025-06-11 | latent-predictive, action-free | repr. → WM | Self-sup on **>1M h** video; SOTA motion understanding/anticipation | [2506.09985](https://arxiv.org/abs/2506.09985) |
| **V-JEPA 2-AC** | Meta FAIR | 2025-06-11 | latent **action-conditioned** | repr. + planning | **<62h** unlabeled robot video → zero-shot Franka; **16s/action vs ~4min Cosmos** | [2506.09985](https://arxiv.org/abs/2506.09985) |
| **Cosmos (WFM platform)** | NVIDIA | 2025-01 | diffusion + AR; tokenizers | **generative** | Open World Foundation Models for Physical AI (Predict/Transfer/Reason) | [2501.03575](https://arxiv.org/abs/2501.03575) |
| **Cosmos Tokenizer** | NVIDIA | 2025-01 | visual tokenizer | infra | up to 2048× compression, ~12× faster — reusable for any video pipeline | [GitHub](https://github.com/NVIDIA/Cosmos-Tokenizer) |
| **Cosmos 3** | NVIDIA | **2026-06-01** | omnimodal, mixture-of-transformers | gen + reason + **act** | text/image/video/audio/**actions**; 20T tokens; "leading physics" (vendor claim) | [report](https://research.nvidia.com/labs/cosmos-lab/cosmos3/technical-report.pdf) |
| **Sora / Sora 2** | OpenAI | 2024 / 2025 | diffusion-transformer | generative | Marketed "world simulator"; fails physics benchmarks (§6) | — |
| **Veo 2/3** | Google DeepMind | 2024–2026 | diffusion (video) | generative | Veo-3 shows **emergent zero-shot perception/reasoning** (counter-argument to JEPA) | [2509.20328](https://arxiv.org/abs/2509.20328) |
| **Marble** | World Labs (Fei-Fei Li) | **2025-11-12** GA | 3D/spatial generative | generative (**persistent 3D**) | First commercial 3D world model; exports Gaussian splats/meshes | [TechCrunch](https://techcrunch.com/2025/11/12/fei-fei-lis-world-labs-speeds-up-the-world-model-race-with-marble-its-first-commercial-product/) |

**趋势 / Trends.** ① JEPA-vs-生成 成为核心架构分歧。② **LeCun 2025-12 离开 Meta** 创办 AMI Labs（押注 JEPA 式世界模型即 AGI 路径；融资数字各源不一，见 §9）。③ **V-JEPA 2-AC** 是"预测潜在→控制"的旗舰证据（<62h 机器人视频、规划比 Cosmos 快约 15×）。④ NVIDIA **Cosmos** 是生成派平台打法，迭代极快至 **Cosmos 3 全模态含 action**。⑤"视频生成=世界模型吗"在 2025 有了正反实证：Veo-3 涌现零样本感知/推理 *vs* 物理基准证明"真实≠懂物理"。⑥ **空间智能/持久 3D** 成独立赛道（World Labs Marble）。
*JEPA-vs-generative is the central split; LeCun left Meta (Dec 2025) to found AMI Labs on the JEPA thesis; V-JEPA 2-AC is the flagship predictive-latent→control result; NVIDIA Cosmos is the generative-platform play (now omnimodal Cosmos 3 with an action modality); the "is video-gen a world model?" debate got both-sides evidence in 2025; spatial-intelligence/persistent-3D (Marble) emerged as a distinct track.*

**开放问题 / Open problems.** 物理一致性（像素生成派的头号败因，且与画面真实度*不相关*）；长程一致性/记忆；评测割裂；可控性；像素世界模型在规划环里的算力代价（16s vs ~4min/动作即是明证）。
*Physics consistency (the headline failure of pixel generators, *uncorrelated* with realism); long-horizon coherence; fragmented eval; controllability; the compute cost of pixel world models in a planning loop.*

**与 thesis 关联 / Relevance.** **V-JEPA 2-AC 几乎是 thesis 的蓝图**（大规模无标注视频预训练 → 极少无标注交互数据适配 → 规划式零样本控制），且其预测潜在设计是"规划便宜"的根因；**Physics-IQ/VideoPhy** 提供反对"纯像素生成式世界模型"的证据，可用来论证押注预测潜在/混合、并定义评测；**Cosmos tokenizer** 是可复用基础设施。

---

## §4. 具身与自动驾驶世界模型 / Embodied & Autonomous-Driving World Models

**导览 / Overview.** 这是 thesis 的*终点*——世界模型如何真正抵达机器人。用一个干净框架看全场：**世界模型有两种角色**：**(1) 当模拟器/数据厂**（UniSim、Cosmos、GR00T-Dreams、Wayve GAIA）——输出视频/轨迹、用 IDM 反推动作、喂给*另一个*策略，这是**规模化部署**的那一支（驾驶 + NVIDIA 机器人）；**(2) 当规划器**（DayDreamer、V-JEPA 2-AC、iVideoGPT）——模型*本身*通过 rollout+优化就是控制器，样本效率高、长程难 scale。
*The destination. One clean framing: world models play **two roles** — **(1) simulator / data-factory** (UniSim, Cosmos, GR00T-Dreams, GAIA): output video/trajectories, recover actions via an IDM, feed a *separate* policy — the deployed-at-scale branch (driving + NVIDIA robotics); and **(2) planner** (DayDreamer, V-JEPA 2-AC, iVideoGPT): the model *is* the controller via rollout-and-optimize — sample-efficient, hard to scale to long horizons.*

| Name | Org | Date | Domain | Role | Action data | Link |
|---|---|---|---|---|---|---|
| **V-JEPA 2-AC** | Meta | 2025-06 | manip (Franka) | **planner** (latent MPC) | ≤62h unlabeled robot video | [2506.09985](https://arxiv.org/abs/2506.09985) |
| **UniSim / UniPi** | Google/Berkeley/MIT | 2023 | manip/nav | **simulator** → trains transferable policies | mixed; IDM at deploy | [2310.06114](https://arxiv.org/abs/2310.06114) |
| **GR00T N1 / N1.5** | NVIDIA | 2025-03 / 05 | humanoid | **policy (VLA)**, fed by WM data-gen | teleop + human video + **synthetic** | [2503.14734](https://arxiv.org/abs/2503.14734) |
| **GR00T-Dreams / DreamGen** | NVIDIA GEAR | 2025-06 | humanoid/manip | **data-gen** (dream → IDM → pseudo-actions) | image+prompt → synthetic | [GitHub](https://github.com/nvidia/gr00t-dreams) |
| **RoboDreamer / iVideoGPT** | MIT-IBM / Tsinghua | 2024 | manip | planner / WM (MBRL) | video+lang; IDM | [2404.12377](https://arxiv.org/abs/2404.12377) |
| **WorldVLA** | Alibaba DAMO | 2025-06 | manip | **unified policy + WM** | robot action (shared tokens) | [2506.21539](https://arxiv.org/abs/2506.21539) |
| **1X World Model** | 1X | 2025 | humanoid | **evaluator/sim** (eval policies) | raw humanoid sensors | [PDF](https://www.1x.tech/1x-world-model.pdf) |
| **GAIA-1 / 2 / 3** | Wayve | 2023 / 2025-03 / 2025-12 | **driving** | simulator → **validation/eval** | video+text+ego action | [GAIA-2 2503.20523](https://arxiv.org/abs/2503.20523) |
| **DriveDreamer 1/2 · Vista** | GigaAI/Tsinghua · OpenDriveLab | 2023–2024 | **driving** | simulator/data-gen | real driving video + layout/action | [Vista 2405.17398](https://arxiv.org/abs/2405.17398) |
| **OccWorld / OccSora** | — | 2024 | **driving** | 3D/4D-occupancy WM | occupancy + ego | [OccSora 2405.20337](https://arxiv.org/abs/2405.20337) |
| *VLA baselines:* **OpenVLA · π0 / π0.5** | Stanford+ · Physical Intelligence | 2024–2025 | manip | **policy** (not a WM) | OXE 970k; web data | [OpenVLA 2406.09246](https://arxiv.org/abs/2406.09246) |

**趋势 / Trends.** ①2022 DayDreamer 证明 MBRL 能在真机上学（四足~1h 学会走）；②2023 驾驶世界模型走向大模型（GAIA-1、UniSim）；③2024 VLA 浪潮 + 潜在动作思想（LAPA）成型；④2025-01 NVIDIA Cosmos 把世界模型定位成**合成数据引擎**；⑤2025 中"世界模型当数据厂"成主流工业配方（GR00T-Dreams "梦"轨迹→IDM→动作→训策略）；⑥2025-06 V-JEPA 2-AC 以*非生成*方式闭环到真机；⑦2025-12 **GAIA-3 把驾驶世界模型从"仿真"推向"安全验证/评测"**（外部 Warwick 验证），与 1X "在学到的模拟器里评估策略"同向。
*2022 DayDreamer (MBRL on hardware); 2023 large driving WMs (GAIA-1, UniSim); 2024 the VLA wave + latent-action idea; Jan-2025 Cosmos positions WMs as synthetic-data engines; mid-2025 "WM as data factory" becomes the dominant industrial recipe (GR00T-Dreams: dream → IDM → policy); Jun-2025 V-JEPA 2-AC closes the loop the non-generative way; Dec-2025 GAIA-3 repositions driving WMs from simulation to safety validation.*

**开放问题 / Open problems.** Sim-to-real / dream-to-real 保真（NVIDIA 的答案是合成*增强*而非替代真实，+40% 仅在混合时）；**从无标注视频做动作 grounding 是中心 gap——每个系统仍需一个标注桥**（LAPA 需小标注集、DreamGen/UniPi 需 IDM、V-JEPA 2-AC 需 62h 真机视频）；长程一致性；规划算力/延迟；真机标注数据成本（DROID 全量仅 350h）；跨具身/形态迁移；用世界模型评策略的"自证"风险。
*Sim/dream-to-real fidelity (synthetic must augment, not replace real); **action grounding from unlabeled video is the central gap — every system still needs a labeled bridge**; long-horizon coherence; planning compute/latency; the teleop-data bottleneck (DROID = 350h total); cross-embodiment transfer; the circularity of evaluating policies inside a learned sim.*

**与 thesis 关联 / Relevance.** 两个独立成果"夹击"了目标：**Genie/LAPA**（无标注视频→潜在动作→策略，小标注桥）与 **V-JEPA 2-AC**（潜在视频世界模型→真机零样本 MPC，~62h 无标注真机视频）。**没有一个做到零真机数据**；务实预期=**几十小时（可无标注）真机交互来对齐桥**，外加生成路线还要一个 IDM。**驾驶世界模型的教训**：最先兑现的价值是*合成数据 + 策略评测*，不是闭环想象规划；且必须外部对照真实再信任。

## §5. 潜在动作模型与跨具身桥接 / Latent Action Models & the Unlabeled-Video→Control Bridge

**导览 / Overview.** **本节就是 thesis 的桥**，相关度最高。整个研究线就是为了解决"视频没有动作标注、却想学出控制接口、再用少量标注对齐到真机"。**好消息：配方已成熟**——VQ-VAE 在相邻/远隔帧间学出离散"潜在动作"码本 → AR/VLA 骨干从观测预测这些潜在动作 → 小标注集把潜在解码成真实执行器指令（LAPA/Moto/GR00T/villa-X/UniVLA/GO-1 都是此配方变体，"VLA"正在变成"ViLLA = Vision-Language-**Latent**-Action"）。**坏消息（2025–2026 充分记录）：它在"动作相关干扰物"下会崩**——而游戏画面恰是最坏情形。
*This is the thesis bridge — maximum relevance. The recipe is mature: a VQ-VAE learns a discrete "latent action" codebook between frames → an AR/VLA backbone predicts those tokens from observations → a *small* labeled set decodes latent→real actuator commands ("VLA" is becoming "ViLLA = Vision-Language-**Latent**-Action"). The catch, well-documented in 2025–2026: it collapses under action-correlated distractors — and game footage is the worst case.*

| Method | Org | Date | Label requirement | Core idea / benefit | Link |
|---|---|---|---|---|---|
| **VPT** | OpenAI | 2022 | ~2k h labeled → IDM → pseudo-label ~70k h web video | **IDM pseudo-labeling** unlocks web-scale game video; first Minecraft diamond | [2206.11795](https://arxiv.org/abs/2206.11795) |
| **Genie LAM** | DeepMind | 2024 | **zero labels** | Unsupervised discrete latent actions from unlabeled video → controllability | [2402.15391](https://arxiv.org/abs/2402.15391) |
| **LAPO** | Schmidt & Jiang | 2023 (ICLR'24) | zero pretrain; tiny labeled/RL to align | IDM+forward dynamics autoencoder recovers true action *structure* from obs alone | [2312.10812](https://arxiv.org/abs/2312.10812) |
| **LAPA** | KAIST/UW/NVIDIA | 2024-10 (ICLR'25) | **zero in pretrain**; small robot set to align | VQ-VAE latent actions from unlabeled (even *human*) video → latent VLA; **beats OpenVLA**, ~30–40× cheaper | [2410.11758](https://arxiv.org/abs/2410.11758) |
| **Moto** | HKU/ByteDance | 2024-12 (ICCV'25) | zero; co-fine-tune | Latent motion tokenizer + Moto-GPT; interpretable motion tokens | [2412.04445](https://arxiv.org/abs/2412.04445) |
| **ATM / Track2Act** | Berkeley / CMU | 2024 | action-free; point tracks as action proxy | Predict point trajectories from video → policy; +80% over video-pretrain baselines | [2401.00025](https://arxiv.org/abs/2401.00025) |
| **AgiBot GO-1 (ViLLA)** | AgiBot/OpenDriveLab | 2025-03 | latent planner (human video) + action expert (>1M demos) | VLM → latent-action planner → MoE motor decoder; production generalist | [2503.06669](https://arxiv.org/abs/2503.06669) |
| **GR00T N1 (latent)** | NVIDIA | 2025-03 | latent codebook + IDM annotate action-less video | Unlabeled human video as an "extra robot embodiment" | [2503.14734](https://arxiv.org/abs/2503.14734) |
| **UniVLA** | OpenDriveLab/HKU | 2025-05 (RSS'25) | zero; task-centric latent in **DINO space** | Language-conditioned LAM suppresses task-irrelevant motion; **beats OpenVLA at 1/10 downstream data, 1/20 compute** | [2505.06111](https://arxiv.org/abs/2505.06111) |
| **UniSkill / villa-X / UniAct** | KAIST / MSR / CVPR'25 | 2025 | zero in latent stage | Embodiment-agnostic skills / shared universal action space across embodiments | [villa-X 2507.23682](https://arxiv.org/abs/2507.23682) |

**"何时会失败"——必读批判线 / The "when it fails" line (essential).** *以下多为 2026 新作，arXiv ID 由调研代理报告，正式引用前请复核（见 §9）。*

| Paper | Date | Finding |
|---|---|---|
| **LAL Requires Supervision in Presence of Distractors** ([2502.00379](https://arxiv.org/abs/2502.00379)) | 2025-02 | LAPO 式方法在动作相关干扰物（动背景/镜头运动）下**崩溃**；**LAM 训练期注入 2.5% 真标注 → 4.3× 下游提升**。监督要*早*给。 |
| **Why Latent Actions Fail, and How to Prevent It** ([2605.20223](https://arxiv.org/html/2605.20223)) | 2026-05 | 失败理论="**future leakage**"——重建迫使潜在动作编码*未来外生状态*而非动作；修法=跨外生重建 + 光流等外生鲁棒目标。 |
| **VLMs Unlock Task-Centric Latent Actions** ([2601.22714](https://arxiv.org/html/2601.22714v1)) | 2026-01 | 仅"提示 VLM 忽略干扰物"即把下游成功率提升至多 **6×**。 |
| **HiLAM** ([2603.05815](https://arxiv.org/pdf/2603.05815)) | 2026-03 | 层级潜在动作：**10% demo → 45%；50% → 84%**（≈全量基线）。 |

**趋势 / Trends.** ① 全场收敛到上面那一条配方；②"VLA→ViLLA"成主流生产架构（GO-1 / villa-X）；③ 潜在动作码本≈"学到的动作词表"（UniAct/UniVLA），更好的 tokenizer（残差 VQ）可量化提升；④ 跨具身是*显式目标*（人手视频→机器人已常规可达）；⑤**2025 是失败模式的清算年**，干净基准的成功在真实视觉杂乱下不成立；⑥ 修法 2025–2026 快速落地（DINO 语义空间学 LAM / 语言-VLM 屏蔽 / 光流目标 / 早注入少量标注）；⑦ 世界模型与潜在动作两线合流（LAWM 2025-09 通过世界建模学潜在动作）。
*The field converged on one recipe; "VLA→ViLLA" is now dominant; latent-action codebooks are treated as a learned "action vocabulary"; cross-embodiment is the explicit goal; 2025 was the failure-mode reckoning (clean-benchmark wins don't survive real clutter); cheap fixes landed fast (DINO-space LAM, VLM masking, optical-flow targets, early 2.5% labels); world-model and latent-action lines are merging.*

**关键数据效率数字 / Hard data-efficiency numbers.** UniVLA：1/10 下游标注数据即超 OpenVLA；HiLAM：10% demo→45%；干扰物机制下 2.5% 标注→4.3×（但仅恢复约一半的全标注 BC 性能）。**净结论：规划"小但非零"的标注集（量级：几百条标注轨迹，或几个百分比的帧标注），而非零。** "纯游戏视频零样本上真机"无证据支持。
*Net: plan for a small-but-nonzero labeled set (hundreds of trajectories, or a few % of frames), not zero. "Zero-shot to a robot from pure game video" is unsupported.*

**与 thesis 关联 / Relevance：MAXIMUM.** 本路线设定的数据（大规模无标注交互/游戏录屏、无动作标注、目标=具身控制+小真机集）正好映射到 LAPA/UniVLA/GR00T 模板与 VPT/Genie 的游戏视频谱系。完整应用配方与风险见本 bundle 的 `training_plan.md` / `robotics_transfer.md`。

### §5.1 深读校准（2026-06）/ Deep-read calibration

**中文.** 对本节核心论文（VPT / LAPA / UniVLA / Dreamer 4 / V-JEPA 2-AC / Genie 及"潜在动作失败"线）做了原文级深读，三条横跨结论值得单列：

1. **"需要多少标注"四篇独立收敛到 ~50–100h（而非零、非数千）**：VPT 自述 1962h 过量、~100h 是经验拐点（<50h 技能不涌现）；Dreamer 4 ~100h 标注（~4%）即满额动作 grounding、10h→53% 且能外推到无标注区；LAPA 真机 gap-bridge ~150 demo/skill；失败线 2.5% 标注"早注入"→4.2×。**一份小标注集"一物两用"**：训 robust 的监督 IDM（VPT 式，给真·可解码动作空间）+ 当稳住无监督 LAM 的早期监督——把"最坏数据上的纯无监督"转成唯一有证据 work 的"半监督"。
2. **抗干扰栈（按杠杆）**：早标注 2.5–5% ＞ 光流/外生鲁棒目标（DPFlow，无标注）＞ DINOv2 特征空间 LAM + 语言/caption 条件（UniVLA；task-irrelevant-only 消融崩到 0.2% 即证据）＞ 剔除过场 + future-leakage 探针门。
3. **V-JEPA 2-AC 的细则**：它**用真·本体感（7D 末端位姿 delta），不是 latent action**，并需"部署动作空间里的 action-paired 数据"（≤62h 真机）。即"潜在视频世界模型→真机"的*控制环*（latent-space CEM/MPC、16s/动作）可直接复用，但"无标注视频→潜在动作"这一步是它 assume away 的、仍是开放研究。

**诚实天花板**：干扰物视频学的潜在动作只恢复 ~半（0.44）的全标注 BC；跨"渲染域→真机"的迁移在公开文献里**未被证明**（LAPA 只证人手→机器人）。潜在动作是去风险工具，不是标注替代品。

**English.** Full-paper deep reads of this section's core works yield three cross-cutting conclusions: **(1) "how much labeling" converges on ~50–100h** across VPT (~100h knee; 1962h overkill), Dreamer 4 (~100h/4% for full action grounding; 10h→53%, extrapolates to unlabeled regions), LAPA (~150 demos/skill), and the failure-line (2.5% *early* labels → 4.2×) — and a single small labeled set is **dual-use** (trains a robust supervised IDM *and* stabilizes an unsupervised LAM), turning "pure-unsupervised on worst-case data" into the only regime with evidence of working. **(2) Distractor-suppression stack** (by leverage): early 2.5–5% labels ＞ optical-flow / exogenous-robust targets (DPFlow, label-free) ＞ DINOv2-feature LAM + language/caption conditioning (UniVLA) ＞ cutscene exclusion + a future-leakage probe. **(3) V-JEPA 2-AC uses real proprioception (7-D end-effector deltas), not latent actions**, and needs action-paired data in the deployment action space (≤62h robot) — its latent-space CEM/MPC control loop is directly reusable, but the "unlabeled-video → latent-action" step is assumed away and remains open. **Honest ceiling:** latent actions from distractor-heavy video recover only ~half (0.44) of fully-labeled BC; rendered-domain→real-robot transfer is unproven in public literature.

---

## §6. 数据、评测、架构与产业 / Data, Evaluation, Architectures & Industry

### 6.1 数据集 / Datasets

| Name | Type | Scale | Access / IP | Used by |
|---|---|---|---|---|
| **Ego-Exo4D** | paired ego+exo human-skill video (+audio/gaze/IMU/3D) | ~1,422 h, 800+ participants, 13 cities | public; **consented** (low IP risk) | egocentric perception ([2311.18259](https://arxiv.org/abs/2311.18259)) |
| **Open X-Embodiment** | federated real-robot manip | **>1M episodes, 22 embodiments**, 527 skills | open (mixed per-dataset licenses) | RT-X, OpenVLA, most VLAs ([2310.08864](https://arxiv.org/abs/2310.08864)) |
| **DROID** | in-the-wild Franka manip | 76k demos, **350 h**, 564 envs, 13 insts | open (RLDS) | **V-JEPA 2-AC post-train (≤62h subset)** ([2403.12945](https://arxiv.org/abs/2403.12945)) |
| **Bleeding Edge** | game frames + controller actions | **>1B image-action pairs ≈ 7 yrs play**; 27,990 players | **proprietary; first-party (clean IP)**; only WHAM weights+sample open | WHAM/Muse ([Nature](https://www.nature.com/articles/s41586-025-08600-3)) |
| **VPT / MineRL web video** | scraped Minecraft YouTube + IDM pseudo-labels | ~270k h → ~70k h "clean"; 2k h labeled | **scraped web video — IP/ToS gray zone** | VPT ([2206.11795](https://arxiv.org/abs/2206.11795)) |
| **NVIDIA Cosmos corpus** | curated real-world (human/robot/driving) | **20M h → ~9,000T tokens** | models open; **corpus withheld** | Cosmos ([2501.03575](https://arxiv.org/abs/2501.03575)) |
| **Internet video (V-JEPA 2)** | generic web video, action-free | **>1M h** | mixed/undisclosed | V-JEPA 2 ([2506.09985](https://arxiv.org/abs/2506.09985)) |

> **要点 / Key point.** 最干净的语料是**一方自有游戏遥测**（Bleeding Edge）或**已授权采集**（Ego-Exo4D）；爬来的网络视频（VPT、Cosmos/V-JEPA 部分预训练）都在 ToS/版权灰区——这正是 Cosmos/V-JEPA **开权重却不开语料**的原因。*The cleanest corpora are first-party telemetry (Bleeding Edge) or consented capture (Ego-Exo4D); scraped web video sits in a ToS/copyright gray zone — why Cosmos/V-JEPA open weights but withhold the corpus.*

### 6.2 评测 / Evaluation

| Name | Measures | Note | Link |
|---|---|---|---|
| **FVD** | distributional video realism | **known-broken**: non-Gaussian, temporal-insensitive, dominated by per-frame quality | — |
| **JEDi** | FVD replacement (V-JEPA feats + MMD) | ~16% of samples for comparable reliability; better human-correlation | [2410.05203](https://arxiv.org/abs/2410.05203) |
| **Physics-IQ** | physical prediction (fluids/optics/solids…) | 396 **real** videos; **realism ≠ physical understanding** | [2501.09038](https://arxiv.org/abs/2501.09038) |
| **VideoPhy / -2** | physical commonsense in T2V | best model ~22% joint adherence on hard subset | [2503.06800](https://arxiv.org/abs/2503.06800) |
| **WorldModelBench** | judges video gens *as world models* | 7 domains, physical-adherence criteria; frequent violations | [2502.20694](https://arxiv.org/abs/2502.20694) |
| **WorldSimBench** | perceptual **+ manipulative** eval | do generated videos yield correct *control signals*? | [2410.18072](https://arxiv.org/abs/2410.18072) |
| **1X World Model Challenge** | real-humanoid future-frame / latent prediction | "evaluating bits, not atoms" | [PDF](https://www.1x.tech/1x-world-model.pdf) |

**一句话 / In one line.** 像素指标测不出动力学；**下游控制成功率是唯一被认可的"世界模型级"评测**（WorldSimBench/1X-Challenge 即朝此走）；报分布质量请用 JEDi 不用 FVD。
*Pixel metrics miss dynamics; downstream control success is the only accepted "world-model-grade" test; use JEDi over FVD for any distributional number.*

### 6.3 架构与规模 / Architectures & scaling

**三范式 / Three paradigms.** ① **自回归 Transformer + 视频 tokenizer**（Genie 2/3、WHAM；tokenizer 是杠杆——MAGVIT-v2 的"无查找量化 LFQ"催生"LM 击败扩散，tokenizer 是关键"，[2310.05737](https://arxiv.org/abs/2310.05737)）；② **潜在扩散**（GAIA-2、Cosmos-Predict、多数驾驶世界模型）；③ **JEPA 潜在预测（非生成）**（V-JEPA 2，经 V-JEPA 2-AC 接控制）。**Cosmos Tokenizer** 达 8× 总压缩/12× 提速、最高 2048×，是任何视频管线可直接复用的部件。
*AR-transformer + video tokenizer (Genie/WHAM; the tokenizer is the lever — MAGVIT-v2's LFQ enabled "LM beats diffusion, tokenizer is key"); latent diffusion (GAIA-2, Cosmos-Predict); JEPA latent-prediction (V-JEPA 2). The Cosmos tokenizer (up to 2048× compression) is reusable infra.*

**算力锚点 / Compute anchors.** WHAM-1.6B = **98×H100×5天**（≈1.2万 H100·时；图像 300×180、>10亿图-动作对；"98×5d"源自 Nature 论文经二手转述，微软官方仅称"~100 GPU"）；VPT = 0.5B / 720×V100×9天；V-JEPA 2 = 无动作预训练 >100万小时 → AC 后训 <62h。**Scaling 警示**：尚无干净的"视频世界模型→控制目标"scaling law；"物理定律视角"工作（Kang et al., [2411.02385](https://arxiv.org/abs/2411.02385)）证明**仅靠 scale 无法恢复物理定律**，组合/OOD 泛化会失败。
*WHAM-1.6B ≈ 98×H100×5d (≈12k H100-h; "98×5d" is paper-sourced via secondary reporting, MS only says "~100 GPUs"). VPT = 0.5B / 720×V100×9d. No clean video-WM scaling law to a control objective; Kang et al. show scaling alone can't recover physical laws (combinatorial/OOD generalization fails).*

### 6.4 产业格局 2025–2026 / Industry landscape

**中文.** 2026 Q1 一个季度 **>$20 亿**涌入世界模型创业。主要玩家：**DeepMind**（Genie 3，2026-01 消费级 Project Genie）；**World Labs**（李飞飞，"空间智能/大世界模型"，Marble 2025-11，融资 **$1B**）；**NVIDIA Cosmos**（开源平台，物理 AI 的合成数据底座）；**微软**（Muse/WHAM，*Nature* 2025-02，开权重）；**Meta**（V-JEPA 2；LeCun 2025-12 出走创 AMI Labs，见 §9）；**Wayve**（GAIA-1→3，把世界模型推向安全验证）；**Decart**（Oasis；~$4B 估值，Oasis 3 照片级驾驶 @$0.02/秒）；**Runway**（GWM-Worlds/Robotics/Avatars，$5.3B）；**Luma**（~$4B）；**1X**（人形数字孪生 + 策略评测）。**大势：世界模型的兑现正从"生成"转向"合成数据 + 策略评测"。**
**English.** >$2B into world-model startups in Q1 2026. Key players: DeepMind (Genie 3 → consumer Project Genie Jan 2026); World Labs (Fei-Fei Li, "spatial intelligence", Marble Nov 2025, **$1B**); NVIDIA Cosmos (open platform); Microsoft (Muse/WHAM, Nature 2025); Meta (V-JEPA 2; LeCun left to found AMI Labs Dec 2025 — see §9); Wayve (GAIA-1→3, pushing WMs toward safety validation); Decart (Oasis, ~$4B); Runway (GWM, $5.3B); Luma (~$4B); 1X (humanoid digital twin + policy eval). **The payoff is shifting from generation to synthetic-data + policy evaluation.**

**开放问题/批判 / Open problems & critiques.** 视频生成≠真世界模型（共识批判，画面真实与物理正确*弱相关*）；scale≠物理；长程漂移；评测有效性危机；算力成本；数据版权；相关 vs 因果。
*Video gen ≠ true world model (realism weakly correlated with physics); scale ≠ physics; long-horizon drift; eval-validity crisis; compute cost; data rights; correlation vs causation.*

## §8. 参考文献 / References

*Verified primary sources (arXiv IDs exact unless flagged in §9). Grouped by section.*

**Foundations & MBRL (§1).**
Ha & Schmidhuber, *World Models* [1803.10122](https://arxiv.org/abs/1803.10122) · PlaNet [1811.04551](https://arxiv.org/abs/1811.04551) · DreamerV2 [2010.02193](https://arxiv.org/abs/2010.02193) · MuZero [1911.08265](https://arxiv.org/abs/1911.08265) · EfficientZero [2111.00210](https://arxiv.org/abs/2111.00210) · TD-MPC2 [2310.16828](https://arxiv.org/abs/2310.16828) · DayDreamer [2206.14176](https://arxiv.org/abs/2206.14176) · Diffuser [2205.09991](https://arxiv.org/abs/2205.09991) · IRIS [2209.00588](https://arxiv.org/abs/2209.00588) · DreamerV3 [2301.04104](https://arxiv.org/abs/2301.04104) / [Nature 2025](https://www.nature.com/articles/s41586-025-08744-2) · DIAMOND [2405.12399](https://arxiv.org/abs/2405.12399) · Dreamer 4 [2509.24527](https://arxiv.org/abs/2509.24527)

**Game world models (§2).**
Genie [2402.15391](https://arxiv.org/abs/2402.15391) · Genie 2 [blog](https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/) · Genie 3 [blog](https://deepmind.google/blog/genie-3-a-new-frontier-for-world-models/) · Project Genie [blog](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/project-genie/) · GameNGen [2408.14837](https://arxiv.org/abs/2408.14837) · Oasis [site](https://oasis-model.github.io/) · WHAM/Muse [Nature](https://www.nature.com/articles/s41586-025-08600-3) · WHAMM [MSR](https://www.microsoft.com/en-us/research/articles/whamm-real-time-world-modelling-of-interactive-environments/) · The Matrix [2412.03568](https://arxiv.org/abs/2412.03568) · Matrix-Game [2506.18701](https://arxiv.org/abs/2506.18701) · Yan [site](https://greatx3.github.io/Yan/) · GameGen-X [2411.00769](https://arxiv.org/abs/2411.00769) · Mirage 2 [decoder](https://the-decoder.com/mirage-2-allows-users-to-turn-sketches-and-photos-into-interactive-game-worlds/) · Runway GWM-1 [news](https://mlq.ai/news/runway-launches-gwm-1-world-model-with-real-time-interaction-capabilities/)

**Video & JEPA (§3).**
I-JEPA [2301.08243](https://arxiv.org/abs/2301.08243) · V-JEPA 2 / -AC [2506.09985](https://arxiv.org/abs/2506.09985) · Cosmos platform [2501.03575](https://arxiv.org/abs/2501.03575) · Cosmos Tokenizer [GitHub](https://github.com/NVIDIA/Cosmos-Tokenizer) · Cosmos 3 [report](https://research.nvidia.com/labs/cosmos-lab/cosmos3/technical-report.pdf) · Veo-3 zero-shot reasoners [2509.20328](https://arxiv.org/abs/2509.20328) · Physics-IQ [2501.09038](https://arxiv.org/abs/2501.09038) · VideoPhy-2 [2503.06800](https://arxiv.org/abs/2503.06800) · Marble [TechCrunch](https://techcrunch.com/2025/11/12/fei-fei-lis-world-labs-speeds-up-the-world-model-race-with-marble-its-first-commercial-product/)

**Embodied & driving (§4).**
UniSim [2310.06114](https://arxiv.org/abs/2310.06114) · GR00T N1 [2503.14734](https://arxiv.org/abs/2503.14734) · RoboDreamer [2404.12377](https://arxiv.org/abs/2404.12377) · iVideoGPT [2405.15223](https://arxiv.org/abs/2405.15223) · WorldVLA [2506.21539](https://arxiv.org/abs/2506.21539) · 1X World Model [PDF](https://www.1x.tech/1x-world-model.pdf) · GAIA-1 [2309.17080](https://arxiv.org/abs/2309.17080) · GAIA-2 [2503.20523](https://arxiv.org/abs/2503.20523) · GAIA-3 [Wayve](https://wayve.ai/thinking/gaia-3/) · DriveDreamer [2309.09777](https://arxiv.org/abs/2309.09777) · DriveDreamer-2 [2403.06845](https://arxiv.org/abs/2403.06845) · Vista [2405.17398](https://arxiv.org/abs/2405.17398) · OccSora [2405.20337](https://arxiv.org/abs/2405.20337) · OpenVLA [2406.09246](https://arxiv.org/abs/2406.09246) · π0.5 [blog](https://www.pi.website/blog/pi05)

**Latent action (§5).**
VPT [2206.11795](https://arxiv.org/abs/2206.11795) · LAPO [2312.10812](https://arxiv.org/abs/2312.10812) · LAPA [2410.11758](https://arxiv.org/abs/2410.11758) · Moto [2412.04445](https://arxiv.org/abs/2412.04445) · ATM [2401.00025](https://arxiv.org/abs/2401.00025) · Track2Act [2405.01527](https://arxiv.org/abs/2405.01527) · AgiBot World/GO-1 [2503.06669](https://arxiv.org/abs/2503.06669) · UniVLA [2505.06111](https://arxiv.org/abs/2505.06111) · UniSkill [2505.08787](https://arxiv.org/abs/2505.08787) · villa-X [2507.23682](https://arxiv.org/abs/2507.23682) · UniAct [CVPR'25](https://openaccess.thecvf.com/content/CVPR2025/papers/Zheng_Universal_Actions_for_Enhanced_Embodied_Foundation_Models_CVPR_2025_paper.pdf) · LAWM [2509.18428](https://arxiv.org/abs/2509.18428) · *Distractors require supervision* [2502.00379](https://arxiv.org/abs/2502.00379) · *(2026, verify §9)* Why Latent Actions Fail [2605.20223](https://arxiv.org/abs/2605.20223), VLMs Unlock Task-Centric LA [2601.22714](https://arxiv.org/abs/2601.22714), HiLAM [2603.05815](https://arxiv.org/abs/2603.05815), Olaf-World [2602.10104](https://arxiv.org/abs/2602.10104)

**Data, eval, scaling (§6).**
Ego-Exo4D [2311.18259](https://arxiv.org/abs/2311.18259) · Open X-Embodiment [2310.08864](https://arxiv.org/abs/2310.08864) · DROID [2403.12945](https://arxiv.org/abs/2403.12945) · JEDi [2410.05203](https://arxiv.org/abs/2410.05203) · WorldModelBench [2502.20694](https://arxiv.org/abs/2502.20694) · WorldSimBench [2410.18072](https://arxiv.org/abs/2410.18072) · MAGVIT-v2 [2310.05737](https://arxiv.org/abs/2310.05737) · *How Far is Video Generation from World Model (Physical Law)* [2411.02385](https://arxiv.org/abs/2411.02385) · Ego4D [2110.07058](https://arxiv.org/abs/2110.07058)

---

## §9. 不确定性与待核实项 / Uncertainty & items to re-verify

*调研代理逐条标注的低置信项；正式对外引用前请复核。/ Low-confidence items flagged by the research agents; re-verify before any external citation.*

- **WHAM「98×H100×5天」** 来自 Nature 论文经二手转述；微软官方博客仅称"~100 GPU/H100"。高置信但非官方复述。
- **LeCun 离开 Meta 创办 AMI Labs（2025-12）** 被广泛报道；**融资数字各源差异大**（€500M / $1.03B / $3–3.5B 估值）——按"约数"处理，待一手确认。
- **Cosmos 3**（2026-06）的参数量、"leading physics accuracy" 等为 **NVIDIA 自述/厂商口径**，非独立基准；细节在搜索时仍偏薄。
- **2026 年潜在动作新作的 arXiv ID**（Why Latent Actions Fail `2605.20223`、VLMs Unlock `2601.22714`、HiLAM `2603.05815`、Olaf-World `2602.10104`）及若干 2026 评测基准（WorldArena `2602.08971`、WBench `2605.25874`、PhyWorld/PhyGround `2605.*`）均为**代理报告、晚于知识截止**，**正式引用前请逐一核对 ID 与内容**。
- **更未核实的潜在动作线索（仅作追踪）**：LatBot `2511.23034`、LAOF（光流）`2511.16407`、ConLA `2602.00557`、VLA-JEPA `2602.10098`、Co-Evolving LA World Models `2510.26433`、StaMo `2510.05057`。
- **「Odyssey」「Lucid」/ Luma 游戏世界产品**：未独立证实/可能与 Mirage 等混淆——需定向复核。
- **Tesla 世界模型表态**：未找到可引用的一手、带日期来源——**宁缺勿造**；驾驶世界模型的可靠范例用 Wayve(GAIA)/NVIDIA(Cosmos)。
- **「GenAD」** 指代 ≥2 篇不同的 2024 论文（一篇驾驶世界模型、一篇端到端生成式规划）——引用前先消歧。
- **Genie 2/3 内部架构**：DeepMind 未发技术论文，"Genie 3 用潜在动作"为**谱系推断**而非文档化规格。
- **Physics-IQ 各模型数值分**在全文/项目页，不在所取摘要。
- **DROID = 350h 全量；V-JEPA 2-AC 用的是其 ~62h 单臂 Franka 子集**——引用"62h"时注明是子集。

---

*End of report — public, generalised edition.*
