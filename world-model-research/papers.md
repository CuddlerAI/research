# World Model 论文 / 资源清单（带注释）

> 配合 [`world_models_survey.md`](world_models_survey.md) 用。★ = 必读，◆ = 与机器人迁移强相关，▣ = 与「从游戏/视频数据学」强相关。
> 维护方式：新论文追加到对应分组，注明日期与一句话「对我们的用处」。可设每周 routine 自动追新（见 [`../README.md`](README.md) §6）。

## A. 直接对标（先例）
- ★▣ **WHAM / Muse** — *World and Human Action Models towards gameplay ideation*，Microsoft + Ninja Theory，**Nature 2025**。
  HF: https://huggingface.co/microsoft/wham ｜ blog: https://www.microsoft.com/en-us/research/blog/introducing-muse-our-first-generative-ai-model-designed-for-gameplay-ideation/
  → 用处：**数据格式/规模/算力的直接模板**（VQ-GAN + decoder-only transformer，10Hz `(obs,action)`，1.6B@98×H100×5d）。
- ▣ **WHAMM!** — 实时世界建模。https://www.microsoft.com/en-us/research/articles/whamm-real-time-world-modelling-of-interactive-environments/
  → 用处：当我们要把世界模型做成「可实时玩/可实时控制」时的参照。

## B. 机器人迁移（最关键）
- ★◆ **V-JEPA 2 / V-JEPA 2-AC** — Meta，arXiv:**2506.09985**。https://arxiv.org/abs/2506.09985
  → 用处：视频世界模型 + ~62h 真机数据 → 零样本 Franka 控制（MPC）。**我们机器人路线的主范本。**
- ◆ **NVIDIA Cosmos**（Predict/Transfer/Reason, Cosmos 3 2026-06）。https://www.nvidia.com/en-us/ai/cosmos/
  → 用处：合成数据扩增 / 真机仿真 / 「世界模型当模拟器训策略」的工业级方案。
- ◆ **World-Action Models（WAM）综述资源** — Awesome-WAM。https://github.com/OpenMOSS/Awesome-WAM
  → 用处：GR-1/2、WorldVLA、RynnVLA、Cosmos Policy、HMA 等机器人世界-动作模型的活跃清单。
- ◆ **DreamerV3** — *Mastering Diverse Domains through World Models*，2023。
  → 用处：在隐想象中做 model-based RL 的标杆；「梦里训策略」路线的代表。

## C. 解「具身 gap」：从无标注视频学动作
- ★▣◆ **LAPA** — *Latent Action Pretraining from Videos*，arXiv:**2410.11758**。https://arxiv.org/abs/2410.11758
  → 用处：VQ-VAE 学隐动作 → 少量真机数据映射到真实动作。**把游戏交互场景无标注录屏也用上的关键。**
- ▣ **VideoWorld** — *Exploring Knowledge Learning from Unlabeled Videos*，arXiv:2501.09781。
- ◆ **UniSkill / VLA-JEPA / ACT-JEPA** — 跨具身技能表征、JEPA 隐世界模型接 VLA、JEPA 策略表征。

## D. 可玩 / 可交互世界模型（范式与评测直觉）
- ★ **Genie 3** — Google DeepMind，2025-08。https://deepmind.google/blog/genie-3-a-new-frontier-for-world-models/
  → 用处：实时可交互 SOTA；一致性/可控性/时长的评测直觉；Genie 的 latent action model。
- **GameNGen** — *Diffusion Models Are Real-Time Game Engines*，arXiv:2408.14837。https://arxiv.org/html/2408.14837v2
- **DIAMOND** — 扩散世界模型 for RL（NeurIPS 2024 Spotlight）。
- **Oasis** — 实时 Minecraft 世界模型。https://oasis-model.github.io/
- **MineWorld**（arXiv:2504.08388）/ **Matrix-Game**（arXiv:2506.18701）/ **GameGen-X** — 开源/开放世界可交互生成。

## E. 奠基 / 坐标
- **World Models** — Ha & Schmidhuber，2018。https://worldmodels.github.io/ → 一切的起点（VAE+RNN+在梦里训控制器）。
- **Sora: Video generation models as world simulators** — OpenAI，2024。→ 把话题推向主流（偏生成、可控性弱）。

## F. 综述（建坐标系优先读这几篇）
- ★ **A Comprehensive Survey on World Models for Embodied AI** — arXiv:**2510.16732**。https://arxiv.org/abs/2510.16732
- **World Model for Robot Learning: A Comprehensive Survey** — https://ntumars.github.io/wm-robot-survey/
- **World Models for Robotic Manipulation: A Survey** — arXiv:2606.00113。
- 资源墙：**awesome-world-model-games** https://github.com/dweam-team/awesome-world-model-games

---
*首版 2026-06-29。链接可能失效，arXiv 号是更稳的检索锚。*
