# DIAMOND: Diffusion for World Modeling ("Visual Details Matter in Atari") — Deep Read for Diogenes Lab

> Deep-dive note · Alonso et al., [arXiv 2405.12399](https://arxiv.org/abs/2405.12399) v2, NeurIPS 2024 Spotlight; verified vs abstract/HTML/project page/GitHub. Compiled 2026-06-29. See survey §1/§2/§7. **Informs our observation-WM backbone choice (diffusion vs token-AR).**

## 1) Problem & core idea
World models let RL agents train "in imagination." The dominant recipe (IRIS, DreamerV3, STORM) compresses each frame into **discrete latent tokens** and models dynamics over tokens. DIAMOND's thesis — *visual details matter* — is that this compression **discards small, reward-relevant pixels** (e.g. Asterix: a 2-px enemy↔reward flip; Road Runner: tiny reward dots flicker). Fix: model dynamics **directly in pixel space with a diffusion model** (no discretizing autoencoder), train the agent inside it.

## 2) Architecture — precise
- **Framework: EDM** (Karras 2022), not DDPM — stable at low step counts; EDM preconditioning `c_skip·x_τ + c_out·F_θ(c_in·x_τ, y_τ)`, conditioning `y_τ=(c_noise, x⁰_{≤t}, a_{≤t})`.
- **Conditioning:** buffer of **L past obs + actions**; past frames **concatenated channel-wise** to the noisy next frame; **actions via adaptive group-norm (adaGN)**.
- **Backbone:** standard **U-Net 2D** denoiser, pixel space.
- **Sampling: n=3 denoising steps (Euler)** — **3 NFE/frame vs IRIS's 16**; diffusion stays coherent at very few steps.
- **Sizes:** **~4M params (Atari) → 381M (CS:GO)** (widened U-Net); CS:GO = two-stage **~330M low-res dynamics + 51M upsampler**.

## 3) Data & training
- **Atari-100k:** 26 games, 100k actions (~400k frames ≈2 h) per game; WM + actor-critic trained jointly on imagined rollouts.
- **CS:GO neural engine:** **5.5M frames (95 h) @ 16 Hz**, Dust II (5M/87h train + 0.5M/8h test); native 280×150 → dynamics at **56×30** → upsample. **12 days on one RTX 4090**; **plays ~10 Hz on RTX 3090**.

## 4) Results
- **Atari-100k mean HNS = 1.459** (IQM 0.641), **11/26 superhuman** — best for an agent trained entirely in a WM. Beats **STORM 1.266, DreamerV3 1.097, IRIS 1.046** (IRIS = same imagination setup but discrete tokens → the load-bearing "details matter" comparison). *(Headline metric is mean+IQM, not median — IQM is the modern standard.)*
- **CS:GO:** a **playable real-time neural game engine** from video+actions, no game code.

## 5) Limitations (paper's own)
(1) **Discrete-control only** (continuous untested). (2) **Frame-stacking = minimal memory** → weak long-horizon consistency. (3) **Reward/termination not integrated** (CS:GO engine has no game logic). Implicit: **per-frame sampling cost caps real-time** (~10 Hz @ 381M); **one model per game/map**.

## 6) FOR OUR PATH (observation-WM)
**Diffusion (DIAMOND) vs token-AR (WHAM/Genie) as the observation-WM backbone.** DIAMOND's evidence *for diffusion*: token compression provably drops small reward/control-relevant detail — exactly the failure that bites on **distractor-heavy companion/game screens** (UI chrome, particles, tiny state indicators). Cost *against*: **381M @ ~10 Hz**, 12 GPU-days/map, one-model-per-environment.

**Label caveat (key):** DIAMOND trained on **labeled actions** (Atari indices; CS:GO keyboard/mouse logged with frames). Like WHAM, it's an **architecture template, not a no-label precedent** — its CS:GO result is "(screen video + logged actions) → engine," not "unlabeled video → engine." Our no-label gap still needs a **latent-action layer in front of *either* backbone**.

**3 takeaways:**
1. **Use DIAMOND's conditioning/training recipe** (channel-concat past frames + actions via adaGN, EDM n=3) as a clean blueprint — but budget a **latent-action module** to supply the actions it assumes given.
2. **Diffusion's "details matter" edge is strongest exactly where our data is hard** (distractor-rich UIs flicker small state under tokenization). Worth A/B-ing a diffusion vs token observation-WM and checking temporal consistency of control-relevant elements.
3. **The real-time wall is binding for embodied control.** ~10 Hz @ 381M/one game ⇒ a diffusion WM is better as an **offline imagination trainer / rollout generator** than an online controller. Plan to **distill** (fewer NFE / consistency sampling, cf. Dreamer 4 shortcut forcing) or pair with a cheaper latent dynamics model; token/AR (Genie/WHAM) still wins on throughput + multi-environment generality.

**Sources:** [arXiv](https://arxiv.org/abs/2405.12399) · [project](https://diamond-wm.github.io/) · [GitHub](https://github.com/eloialonso/diamond).
