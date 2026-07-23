# Olaf-World: Orienting Latent Actions for Video World Modeling (arXiv 2602.10104) — Deep Read

> Deep-dive note · **VERIFIED real** (≥5 sources: arXiv, github.com/showlab/Olaf-World, project page, alphaXiv, HF Papers): Jiang, Gu, Tsang, Shou (Show Lab, NUS), v1 2026-02-10 / v2 2026-05-26. Confidence: existence + mechanism **high**; exact numbers **medium** (single HF-papers extraction; full PDF too large to re-confirm every digit). Compiled 2026-06-29. See survey §5/§9. **Directly solves our biggest unproven risk: latent-action TRANSFER (game→robot).**

## 1) The transfer-failure problem (precise)
LAMs infer `a_t` from `(x_t, x_{t+1})` so a forward model reconstructs `x_{t+1}`. That objective is **per-clip + purely predictive**, causing two named failures:
- **Shortcut learning** — the latent absorbs *whatever* predicts the next frame, incl. exogenous scene/camera/background/parallax motion. Avatar motion and camera pan get entangled in one code.
- **Cross-context non-identifiability** — each clip/env gets its *own* latent coordinate frame; "move right" in scene A vs B map to unrelated latent vectors (nothing ties action semantics across contexts). **No shared coordinate system → a controller learned in one context doesn't transfer.** This is exactly the embodiment-gap blocker: a code trained on game-avatar video means nothing in robot-camera context.

## 2) The fix — SeqΔ-REPA (precise)
**Insight:** actions are unobserved, but their *effects* are observable and context-agnostic → use effects as a shared anchor.
- **Target:** a **frozen self-supervised video encoder — V-JEPA 2 (ViT-Giant/16)** — embeds frames; the "effect" = **temporal feature difference** `Δφ = φ(x_{t+k}) − φ(x_t)` over a window (sequence-level, not single-step).
- **Prediction:** the **integrated latent action** (aggregated/summed per-step latents over the same window).
- **Loss:** a **REPA-style representation-alignment** (cosine) forcing the integrated latent-action trajectory to point the same direction as `Δφ`. Added to the standard LAM/world-model objective.

**Why it disentangles:** V-JEPA-2 features encode semantic scene *change* in a representation **shared across scenes/viewpoints**. Anchoring to `Δφ` rewards the latent for capturing the *effect that generalizes* ("character advanced") over the pixel shortcut ("these background pixels shifted"); sequence-level integration prevents per-step camera jitter from being encoded; the shared encoder supplies the **missing common coordinate frame** → diagonal-dominant action-prototype similarity across first→third-person.
**Pipeline:** LAM (inverse-dynamics + β-VAE-style latent) → world model = **SkyReels-V2-1.3B I2V DiT** conditioned on latents, pretrained on **MiraData** (3D-render + city-walking).

## 3) Results (medium confidence on exact digits)
Eval: **MIND** (cross-context linear probing, Macro-F1), VBench, **RPE** (Relative Pose Error: fixed action seq → generate → re-estimate camera traj with **ViPE** → vs GT; lower = more faithful control). Baselines: **AdaWorld, DirectAct**.
- **Cross-context linear probing (Macro-F1):** in-domain 1ST-P **0.8138 vs AdaWorld 0.6004**; **cross-domain 1ST→3RD-P 0.6250 vs 0.4820**.
- **Adaptation budget (RPE-Trans, lower better):** 0 labels **0.0387 vs 0.0470**; **~1 min labeled 0.0284 vs 0.0318**; 50 videos **0.0230 vs 0.0263**.
- **OOD novel scenes:** RPE-Trans **0.0478**, lowest among methods. Olaf-World is **lowest-RPE in every reported setting**.
- **Code:** LAM weights released Apr 2026; WM pretraining/eval code was still TODO.

## 4) FOR OUR PATH (game-video → robot)
Our current LAM (DINO-space + optical-flow) has exactly the entanglement weakness this targets. **Optical flow is *especially* prone to the shortcut** (it fires on camera pan / background scroll, not just avatar control). Olaf-World is the transfer fix — and uses **the same V-JEPA-2 encoder family we already bet on**, so it slots in.

**Concrete additions beyond DINO + flow:**
1. **Add an effect-alignment head against a frozen V-JEPA-2 encoder.** Compute sequence-level `Δφ`, add a REPA cosine loss tying the *integrated* latent action to `Δφ`. **Single highest-leverage change for transfer** (the 4th hardening move, on top of DINO-space + early-labels + optical-flow).
2. **Integrate latents over a window, not per-frame; supervise sequence-level effect.** Per-step codes overfit camera jitter — distractor-heavy *screen* video is worse than their game footage.
3. **Hold out the cross-context probe as the TRANSFER gate.** Their real evidence is cross-domain Macro-F1 + RPE-after-~1-min-adaptation, **not** reconstruction. Adopt: train LAM on game avatar, freeze, linear-probe / few-shot adapt (~1 min labels) on robot-camera clips, measure RPE/Macro-F1 transfer. **Reconstruction looking good means nothing here.**

**3 takeaways:** (1) **Verified real** (Show Lab NUS); mechanism well-corroborated, numbers single-sourced. (2) The transfer fix = **effect-alignment to a frozen V-JEPA-2 temporal Δφ** — same encoder family as our control stack, slots straight in. (3) **Flow alone won't transfer; add the Seq-Δ effect-alignment loss and measure with a cross-context probe**, not pixel/feature reconstruction. → adds a **second acceptance gate** (transfer) beyond the within-context future-leakage probe.

**Sources:** [arXiv 2602.10104](https://arxiv.org/abs/2602.10104) · [GitHub](https://github.com/showlab/Olaf-World) · [project](https://showlab.github.io/Olaf-World/). *Flag: exact result digits single-sourced (HF papers); mechanism/existence high-confidence.*
