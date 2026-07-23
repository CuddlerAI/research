# LAPO: Learning to Act without Actions — Deep Read for Diogenes Lab's LAM

> Deep-dive note · Schmidt & Jiang, [arXiv 2312.10812](https://arxiv.org/abs/2312.10812) (ICLR 2024 spotlight); verified vs abstract + ar5iv + repo README + `lapo/config.yaml`. Compiled 2026-06-29. See survey §5. **The foundational LAM our skeleton copies — and exactly the method that collapses on distractors.**

## 1) Problem & core idea
Web video lacks **action labels**. LAPO recovers **latent actions purely from observation sequences** (no labels, no rewards) via an **IDM→FDM autoencoder over consecutive frames** where the latent action is an **information bottleneck**. Reconstructing `o_{t+1}` forces the bottleneck to encode "what changed between frames" = the action's effect.

## 2) Method — precise
**Autoencoder (optimize only pixel recon `min‖ô_{t+1}−o_{t+1}‖²`):**
- **IDM (encoder):** sees both sides `(o_{t−1}, o_t, o_{t+1})` → latent action `z_t`.
- **FDM (decoder):** sees only the **past** `(o_{t−1}, o_t)` + `z_t` → predicts `ô_{t+1}`.

**The bottleneck is the whole paper.** Unconstrained, the IDM copies `o_{t+1}` into `z_t` (no action learned). LAPO makes `z_t` a tight **VQ-VAE** bottleneck; since both models already condition on the past, the IDM is pressured to encode **only the delta** = the action. **Authoritative VQ config** (`config.yaml`): `num_codebooks: 2`, `num_discrete_latents: 4`, `emb_dim: 16`, `num_embs: 64`, `commitment_cost: 0.05`. *(⚠️ earlier "128-dim / 8 codes" guesses are NOT in the config — trust these.)* Backbones: IDM/policy = IMPALA-CNN×4; FDM = U-Net/ResNet.

**Recovering true action structure:** UMAP of `z_t` colored by true action (viz only) clusters cleanly by action on ~7/16 Procgen games; fragments in partially-observed games (moving camera → IDM smuggles newly-revealed pixels into `z_t`). A **no-VQ ablation** has lower FDM loss but worse structure → **VQ is the binding constraint**.

**Alignment latent→true:** Stage 2 BC a latent policy `min‖π(o_t)−z_t‖²`. Stage 3: either an **offline decoder** (tiny MLP `Z→A`, **<256 labeled transitions** ≈ PPO-from-scratch@4M) or **online RL** (freeze convs, swap head, PPO 4M frames).

## 3) Results
Procgen (16 games). Online: recovers expert in **4M frames** (vs from-scratch 44% of expert); **80% expert within 300k frames in 8/16**; exceeds expert in 3/16. Offline: **<256 labels** ≈ 4M-step from-scratch (extreme label efficiency, but plateaus below online RL since latents aren't fully state-invariant). *(Procgen only; Atari was NOT a LAPO benchmark; DMC preliminary.)*

## 4) Limitations
Authors': (1) **delayed effects** (latent models the *visible effect*, time-delayed, not the action — want multi-step/Transformer IDM-FDM); (2) **stochasticity** competes for bottleneck capacity; (3) **scaling** = the autoencoder FDM-vs-latent capacity tension. **Crucially — the distractor failure** ([2502.00379](https://arxiv.org/abs/2502.00379), LAOM): LAPO **collapses under action-correlated distractors** (bottleneck spends itself on moving background); LAOM improves latent quality **8×**, and **2.5% labels injected DURING LAM training → 4.2×** downstream. The "learn LAM first, decode later" pipeline breaks on busy frames.

## 5) FOR OUR PATH (Diogenes Lab LAM)
**Skeleton to copy directly:** IDM(past+future)→`z_t`→FDM(past-only)→reconstruct; **VQ bottleneck is load-bearing** (without it the model cheats). Start from LAPO's `config.yaml` VQ shape (codebook size 64, 2 codebooks, 4 discrete latents) and **tune codebook capacity as the tension knob** *(note: our `config.py` defaults to UniVLA's |C|=16/N=4 — LAPO's 64 is the alternative reference; pick by ablation)*. **Alignment:** BC a latent policy, decode with a small MLP on a **handful of labeled transitions (LAPO: <256)** — astonishingly cheap on *clean* data.

But our screens are **distractor-heavy** (chat bubbles, cursors, ads, video backgrounds, scroll) — exactly where 2502.00379 shows LAPO fails. **3 takeaways:**
1. **Don't reconstruct raw pixels — operate in DINO/V-JEPA latent space.** Pixel-MSE FDM rewards modeling *every* moving pixel; a semantic space starves distractors of bottleneck budget. **Single highest-leverage hardening move.** (Confirms our DINO-space decision; see [univla](univla.md).)
2. **Inject labels early/jointly, not just at decode** (2.5% during training → 4.2×). Auxiliary action-prediction loss alongside reconstruction from day one; budget a few hundred labeled UI-action transitions (= the M0 seed).
3. **Mask/route attention to the agent region** (optical-flow or segmentation gating) so the IDM delta is dominated by the user's action, not ambient motion — then keep LAPO's VQ + <256-label decoder on top.

**Sources:** [arXiv](https://arxiv.org/abs/2312.10812) · [GitHub](https://github.com/schmidtdominik/LAPO). *Flag: exact pre-quant latent dim unknown (not in config).*
