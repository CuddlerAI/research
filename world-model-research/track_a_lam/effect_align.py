"""SeqΔ-REPA effect-alignment — numpy reference + smoke test (the loss LOGIC, runnable).

The torch version lives in `lam.py: LatentActionModel.effect_alignment_loss`; this file proves
the logic without torch: an INTEGRATED latent action aligned to the frozen V-JEPA-2 temporal
feature delta Δφ scores LOW loss; a "shortcut" latent (aligned to camera/distractor motion, not
the controllable effect) scores HIGH. Per olaf-world.md — this is the move that buys cross-context
(game→robot) transfer; flow alone does NOT transfer.

Loss:  L = 1 - mean_i cos( P · integrated_z_i ,  Δφ_i )
where P is a (learned) projection latent→vjepa dim. Reference uses P = identity (matched dims).
"""
from __future__ import annotations

import numpy as np


def _unit(x: np.ndarray, axis: int = -1, eps: float = 1e-8) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=axis, keepdims=True) + eps)


def seqd_repa_loss(integrated_z: np.ndarray, vjepa_delta: np.ndarray,
                   proj: np.ndarray | None = None, whiten: bool = True) -> float:
    """1 - mean cosine alignment between projected integrated latent action and Δφ.

    integrated_z : [B, d_z]  sum/aggregate of per-step latent actions over the effect window.
    vjepa_delta  : [B, d_v]  φ(o_{t+W}) - φ(o_t) from the frozen V-JEPA-2 encoder.
    proj         : [d_z, d_v] projection; None => identity (requires d_z == d_v).
    whiten       : per-dim normalize Δφ first — it subtracts two noisy features so it's low-SNR (repa.md).

    REPA recipe (repa.md): in production `proj` is a TRAINED 3-layer MLP+SiLU head; the V-JEPA-2 target
    is FROZEN and discarded at inference; λ=0.5 then ANNEALED; align at the early integration point.
    Validate Δφ is meaningful on UI first (V-JEPA-2 is natural-video-trained → UI is OOD).
    """
    z = integrated_z if proj is None else integrated_z @ proj
    d = vjepa_delta
    if whiten:
        d = (d - d.mean(axis=0, keepdims=True)) / (d.std(axis=0, keepdims=True) + 1e-8)
    cos = np.sum(_unit(z) * _unit(d), axis=-1)
    return float(1.0 - cos.mean())


if __name__ == "__main__":
    np.seterr(all="ignore")
    rng = np.random.default_rng(0)
    B, d = 400, 32
    # Δφ: the controllable "effect" direction per sample (what generalizes across contexts).
    delta = rng.normal(size=(B, d))
    # GOOD integrated latent: encodes the effect (aligned to Δφ) + small noise.
    good_z = delta + 0.05 * rng.normal(size=(B, d))
    # SHORTCUT integrated latent: encodes an unrelated distractor/camera signal, orthogonal to Δφ.
    shortcut_z = rng.normal(size=(B, d))
    print(f"good  z  SeqΔ-REPA loss = {seqd_repa_loss(good_z, delta):.4f}   (want ~0)")
    print(f"short z  SeqΔ-REPA loss = {seqd_repa_loss(shortcut_z, delta):.4f}   (want ~1)")
