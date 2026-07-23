# Wayve GAIA Driving World Models (GAIA-1 / 2 / 3) — Deep Read for Diogenes Lab

> Deep-dive note · [GAIA-1 2309.17080](https://arxiv.org/abs/2309.17080) + [GAIA-2 2503.20523](https://arxiv.org/abs/2503.20523) (ar5iv full text) + GAIA-3 (Wayve blog, Dec 2025 — **blog-only, unverified**). Compiled 2026-06-29. See survey §4. **The most operationally mature deployed WM — a lesson-bank for what a WM is *used for*.**

## 1) Problem & core idea
AV needs to predict many possible action-conditioned futures in long-tail traffic. GAIA = **generative world modeling**: conditioned on past obs + intended action/scene, generate realistic future driving video → accelerate AV training. Operational role shifts across generations: **GAIA-1 = imagination; GAIA-2 = controllable multi-view simulation; GAIA-3 = evaluation/validation infrastructure.**

## 2) Architecture — precise
**GAIA-1 (Sep 2023, ~9.4B):** next-token prediction in 3 stages — image tokenizer (0.3B, 288×512, D=16 → **576 tokens/frame**, codebook 8192); **6.5B AR world model** over interleaved **text(32)→image(576)→action(2: speed, curvature)**, T=26 @6.25Hz (4s) = 15,860 tokens; **2.6B video-diffusion decoder** (3D U-Net, factorized space+time attn, DDIM 50 steps).
**GAIA-2 (Mar 2025):** **latent diffusion** (no discrete tokens). Continuous autoencoder (L=64, spatial 32× / temporal 8× ≈384× compression); **8.4B** space-time factorized DiT, **flow matching**; **up to 5 consistent camera views** @448×960; **structured conditioning** — ego speed/curvature (adaLN), dynamic agents as **3D bounding boxes** (ℝ^{T×N×B×13}), road metadata (country/weather/time/lanes/lights) via cross-attn, camera intrinsics/extrinsics, + CLIP & proprietary scenario embeddings.
**Representation:** both **pixel/video-space** (realism-first), not abstract occupancy/BEV.

## 3) Data
Proprietary fleet. GAIA-1: **4,700 h @25Hz (~420M imgs), London**. GAIA-2: **~25M 2-s sequences, UK+US+DE**, 3 cars + 2 vans, 5–6 cams; geo-held-out val. GAIA-3 (blog): "**~10× more data, 9 countries / 3 continents, 5× compute**, tokenizer 2× GAIA-2." No public weights/data.

## 4) Results & deployment role
GAIA-1: minutes-long stable rollouts "from imagination," multimodal futures, action-controlled OOD. GAIA-2: high-res consistent **multi-camera** w/ fine-grained control for "common and rare scenario" simulation. **GAIA-3 (15B, blog Dec 2025)** reframes WM as **evaluation infra**: (a) safety-critical scenario gen, (b) **embodiment transfer** across rigs, (c) controlled visual diversity. Headline claims: "simulated testing **mirrors real-world results**," "**5× lower synthetic-test rejection**."

⚠️ **Verification flags.** GAIA-1/2 = peer-reviewable arXiv with explicit numbers. **GAIA-3 = blog/press only, no paper**; the "5×"/"mirrors reality" claims are "**early studies**" with **no published metrics/methodology** → vendor claims, unverified. The **Warwick (WMG)/DriveSafeSim** tie-up is real & gov-grant-funded but **validation is in progress, not a completed independent result**.

## 5) Limitations / open problems
Pixel-space = compute-heavy, physics only implicit (no guaranteed dynamical/causal consistency). **Open-loop generation ≠ closed-loop fidelity.** The decisive open question — *does synthetic-test performance predict on-road performance?* — is exactly what GAIA-3's unverified claims + Warwick project are trying to settle. Proprietary → no external reproduction.

## 6) FOR OUR PATH — transferable lessons (not the driving specifics)
The **operational arc** transfers. 3 takeaways:
1. **Phase-1 payoff = data-gen + policy *evaluation*, not closed-loop control.** GAIA delivered value as a corner-case generator and (GAIA-3) offline *evaluator*; closed-loop autonomy was never the WM's first product. Scope Phase-1 to: generate rare/long-tail screen scenarios + an **offline eval harness** ranking candidate policies. Aim for "predicts *relative* policy performance," not absolute realism.
2. **Externally validate the WM against reality before trusting it.** Wayve's most credible move is the **Warwick/LiDAR correlation studies** — and even they haven't published numbers. Bake in a **correlation gate**: hold out real interaction logs, measure WM-predicted vs actual outcome correlation, don't promote the WM to a decision tool until it clears a pre-registered bar. Treat any internal "N× better" as unproven until externally measured.
3. **Choose representation deliberately — pixel realism vs planning-friendliness.** GAIA stayed pixel/latent-video (max realism, heavy, physics-implicit). For *control*, an abstract state (occupancy/object/UI-state for screens) is cheaper & more planning-friendly. **Two-track**: a pixel/latent WM for human-inspectable data-gen + eval, plus a compact latent-state WM (JEPA-style) for the actual policy/latent-action learning. Don't force one representation to do both.

**Sources:** [GAIA-1](https://arxiv.org/abs/2309.17080) · [GAIA-2](https://arxiv.org/abs/2503.20523) · [GAIA-3 (blog, unverified)](https://wayve.ai/thinking/gaia-3/).
