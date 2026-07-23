# Latent-Action Failure Modes: Why Distractor-Heavy Video Breaks LAMs, and What to Do — Deep Read

> Deep-dive note · **both papers verified real** (the agent caught & removed its own earlier hallucinated numbers; figures below are source-checked). Compiled 2026-06-29. See survey §5/§7. **This is the central technical risk for our path.**
>
> - PRIMARY: Nikulin et al., *Latent Action Learning Requires Supervision in the Presence of Distractors*, [arXiv:2502.00379](https://arxiv.org/abs/2502.00379) (ICML 2025).
> - SECONDARY (post-cutoff, verified): Lee, Cho, Zhao & Lee, *Why Latent Actions Fail, and How to Prevent It*, [arXiv:2605.20223](https://arxiv.org/abs/2605.20223) (13 May 2026) — theory companion formalizing the same failure.

## 1) The failure mode — precise
LAMs (à la LAPO) learn `z = IDM(o_t, o_{t+1})` by asking `FDM(o_t, z)` to reconstruct `o_{t+1}`. In real video, frame-to-frame change is **not** primarily explained by ground-truth actions — it also contains **exogenous** change (background, camera jitter, lighting, particles, other agents). Since the *future* exogenous state `ξ'` is only visible *in* `o_{t+1}`, the reconstruction objective forces `z` to carry `ξ'`. Nikulin calls it **"shortcut learning"** (IDM copying `o_{t+1}` to FDM). Lee formalizes it as **"future leakage"** and proves (**Prop 4.2**) that *no global minimizer of the LAM loss admits a ξ'-independent latent action* — leakage is **baked into the reconstruction objective**, not a tuning artifact. Net: latent capacity that should encode the controllable action is spent on action-*correlated but uncontrollable* motion.

## 2) Quantified evidence
- **LAOM (Nikulin's architectural fix, no labels): 8× better latent-action quality** (linear probing, DCS).
- **Supervision is the bigger lever: ~2.5% ground-truth labels injected *during* LAM training → 4.2–4.3× avg downstream improvement** (same label budget as baselines, "differing only in *how* they use them").
- **Honest ceiling:** LAOM+supervision reaches **normalized score 0.44 — "recovers almost half the performance of BC with the full dataset"** using 2.5% of labels. **Half, not parity.**
- **Benchmark:** **Distracting Control Suite only** (cheetah/walker/hopper/humanoid). NOT Distracting MetaWorld or BridgeData — ignore claims that it is.
- **Lee's DCS corroboration (cheetah-run):** BC upper bound 0.25±0.14; vanilla LAM collapses to **0.04±0.03**; fixes recover to 0.17–0.19 (cross-exogenous 0.17, optical-flow 0.19, encoder-robust 0.18) — "recover ~⅔–¾ of a low ceiling, never parity."

## 3) The fixes — precise
- **(a) Inject labels *early* (Nikulin).** ~2.5% true actions as an auxiliary loss *during* LAM training (not just at latent→action decoding). Anchors the latent space *before* reconstruction colonizes it with `ξ'`. The headline result (4.2× / 0.44).
- **(b) Exogenous-robust targets / optical flow (Lee).** Replace next-pixel reconstruction with an η-robust target `y` — ground-truth actions *or* **optical flow** (via pretrained **DPFlow, no labels**). **Prop 4.8** bounds latent mismatch across exogenous states → flow targets *provably* push latents to be distractor-consistent.
- **(c) Cross-exogenous reconstruction (Lee).** Two clips sharing endogenous state but different distractors → reconstruct one from the other's latent. **Prop 4.6**: under whitening reduces to CCA, keeping only directions with high energy under *both* conditions.
- **(d) Robust encoder (Lee).** Leakage energy = (frequency of ξ-change) × (encoder ξ-sensitivity δ_h); can't change scene-switch frequency → **lower δ_h**. **DINOv2** gives object-centric, ξ-robust features so the LAM attends to manipulation-relevant regions.

## 4) For our path (Diogenes Lab game/companion footage)
Game/companion screen is the **adversarial worst case**: HUD, particles, scrolling parallax, cutscenes, other agents — all action-correlated exogenous motion. **Do not run vanilla LAPO** on it; expect 0.04-style collapse.

**3 concrete takeaways:**
1. **Plan to label a little, and use it early.** The 2.5%-during-LAM-training result is the highest-leverage, lowest-cost intervention. Budget ~2–5% of clips with a coarse ground-truth action channel (for a companion app: logged input events / control deltas — cheaper than robotics). Feed as an auxiliary IDM loss in Phase-1, not a post-hoc decoder. **Order: (i) early-label supervision → (ii) optical-flow target → (iii) robust encoder.**
2. **Default the reconstruction target to optical flow, not pixels** (Lee Prop 4.8): label-free, provably exogenous-consistent, kills the "copy the scrolling background" shortcut. Best *unlabeled* lever; additive with (1).
3. **Front the pipeline with a frozen object-centric encoder (DINOv2)** — cheapest structural defense against HUD/parallax leakage; lowers δ_h before any LAM loss. **Detect & exclude cutscenes** (zero agent control, full-frame motion = pure exogenous).

**Proposed diagnostic — "future-leakage probe."** From held-out data, build pairs with *matched* agent action but *different* distractor conditions (same input replayed over two backgrounds/HUD states, or augment: swap background, inject particles, jitter camera). Compute **(A)** linear-probe accuracy `z`→true action (want high) and **(B)** exogenous-consistency variance `Var(z | same action, different distractor)` (want ≈0), plus a probe `z`→*distractor* attributes (want chance). Leakage = B large / distractor-probe above chance even when A looks okay. Acceptance gate before scaling Phase-1: **A↑, B↓, distractor-probe→chance.**

**Residual risk, plainly:** even the best published recipe recovered only **~half (0.44) of fully-labeled BC** on DCS; Lee's fixes top out at ~¾ of an already-low ceiling. **Latent actions from distractor-heavy video are a *de-risking* tool, not a label replacement** — assume Phase-1 LAM is necessary-but-insufficient and keep a true-action labeling track funded.
