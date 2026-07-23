# DirectAct — Verification & Analysis (Olaf-World's direct-action baseline) — Deep Read

> Deep-dive note · **DirectAct is NOT a standalone paper** — it is an internal baseline named *inside* Olaf-World (arXiv 2602.10104), verified from the v2 PDF (appears 9×, defined §4.4.1). Numbers below are from the **primary PDF** (higher confidence than the earlier [olaf-world](olaf-world.md) HTML extraction). Compiled 2026-06-29. See survey §5. **Confirms latent-action > direct-action for our no-input-capture data; and that direct-action = the cheap last-mile grounding head (= our M0 seed).**

## 1) Verification — very high confidence
Independent searches (arXiv, Google/Bing, OpenReview, GitHub, HF) surface **no separate "DirectAct" publication** — every hit traces to Olaf-World. Defined verbatim (§4.4.1): *"We compare: (a) **DirectAct, conditioning directly on ground-truth actions**; (b) AdaWorld, latent-action pretraining with vanilla β-VAE; (c) Olaf-World, latent-action pretraining with β-VAE + Seq∆-REPA."* → cite as *Olaf-World's direct-action-conditioning baseline*, not its own method.

## 2) Method
All three baselines share the **same video backbone + adaptation capacity (LoRA rank 16, matched steps/optimizer)**; only the action-conditioning route differs. DirectAct adapts the pretrained video model by **feeding true action labels directly** as the conditioning signal (no latent-action interface). Verbatim: *"**DirectAct with 0 videos reduces to standard image-to-video generation**"* — with zero labels it has no action channel, i.e. an unconditioned I2V generator; controllable only once given labeled action data.

## 3) The contrast: direct-action vs latent-action
Olaf-World frames the field on this axis: action-controllable WMs historically *"rely on explicit control signals… frame-level keyboard/mouse inputs logged as controls. Strong controllability, **but ties the model to a specific action schema and data-collection pipeline.**"* That's DirectAct: **requires per-frame ground-truth actions → cannot train on passive/unlabeled video at all.** Latent-action models *"infer a control interface directly from videos, enabling interaction without ground-truth actions"* (IDM infers zᵢ from (xᵢ,xᵢ₊₁); FDM predicts next frame). Corroborated by LAPO/LAPA/Genie/UniVLA. **For Diogenes Lab's no-input-capture screen video, DirectAct is a non-starter for pretraining; latent-action is the only route that consumes the unlabeled corpus.**

## 4) Results (single-source: Olaf-World's own ablation)
RPE (lower=better control; Trans/Rot), #Adapt Videos = 0 / 1 / 50 (≈0 / 1 min / 2 h labels), 1ST-P:
- **0 videos:** DirectAct **0.0703/1.4311** (uninformative — just I2V) · AdaWorld 0.0470/1.0844 · **Olaf 0.0387/0.8773**.
- **1 video (~1 min):** DirectAct 0.0672/1.2822 (overfits) · AdaWorld 0.0318/0.6420 · **Olaf 0.0284/0.4680**.
- **50 videos (~2 h):** DirectAct 0.0351/0.4527 · AdaWorld 0.0263/0.3834 · **Olaf 0.0230/0.3785**.
- **OOD:** DirectAct Rot 1.2343 · AdaWorld 1.7063 · **Olaf 1.2221**.
Discussion: *"With action supervision, DirectAct improves, but remains less controllable than latent-action pretraining under the same rank-16 LoRA setting. **We expect the gap to narrow with larger adaptation capacity.**"* **Caveat:** DirectAct has the *best visual quality* at 0 videos (unconstrained I2V); the controllability gap is conditioned on a **fixed small LoRA budget** (author-acknowledged). Single-source — reported, not independently replicated.

## 5) FOR OUR PATH
- **Takeaway 1 — confirmed:** latent-action over direct-action is right for unlabeled screen video. Direct-action **cannot pretrain without per-frame labels we don't have**; every latent-action line exists to escape that.
- **Takeaway 2 — the M0-seed niche:** DirectAct shows that once you have a small labeled slice (~1 min–2 h), **conditioning on real actions is a valid simple adaptation head** (improves monotonically with labels). So the M0 pattern — pretrain a *latent* LAM on the big unlabeled corpus, then attach a **small direct-action adapter/decoder on the tiny captured-input slice** to ground latent codes to the real control schema — is exactly Olaf-World's LoRA-rank-16 adapter regime. **Direct-action isn't the pretraining method; it's the cheap last-mile grounding head.** (Matches our M0 dual-use: seed = IDM trainer + LAM supervision + grounding head.)
- **Takeaway 3 — watch the asterisk:** the "latent beats direct" margin is at a *deliberately small* adaptation capacity; the gap narrows with more capacity/labels. **Latent-action's edge is a low-label-regime claim** — strongest exactly in our low-label setting, weaker if labeling scales. Budget verification to our actual label volume, and prefer transferable latents (SeqΔ-REPA) across the heterogeneous contexts screen video spans.

**Sources:** [Olaf-World arXiv](https://arxiv.org/abs/2602.10104) · [PDF (primary, all quotes/numbers)](https://arxiv.org/pdf/2602.10104) · [project](https://showlab.github.io/Olaf-World/).
