# Video Tokenizer Line — MAGVIT-v2/LFQ · Cosmos · C-ViViT · MAGVIT-v1 — Deep Read for Diogenes Lab

> Deep-dive note · MAGVIT-v2 [2310.05737] (ICLR 2024), Cosmos Tokenizer (NVIDIA), C-ViViT (Phenaki [2210.02399]), MAGVIT-v1 [2212.05199]; numbers verified from primary sources. Compiled 2026-06-29. See survey §6.3. **Decides our video front-end: reuse vs build.**

## 1) Why the tokenizer is the lever
MAGVIT-v2's thesis: LMs lag diffusion in visual gen **because of a weak discrete representation**, not the model class. ImageNet 256²: best prior LM **FID 3.41 vs diffusion 1.79**. Swap in a stronger tokenizer and the ordering flips — a masked LM on MAGVIT-v2 tokens beats diffusion (ImageNet 512² **FID 1.91 vs VDM++ 2.65**, half the model, 64 vs 250 steps); K600 frame-pred **FVD 5.2** (v1 9.9). **The lever is the codebook, not the generator.**

## 2) Methods — precise
**(a) LFQ (Lookup-Free Quantization).** Reduce the codebook embedding dim to **zero** — replace `C∈R^(K×d)` with an integer set, `|C|=K`, no embedding to look up. Binary-latent variant: factorize into `log₂K` binary dims, quantize `q(zᵢ)=sign(zᵢ)∈{−1,+1}`, token index = binary number. **Entropy penalty** drives utilization (no codebook loss). Why it scales: VQGAN's per-token embeddings become unlearnable as vocab grows; LFQ removes that bottleneck → recon+gen FID keep improving with vocab (sweep **2^10→2^16**). **Default K=2^18=262,144.**
**(b) Cosmos Tokenizer.** Continuous + discrete; **CV4×8×8, CV8×8×8, DV8×16×16** (temporal×H×W); spatial 8/16×, temporal 4/8× → up to **2048×**. **2-level Haar wavelet** front-end + causal encoder; **AE latent C=16** (continuous), **FSQ ~64K vocab** (discrete). ~**8× more compression, up to 12× faster**. Apache code / NVIDIA Open weights.
**(c) C-ViViT (Phenaki).** Factorized spatial → **causal temporal** transformer; first frame patchified as image, rest as 2-frame tubelets; causal-in-time → variable-length AR + single-image training. VQ **8,192, dim 32**. *Correction: per Nature, **WHAM uses ViT-VQGAN** (~300M, 540 tok/frame, vocab 16,384), NOT C-ViViT; **LAPA** is the C-ViViT-lineage user.*
**(d) MAGVIT-v1.** 3D-CNN VQ, codebook 1,024; v2's gain = **LFQ + large vocab + causal-3D-CNN**.

## 3) Numbers
| Tokenizer | Compression | Vocab | Recon |
|---|---|---|---|
| MAGVIT-v1 | 8× sp, 4× temp | 1,024 | UCF rFVD 24.55 |
| MAGVIT-v2 | same, K=2^18 | 262,144 | UCF recon FVD **8.62**; ImageNet-128 recon FID **1.15** |
| C-ViViT | 8× sp, 2× temp | 8,192 | (not numerically reported) |
| Cosmos CV4×8×8 | 4×8×8 | C=16 / ~64K FSQ | **DAVIS PSNR 32.80 / SSIM 0.900 / rFVD 15.93** (vs CogVideoX 29.29/0.864/19.58) |

Cosmos speed: 720×1280 4×8×8 = **34.8 ms vs CogVideoX 414 ms (~12×)**; +4 dB PSNR on DAVIS.

## 4) Limitations
- **Temporal compression vs detail:** 8× temporal (Cosmos DV/CV8×) smears fast motion — bad for high-Hz UI; **4× safer**.
- **Causal vs non-causal:** causal masking (needed for AR rollout) is strictly weaker at reconstruction — MAGVIT-v2's own non-causal baseline (K600 FVD 11.6) vs causal+LFQ (5.2); you pay for causality.
- **Vocab over-scaling:** plain VQ gen-FID worsens past a point; LFQ mitigates but entropy term needs annealing.
- **Recon artifacts:** wavelet/AE tokenizers can drop fine text/edges at high compression — the DIAMOND concern.

## 5) FOR OUR PATH
- **Reuse, don't build — adopt open Cosmos as the front-end.** At 300×180–360p / 10–20 Hz, training a C-ViViT from scratch buys little: Cosmos ships causal continuous+discrete checkpoints, Apache code, best-in-class rFVD/PSNR. Start with **CV4×8×8 (continuous, 4× temporal)** — 4× temporal preserves low-Hz cursor/contact frames; continuous latents feed JEPA/diffusion; switch to **DV (FSQ ~64K)** only if committing to an AR-LM head.
- **The tokenizer must preserve avatar/contact detail because the LAM reads its reconstruction target.** LAPA quantizes latent actions from raw frames; UniVLA from **DINOv2 patch features**. UniVLA warns web-video latent actions "capture task-irrelevant dynamics… non-ego agents or camera shifts" — **literally our distractor problem.** Choices are coupled: lossy temporal compression that helps the tokenizer can erase the very pixels the LAM needs.
- **3 takeaways:** (1) **Default Cosmos CV4×8×8 continuous**; benchmark recon PSNR/rFVD on *held-out screen clips* before committing (DAVIS≠UI). (2) **Avoid 8× temporal** for interactive screen video — motion smear costs more than token savings. (3) **Decouple distractor-robustness into the LAM** via DINO-space latent actions (UniVLA-style) — let Cosmos handle pixels, let the LAM handle "what's the agent doing"; you don't need a bespoke detail-preserving tokenizer.

**Sources:** [MAGVIT-v2 2310.05737](https://arxiv.org/abs/2310.05737) · [Cosmos Tokenizer](https://github.com/NVIDIA/Cosmos-Tokenizer) · [Phenaki/C-ViViT 2210.02399](https://arxiv.org/abs/2210.02399).
