# Real-time decoding for generative game-world-models — Deep Read for Diogenes Lab

> Deep-dive note · GameNGen [2408.14837], Matrix-Game 2.0 [2508.13009], WHAMM (MSR article), Genie 3 (DeepMind blog — **no paper**), ref point Dreamer 4 [2509.24527]. Compiled 2026-06-29. See survey §2. **The decoding engineering that makes an observation-WM fast enough for imagination training.**

## 1) The real-time problem
A generative WM must emit a new action-conditioned frame every ~40–100 ms, indefinitely. Two cost structures fight that: **(a) AR token-by-token** — N tokens/frame = N sequential forwards (WHAM-1.6B: ~1 fps; WHAMM frame = 576 tokens → token-serial is a non-starter); **(b) diffusion** — 20–50+ denoise steps/frame = seconds/frame. Plus **(c) the AR coupling tax** — each frame conditions on prior generated frames → inherently sequential in time, errors compound (exposure bias/drift). Target: collapse *per-frame* step count to a tiny constant while keeping temporal AR stable.

## 2) Decoding strategies — precise
- **(a) MaskGIT parallel decoding (WHAMM).** Generate *all* frame tokens in parallel over a small tunable **K** passes (predict all masked tokens, keep most-confident, re-mask rest). Two-transformer stack: **~500M Backbone + ~250M Refinement**; ViT-VQGAN **576 tokens**/640×360. N=576 serial → K parallel → **10+ fps**.
- **(b) Few-step diffusion distillation / Self-Forcing (Matrix-Game 2.0).** Base SkyReels-V2-I2V-1.3B (Wan2.1) → **~1.8B** with per-block action modules + **block-causal attention** (streaming DiT). Bidirectional teacher distilled to a **few-step causal student** via **Self-Forcing + DMD** (student conditioned on *its own* prior frames, not GT → attacks drift, not just speed). **3 denoise steps/frame**; rolling **KV cache ~6 latent frames** → unbounded length.
- **(c) GameNGen — diffusion + frame-conditioning.** SD v1.4 (VAE 8×, v-prediction); past **64 frames** VAE-encoded, **concatenated in latent channels**; **actions replace text cross-attention**. Real-time trick: **only 4 DDIM steps** (no quality loss vs 20+). Drift controlled by **noise augmentation** of context frames (max 0.7, level fed to model).
- **(d) Genie 3 — documented real-time, internals undisclosed.** DeepMind states **720p, 24 fps, "auto-regressive… frame by frame,"** consistency "emergent," visual memory "~one minute." **No step count / params / latency / diffusion-vs-token published** → any architectural attribution is inference, not fact.

## 3) Throughput / quality / memory (concrete)
| Model | fps | Res | Per-frame decode | Memory/context | Quality |
|---|---|---|---|---|---|
| **GameNGen** | 20 (1 TPU-v5, ~50ms) | 320×240 | **4 DDIM** | 64 frames (~3.2s) | PSNR 29.43; humans 58–60% distinguish |
| **WHAMM** | 10+ | 640×360 | **K** MaskGIT (576 tok) | **0.9s (9 frames)** | — |
| **Matrix-Game 2.0** | 25 (1 H100) | 352×640 | **3** denoise | rolling 6 latents; "minute-level" | trained ~800h @360p |
| **Genie 3** (claims) | 24 | 720p | undisclosed | ~1 min | no paper |
| **Dreamer 4** (ref) | **21 (1 H100)** | latent | **4** shortcut (=64-step, 16×) | ~9.6s | FVD 57 |

## 4) Limitations
Recurring axis = **consistency vs speed × memory length.** Short context = forgetting (WHAMM 0.9s → objects vanish ~1s after leaving view). GameNGen single-level DOOM. Matrix-Game 2.0 unbounded length but **352×640** (below SOTA) + residual AR drift. Genie 3's "minute memory" strongest-claimed but **unverifiable**. Cutting steps too far trades texture + long-horizon coherence for fps.

## 5) FOR OUR PATH
The cheapest real-time win = **few-step shortcut/distilled decoding of a *causal latent* dynamics model** — NOT MaskGIT, NOT pixel diffusion. **Dreamer 4 is the current best template**: shortcut forcing → **4-step at 64-step quality (16×) → 21 fps on one H100**, in **latent space with x-prediction** (predict the clean frame), credited with *lower error accumulation* over long rollouts — exactly what imagination-training RL needs. This matters because **imagination training is bottlenecked on WM throughput**: every gradient step rolls the WM forward, so 4-step latent decode vs 50-step pixel diffusion = feasible vs not.

**3 takeaways:**
1. **Decode in latent space, not pixels, and distill to ≤4 steps.** Pair a causal VAE/tokenizer with shortcut-forcing (Dreamer 4) or Self-Forcing+DMD (Matrix-Game 2.0). Both ~20–25 fps on one GPU; pixel-space (GameNGen) needs a TPU even at 4 steps + lower res.
2. **x-prediction + self-conditioned (Self-Forcing) distillation to fight drift** — the policy exploits any compounding WM error, so train the student on its *own* rollouts. **The single most load-bearing choice for embodied imagination**, more than raw fps.
3. **Budget context honestly.** Companion/game screens need object permanence beyond WHAMM's 0.9s. Target Dreamer-4-class **~10s context** via GQA + sparse temporal attention (cheap KV cache) before chasing Genie-3 minute-memory — whose mechanism is **undisclosed; don't assume buildable from a blog.**

**Sources:** [GameNGen 2408.14837](https://arxiv.org/abs/2408.14837) · [Matrix-Game 2.0 2508.13009](https://arxiv.org/abs/2508.13009) · [WHAMM (MSR)](https://www.microsoft.com/en-us/research/articles/whamm-real-time-world-modelling-of-interactive-environments/) · [Dreamer 4 2509.24527](https://arxiv.org/abs/2509.24527). *Flags: all Genie 3 figures are DeepMind blog claims, no paper; Matrix-Game 2.0 / Dreamer 4 fps cross-checked via arXiv HTML + secondary mirrors (PDFs exceeded fetch limits).*
