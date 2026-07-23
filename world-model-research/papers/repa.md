# REPA — Representation Alignment for Generation (arXiv 2410.06940, ICLR 2025 Oral) — Deep Read

> Deep-dive note · Yu, Kwak, Jang, Jeong, Huang, Shin, Xie; verified vs abstract + ar5iv + project + GitHub. Compiled 2026-06-29. See [olaf-world](olaf-world.md). **The mother technique of SeqΔ-REPA — gives us the exact recipe + the failure modes.**

## 1) Problem & core idea
Diffusion transformers (DiT/SiT) learn good *semantic* representations **slowly/weakly** while also learning to denoise — that representation-quality gap is the training bottleneck. **REPA:** add a cheap auxiliary regularizer **aligning the diffusion model's intermediate hidden state (from the noisy x_t) to the features of a frozen pretrained self-supervised encoder on the clean x***. Distills a strong external representation into early layers → faster convergence + better FID.

## 2) Method — precise
- **What is aligned:** the hidden state h_t at **one intermediate block**, projected through a small trainable head, matched **patch-token-wise** to the clean-image encoder feature.
- **Target:** a **frozen** encoder — default code `dinov2-vit-b`, headline results **DINOv2-g**.
- **Loss:** patch-wise **negative cosine similarity**: `L_REPA = −E[(1/N)Σₙ sim(y*[n], h_φ(h_t[n]))]` (cosine kept over an NT-Xent variant).
- **Projection head h_φ:** lightweight **3-layer MLP + SiLU**, <1% FLOPs, **discarded at inference**.
- **Where applied:** only the **first few blocks** — default **depth = block 8** (`--encoder-depth=8`); deliberately leaves later blocks for high-freq detail.
- **Total:** `L = L_velocity + λ·L_REPA`, **λ = 0.5** (`--proj-coeff=0.5`).

## 3) Results
- **>17.5× faster** SiT training (REPA <400K steps ≈ vanilla SiT-XL at 7M); FID 7.9 @400K (no guidance).
- **FID 1.42** ImageNet 256² with CFG.
- **Encoder ablation** (paraphrased — confirm decimals): FID tracks encoder strength (DINOv2-g ~9.8 < L ~10.0 < CLIP-L ~11.0 < MoCov3-L ~11.9) → **stronger encoder → lower FID**.
- **Depth ablation:** block 8 optimal; deep (14) worse → **early alignment wins**.

## 4) Why it works
**Representation-quality bottleneck:** a strong frozen encoder already encodes semantics the diffusion model learns slowly; injecting it early gives a semantic scaffold from step 0 + frees later layers for detail. Generation quality **scales with the target's representation quality** — and *spatial/structural* feature quality is more predictive than global linear-probe accuracy.

## 5) FOR OUR PATH — SeqΔ-REPA (olaf-world.md)
**Mapping:** REPA aligns *static* hidden states → *static* DINOv2 features. **SeqΔ-REPA** aligns the *integrated latent action* → a *temporal feature delta* Δφ of a frozen **V-JEPA-2**.

**Recipe to copy 1:1** (now the spec for `effect_align.py` / the LAM's 5th loss):
- **3-layer MLP + SiLU projection head** on the latent-action representation; train only the head, keep V-JEPA-2 **frozen**.
- **Negative cosine similarity**, token/region-wise then averaged. Start **λ = 0.5** (REPA plateaus for λ≥0.5 → safe floor).
- **Align early** — at the point the latent action is *first integrated*, not the output head (REPA: late alignment strictly worse).
- Additive to the primary objective; head discarded at inference.

**Failure modes to pre-empt:**
1. **Weak/domain-mismatched frozen target — THE central risk.** REPA's gains assume the encoder is strong *on the domain*. V-JEPA-2 is natural-video-trained; **UI/screen is OOD** — if Δφ is semantically flat/noisy on UI, alignment injects weak signal and gains evaporate. **Validate Δφ first** (structural check that V-JEPA-2 deltas separate real UI transitions) — the same pre-commit gate as [dinov2](dinov2.md).
2. **"REPA until it doesn't"** ([2505.16792](https://arxiv.org/abs/2505.16792)): REPA can *hurt late* once the model's own representation surpasses the frozen target → **anneal / early-stop λ**, don't hold 0.5 to convergence.
3. **Static→delta SNR gap:** Δφ subtracts two noisy features → lower SNR than REPA's static case → **normalize/whiten Δφ**, consider a larger averaging window.

**3 takeaways:** (1) **Copy the recipe verbatim** — frozen target + 3-layer-SiLU-MLP head + token-wise negative cosine + λ=0.5 at the early integration point. (2) **Gate on target quality before scaling** — verify V-JEPA-2 Δφ is meaningful on UI or the DINOv2-OOD analog silently kills the gain. (3) **Anneal the alignment** per "REPA Works Until It Doesn't."

**Sources:** [arXiv](https://arxiv.org/abs/2410.06940) · [project](https://sihyun.me/REPA/) · [GitHub](https://github.com/sihyun-yu/REPA). *Flag: exact ablation decimals are secondary-source paraphrase; confirm against the ICLR PDF if load-bearing.*
