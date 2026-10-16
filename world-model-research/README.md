---
license: cc-by-4.0
tags:
  - world-models
  - robotics
  - research-notes
  - survey
---

# World Model Research Notes

> A living research knowledge base on **world models** — from gameplay/video data to robot control.
> Maintained by **Diogenes Lab** / **Oratis**.

This repo collects our running survey of the world-model literature and the methods most relevant to
learning interactive world models from gameplay/video and transferring them to robot autonomy.

## Contents

| File | What it is |
|------|-----------|
| [`world_models_survey.md`](world_models_survey.md) | SOTA survey (2024–2026): the four paradigms (autoregressive / diffusion / JEPA-latent / world-action), per-model deep dives (WHAM, V-JEPA 2, Genie 3, Cosmos, GameNGen/DIAMOND/Oasis, Dreamer…), open problems. |
| [`papers.md`](papers.md) | Annotated reading list with arXiv links, grouped and flagged (must-read / robotics / game-data). |
| [`latent_action_cross_embodiment.md`](latent_action_cross_embodiment.md) | Deep dive on **latent action** & cross-embodiment transfer (LAPA, Genie LAM, UniSkill, Latent Action Diffusion, V-JEPA 2-AC) — the bridge from unlabeled gameplay/video to robot actions. |
| [`training_plan.md`](training_plan.md) | Our staged training approach — VQ tokenizer → autoregressive world model (WHAM-style) → latent-action + controllable latent dynamics → robot transfer. Architecture choices, eval, compute anchors. |
| [`robotics_transfer.md`](robotics_transfer.md) | Three routes from a world model to robot autonomy (action-conditioned planning + MPC / representation backbone / dreamed policy training), the embodiment gap, and a recommended path. |
| [`world_model_benchmarks.md`](world_model_benchmarks.md) | Catalog of world-model benchmarks (2024–2026) across 6 categories — unified world-generation (WorldScore), physical reasoning (Physics-IQ, VideoPhy), action controllability (ACT-Bench), embodied/robotics (EWMBench, RoboWM-Bench), model-based RL (Atari 100k, DMC), and cross-cutting metrics. |

## Notes

- This is a **curated public subset** of a larger internal research effort. Product-specific and
  operational details are intentionally not included; the focus here is the general method and survey.
- Sources are cited inline (arXiv IDs are the stable anchors). Last refreshed **2026-06**.
- Updated periodically — a weekly tracker appends newly published, relevant papers to `papers.md`.

## License

Text released under **CC BY 4.0**. Cited papers belong to their respective authors.
