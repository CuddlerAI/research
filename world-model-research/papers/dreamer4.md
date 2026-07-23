# Dreamer 4 — "Training Agents Inside of Scalable World Models" (arXiv 2509.24527, DeepMind, 29 Sep 2025) — Deep Read

> Deep-dive note · read from the actual PDF in full (body pp.1–18); numbers verified against the primary source, cross-checked vs secondary. Compiled 2026-06-29. See survey §1/§7. **The closest single proof-of-concept of our whole thesis.**

*Hafner\*, Yan\*, Lillicrap, Google DeepMind.*

## 1) Problem & core idea
World models learn general knowledge from video and let you train behaviors *in imagination* (offline, no live env) — key for robotics where online interaction is "unsafe and slow." Prior split: compact RL world models (DreamerV3, fast/accurate, can't fit complex distributions) vs scalable controllable video models (Genie 3, rich but miss precise physics, many GPUs). Dreamer 4: one **scalable yet real-time** world model that (a) predicts object interactions accurately, (b) learns most knowledge from **unlabeled** video + only a *small* action-labeled slice, (c) trains a policy purely by RL in imagination. Headline: **first agent to obtain diamonds in Minecraft purely from offline data**, beating VPT's offline agent with **100× less data**.

## 2) Method — precise
**Architecture (§3, Fig. 2).** Two components share one **block-causal 2D transformer** (separate space-only & time-only attention; temporal attn every 4 layers; QK-norm, RoPE, SwiGLU, GQA, attn soft-capping).
- **Causal tokenizer:** masked-autoencoder reconstruction (MSE + 0.2·LPIPS), encoder dropout p∼U(0,0.9); **low-dim projection + tanh bottleneck**; causal-in-time so frames decode one-by-one.
- **Interactive dynamics:** operates on the *interleaved* sequence of action tokens, a shortcut **(τ signal-level, d step-size)** token, and tokenizer reps; denoises via shortcut forcing. **When a clip is unlabeled, only a learned action embedding is used** — the literal switch that lets unlabeled video flow through the same model.

**Shortcut forcing (key objective).** Combines *diffusion forcing* (per-timestep noise levels) + *shortcut models* (conditioned on step-size d; finest-d flow-matching + larger-d **self-consistency bootstrap** distilling two half-steps). Two twists: (i) **x-prediction** (predict clean reps) not v-prediction → stable arbitrary-length rollouts; (ii) ramp loss weight `w(τ)=0.9τ+0.1`. **Why real-time on 1 GPU:** step-size conditioning → only **K=4 sampling steps/frame** vs 64 → **16× speedup** at matched quality.

**Imagination training — 3 phases (Algorithm 1):**
- **Phase 1 — World-model pretraining:** tokenizer, then dynamics on tokenized video *and optionally actions*.
- **Phase 2 — Agent finetuning:** insert **agent/task tokens** as a new modality; policy+reward MLP heads (multi-token, L=8). Agent tokens attend to everything but **nothing attends back** → prevents causal confusion (futures driven by *actions*, not task label).
- **Phase 3 — Imagination RL:** roll out the **frozen** transformer with its policy; reward head (symexp twohot), value via TD-λ (γ=0.997); policy via **PMPO** (sign-of-advantage RL). No environment interaction — RL runs *inside* the model.

**Scale/speed:** **2B params = 400M tokenizer + 1.6B dynamics**, 256–1024 TPU-v5p. **21.4 FPS on a single H100**, context **9.6 s** (6× prior).

## 3) Data & task
**Dataset:** OpenAI **VPT contractor data** — **2541 hours**, 360p, mouse+keyboard @20 FPS, event-annotated. **Labeled vs unlabeled:** all 2541 h used as video; the action-grounding study provides actions for only **0/10/100/1000/2541 h** subsets. **Diamond task:** raw pixels + low-level mouse (121-way) & keyboard (23 binary), crafting via in-game UI; 60-min episodes from empty inventory. Diamond ≈ **24,000 actions** (human ~20 min); abstract says "over 20,000."

## 4) Results — exact
- **Offline Diamond Challenge (Fig. 3, 1000 eps, 60-min):** **>90% up to stone pickaxe, 29% iron pickaxe, 0.7% diamonds** — first offline agent to get diamonds. VPT-finetuned stalls at sticks (~53%); VLA (Gemma 3) ~11% iron pickaxe → Dreamer 4 **nearly triples** it.
- **World-model quality (Table 1, 1×H100):** **14/16** human-interaction tasks @21 FPS / 9.6 s context, vs Oasis-large 5/16 (~5 FPS). Cascade: FVD **306 → 57**; FPS 0.8 → 21.4.
- **Action-amount ablation (Fig. 7 — directly relevant):** **10 h actions → 53% PSNR / 75% SSIM**; **100 h → 85% PSNR / 100% SSIM** of the all-actions model. **Extrapolation:** trained with Overworld actions only, generalizes to Nether/End (seen only as unlabeled video) at **76% PSNR / 80% SSIM**.

## 5) Limitations the authors admit (§6)
"Far from a full clone": **short memory** (consistency limited to 9.6 s context); **imprecise inventory/HUD predictions** (items "unclear or change over time"). Future work: general-internet-video pretraining, **long-term memory**, language, **small amounts of corrective online data**, automatic goal discovery.

## 6) For our path (Diogenes Lab: unlabeled companion video → world model → robot)
**The exact recipe to copy:** pretrain on **mostly unlabeled** screen video → condition on actions from a **tiny labeled slice** → train the policy *in imagination*. Load-bearing number: action grounding needs only **~100 labeled hours against 2541 unlabeled (~4%)** for 85% PSNR / 100% SSIM; even **10 h (~0.4%)** gives 53% — and grounding **extrapolates to regions seen only in unlabeled video** (76–80%). Mechanism: a learned embedding stands in whenever actions are absent, so unlabeled+labeled clips train one model.

**What transfers from Minecraft (a game, like our domain):** raw-pixel input, distractor-heavy procedural scenes, long horizons (~24k actions), UI-mediated action space — closer to a companion-app screen than typical robotics benchmarks. The architecture/objective is what makes it run at 21 FPS on **one** H100, which makes imagination training tractable.

**The gap we must close — 3 Phase-1 takeaways:**
1. **We have *zero* action labels; Dreamer 4 had ~100 h.** The result is *unlabeled video for knowledge + a small labeled set for control* — "small" ≠ "none." Phase-1's first deliverable is an **action-capture pipeline** (mouse/keyboard/touch synced to frames). Their **10 h→53% / 100 h→85%** curve is our budgeting target; aim ~50–100 first-party labeled hours. *(Note: this is the same "we have no input capture" wall flagged in survey §7.4 — Dreamer 4 quantifies how little capture would suffice.)*
2. **De-risk the cheap part first.** Build/validate the **unlabeled tokenizer + shortcut-forcing dynamics** on our screen corpus *before* any robot, using FVD/PSNR-vs-sampling-steps as acceptance gates. Label-independent; proves whether companion video yields a coherent world model at all.
3. **Don't over-read the diamond headline — read milestones + the distractor caveat.** Diamonds were **0.7%**; the *robust* signal is >90% to stone pickaxe → set Phase-1 success on reliable intermediate behaviors. Minecraft distractors are *in-engine and consistent*; companion UIs add ads/notifications/overlays the model may treat as controllable. Their admitted weak points — **short 9.6 s memory, unstable HUD/inventory** — are exactly where chat-overlay UIs bite, so memory length + HUD stability belong in our eval from day one. **Robotics transfer is only an aspiration here** (one qualitative robot-video demo, no real-robot control) — the embodiment leap is still ours to prove.

**Sources:** [arXiv](https://arxiv.org/abs/2509.24527) · [PDF](https://arxiv.org/pdf/2509.24527).
