"""End-to-end MINIMAL LAM demo (numpy-only, runnable) — validates the pipeline LOGIC.

This is NOT the production LAM (that's lam.py: a deep VQ-VAE with the same structure, needing
torch + Cosmos/DINOv2 weights + M0 data). This is a transparent, runnable demonstration that the
DESIGN holds on synthetic distractor-heavy data:

  - a VANILLA pixel-reconstruction LAM  -> latent entangles distractor motion -> FAILS Gate-1 & Gate-2
  - a HARDENED LAM (semantic / effect-aligned target, à la DINO-space + SeqΔ-REPA) -> latent recovers
    the agent action -> PASSES Gate-1 & Gate-2

The "minimal LAM" here is the closed-form optimum of a LINEAR IDM+FDM bottleneck:
  vanilla  z = top-d_z PCA of the pixel frame-delta            (reconstruct next pixels  -> highest variance = distractor)
  hardened z = top-d_z directions of the pixel-delta that predict the SEMANTIC delta Δφ
              (reconstruct a distractor-attenuated target -> aligns to the action)
A deep VQ-VAE trained with SGD converges to the same place; the linear case is solvable exactly,
so we can show it without a training loop.

HONEST CAVEAT (matches dinov2.md / repa.md): the "semantic encoder" E_sem here is CONSTRUCTED to be
object-/agent-centric (distractor-attenuating). Whether a real frozen encoder (DINOv2 / V-JEPA-2) IS
that on our UI domain is exactly the open question Gate 0 tests — this demo assumes a good E_sem and
shows the rest of the pipeline then works.

Run:  python3 minimal_lam_demo.py
"""
from __future__ import annotations

import numpy as np

np.seterr(all="ignore")  # silence spurious macOS-Accelerate "matmul" FP warnings (results are exact)

from leakage_probe import acceptance_gate
from transfer_probe import transfer_gate
from effect_align import seqd_repa_loss

RNG = np.random.default_rng(7)
D_AGENT, D_DISTR, D_PIX, D_Z, K = 4, 8, 24, 4, 4
DISTR_STD = 1.6          # distractor increment >> action effect -> vanilla bottleneck prefers it
AGENT_EFF = np.linalg.qr(RNG.normal(size=(D_AGENT, K)))[0].T    # K ORTHONORMAL per-action effect directions (max-separable)
R = RNG.normal(size=(D_PIX, D_AGENT + D_DISTR))                 # fixed "render" pixel mixing
R_PINV = np.linalg.pinv(R)
# E_sem: recover latent then ATTENUATE the distractor subspace (a stand-in for an object-centric encoder).
# 0.05 = a GOOD (not perfect) object-centric encoder; whether a real DINOv2/V-JEPA-2 is this on UI is Gate 0.
ATTEN = np.diag([1.0] * D_AGENT + [0.05] * D_DISTR)
E_SEM = ATTEN @ R_PINV                                          # pixel -> distractor-attenuated semantic space
# Two contexts differ ONLY in distractor dynamics (mixing); the action effect is shared.
DISTR_CTX = [RNG.normal(size=(D_DISTR, D_DISTR)), RNG.normal(size=(D_DISTR, D_DISTR))]


def gen(n: int, ctx: int):
    actions = RNG.integers(0, K, n)
    agent = RNG.normal(scale=0.1, size=(n, D_AGENT))  # small within-state noise so the action effect dominates the agent channel
    agent_next = agent + AGENT_EFF[actions]
    distr = RNG.normal(scale=1.0, size=(n, D_DISTR))
    distr_next = distr + (RNG.normal(scale=DISTR_STD, size=(n, D_DISTR)) @ DISTR_CTX[ctx])
    o_t = np.concatenate([agent, distr], 1) @ R.T
    o_tp1 = np.concatenate([agent_next, distr_next], 1) @ R.T
    distr_attr = np.digitize((distr_next - distr)[:, 0], bins=[-1.0, 1.0])  # 3-bin distractor attribute
    return o_t, o_tp1, actions, distr_attr


def _pca_proj(X: np.ndarray, k: int) -> np.ndarray:
    Xc = X - X.mean(0, keepdims=True)
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    return Xc @ Vt[:k].T


def fit_minimal_lam(o_t, o_tp1, mode: str) -> np.ndarray:
    """Return continuous latent action z [n, D_Z]. mode: 'vanilla' | 'hardened'."""
    d_pix = o_tp1 - o_t                                  # pixel frame-delta (carries action + distractor)
    if mode == "vanilla":
        return _pca_proj(d_pix, D_Z)                     # top-variance directions -> distractor-heavy
    # hardened: reconstruct the SEMANTIC delta Δφ (distractor-attenuated) instead of pixels
    d_sem = (o_tp1 - o_t) @ E_SEM.T                      # = the SeqΔ-REPA target Δφ
    W, *_ = np.linalg.lstsq(d_pix, d_sem, rcond=None)    # reduced-rank regression: which pixel-delta dirs predict Δφ
    return _pca_proj(d_pix @ W, D_Z)                     # -> action-aligned latent


def run():
    np.seterr(all="ignore")
    # within-context set (Gate 1) + a 2-context set (Gate 2)
    o_t0, o_tp10, act0, dist0 = gen(1200, ctx=0)
    o_t1, o_tp11, act1, dist1 = gen(1200, ctx=1)
    o_t = np.vstack([o_t0, o_t1]); o_tp1 = np.vstack([o_tp10, o_tp11])
    action = np.concatenate([act0, act1]); distractor = np.concatenate([dist0, dist1])
    context = np.concatenate([np.zeros(1200, int), np.ones(1200, int)])
    d_sem = (o_tp1 - o_t) @ E_SEM.T
    d_sem_z = _pca_proj(d_sem, D_Z)                          # reduce Δφ to D_Z for the alignment check

    for mode in ("vanilla", "hardened"):
        z = fit_minimal_lam(o_t, o_tp1, mode)
        g1 = acceptance_gate(z, action, action_group=action, distractor_attr=distractor, baseline_B=None, A_floor=0.6)
        g2 = transfer_gate(z, action, context)
        proj, *_ = np.linalg.lstsq(z, d_sem_z, rcond=None)   # the learned REPA projection head (fit on z->Δφ)
        repa = seqd_repa_loss(z, d_sem_z, proj=proj, whiten=False)
        print(f"\n=== {mode.upper()} minimal LAM ===")
        print(f"  Gate 1 (within-context leakage): {g1}")
        print(f"  Gate 2 (cross-context transfer): {g2}")
        print(f"  SeqΔ-REPA loss vs Δφ           : {repa:.3f}  (low = aligned to the controllable effect)")

    print("\nExpected: VANILLA fails both gates (latent = distractor); HARDENED passes both (latent = action).")


if __name__ == "__main__":
    run()
