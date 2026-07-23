# Track A · LAM minimal viable experiment (MVE)

> Code skeleton for Phase 1's **only self-built, load-bearing module**: a distractor-robust **Latent Action Model (LAM)** that learns *decodable* latent actions from unlabeled, distractor-heavy first-party screen video. Design is derived from the deep reads in [`../papers/`](../papers/) (see `README.md` there) and the Phase-1 plan.

**Status: SKELETON + validated logic.** Interfaces + design decisions are encoded; the heavy nn forward passes (the *production* LAM in `lam.py`) are `TODO`/`NotImplementedError` and need torch + Cosmos/DINOv2 weights + M0 data. **But the pipeline LOGIC is validated end-to-end** by `minimal_lam_demo.py` (numpy, runs now): on synthetic distractor-heavy data the **vanilla pixel LAM fails all 3 diagnostics** (action-decodability 0.28≈chance, distractor-leak 0.77, transfer-F1 0.21≈chance, SeqΔ-REPA 0.73) while the **hardened LAM passes** (A=1.0, B≈0, distractor-leak≈chance, transfer-F1=1.0, SeqΔ-REPA=0.00). The three probes (`leakage_probe.py`, `transfer_probe.py`, `effect_align.py`) all run standalone too.

## Why these choices (one line each, cite the note)
- **Frozen Cosmos CV4×8×8 continuous front-end**, not a hand-rolled VQ; avoid 8× temporal (motion smear on low-Hz UI). → [`tokenizers.md`](../papers/tokenizers.md), [`cosmos.md`](../papers/cosmos.md)
- **LAM in DINOv2-WITH-REGISTERS feature space**, never raw pixels → object-centric, distractor-robust; **but UI is OOD for DINOv2 — validate per-domain first**. → [`univla.md`](../papers/univla.md), [`dinov2.md`](../papers/dinov2.md)
- **Early-injected 2.5–5% action labels** (auxiliary IDM loss *during* LAM training, not just decoding) → highest-leverage distractor fix. → [`latent-action-failure.md`](../papers/latent-action-failure.md)
- **Optical-flow / exogenous-robust reconstruction target** (label-free) instead of next-feature-only. → [`latent-action-failure.md`](../papers/latent-action-failure.md)
- **VQ codebook |C|=16, N=4 tokens/step** (small, task-centric). → [`univla.md`](../papers/univla.md), [`genie.md`](../papers/genie.md)
- **SeqΔ-REPA effect-alignment to a frozen V-JEPA-2 Δφ** — the 4th hardening move; the one that buys cross-context (game→robot) **transfer** (flow alone doesn't). → [`olaf-world.md`](../papers/olaf-world.md)
- **Two probe gates** — within-context future-leakage + cross-context transfer. → [`latent-action-failure.md`](../papers/latent-action-failure.md), [`olaf-world.md`](../papers/olaf-world.md)

## Module map
| File | Role | Reusable? |
|---|---|---|
| `data_contract.py` | Clip / frame-pair / action-label schemas + dataset protocol | — |
| `config.py` | All hyperparameters (one place) | — |
| `cosmos_frontend.py` | Frozen Cosmos tokenizer + DINOv2 encoder wrappers | **reuse** |
| `lam.py` | The LAM: IDM encoder + VQ + FDM decoder + the 4 loss terms | **build (the delta)** |
| `leakage_probe.py` | Gate 1: within-context diagnostic — A (z→action probe), B (exogenous variance), distractor-probe | **reuse** (runnable) |
| `effect_align.py` | SeqΔ-REPA loss (the 5th term) — numpy reference + smoke test | **reuse** (runnable) |
| `transfer_probe.py` | Gate 2: cross-context transfer — Macro-F1 + few-shot transfer error | **reuse** (runnable) |
| `minimal_lam_demo.py` | **End-to-end demo** (numpy): vanilla vs hardened LAM on synthetic distractor data → runs all gates | **reuse** (runnable) |
| `train.py` | Orchestration + acceptance-gate check | — |

## Acceptance gates (three, in order)
**Gate 0 — DINO-space pre-commit probe (before any LAM training).** UI is OOD for DINOv2 (`dinov2.md`). On ~200 real frames: PCA of patch tokens separates foreground from background; dense-NN matches the same UI element across frames; registers suppress outlier-norm tokens. **Fail → light unsupervised DINO finetune on screen frames first.**

**Gate 1 — within-context future-leakage probe** (`leakage_probe.py`, runnable). On a held-out distractor set: **A** (`z→action` linear probe) ≫ baseline; **B** (`Var(z | same action, diff distractor)`) ≪ vanilla-pixel-LAM; **distractor-probe** (`z→distractor`) ≈ chance. Run the **vanilla pixel-space LAM as the documented collapse baseline** (~0.04 normalized per `latent-action-failure.md`).

**Gate 2 — cross-context TRANSFER probe** (`olaf-world.md`; the real bridge-feasibility test = Phase-1 G2). Train the LAM on game-avatar video, **freeze**, then linear-probe / few-shot adapt (~1 min labels) on a *different-context* set; measure cross-context **Macro-F1 + RPE-after-adaptation**. **Reconstruction looking good means nothing here** — transfer is the gate. (`transfer_probe.py` runs the metric logic now on synthetic data; full impl needs the WM rollout + a real cross-context eval set.)

## Run
```bash
# Runnable NOW (logic validation on synthetic data — good vs collapsed/shortcut/entangled):
python3 leakage_probe.py     # Gate 1 — within-context future-leakage (good z PASS, collapsed FAIL)
python3 effect_align.py      # SeqΔ-REPA loss (aligned ~0, shortcut ~1)
python3 transfer_probe.py    # Gate 2 — cross-context transfer (transferable PASS, entangled FAIL)
python3 train.py             # prints config (no torch needed)

# Once Cosmos/DINOv2 weights + M0 data exist:
python3 train.py --config config.py            # trains the LAM
```
