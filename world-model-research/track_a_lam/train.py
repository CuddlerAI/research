"""Track A · LAM — training orchestration (SKELETON) + acceptance-gate wiring.

Flow:
  1. Compliance-filter clips (data_contract.is_trainable) -> frame pairs.
  2. Frozen front-end: DINOv2 features for the LAM space; Cosmos for recon-benchmark/WM.
  3. Train the LAM with the 4-term loss (early-label supervision on the ~2.5% M0-seed fraction).
  4. (optional) Train the vanilla pixel-space LAM as the documented collapse baseline.
  5. Run the future-leakage probe gate (G2) on a held-out distractor set.

The nn pieces raise NotImplementedError until wired; the structure + gate are complete.
"""
from __future__ import annotations

import argparse

from config import Config, DEFAULT
from data_contract import FramePairDataset, is_trainable
# NB: torch-dependent modules (cosmos_frontend, lam) are imported lazily inside the
# functions that need them, so `python3 train.py` can print config without torch installed.


def build_frontend(cfg: Config):
    from cosmos_frontend import CosmosFrontend, DinoEncoder
    return CosmosFrontend(cfg.frontend), DinoEncoder(cfg.frontend)


def train_lam(cfg: Config, dataset: "FramePairDataset", *, pixel_baseline: bool = False):
    """Train one LAM. pixel_baseline=True => vanilla pixel-space recon, no DINO/flow/early-label
    (the documented 'collapse' reference, per latent-action-failure.md)."""
    from lam import LatentActionModel, build_target  # noqa: F401  (build_target used in the loop)
    cosmos, dino = build_frontend(cfg)
    feature_dim = cfg.lam.encoder_dim
    lam = LatentActionModel(cfg.lam, feature_dim=feature_dim)
    labeled = set(dataset.labeled_indices()) if not pixel_baseline else set()

    # for step in range(cfg.train.max_steps):
    #     batch = sample(dataset, cfg.train.batch_size)
    #     feat_t  = dino.features(batch.obs_t)   if not pixel_baseline else batch.obs_t
    #     feat_tH = dino.features(batch.obs_tH)  if not pixel_baseline else batch.obs_tH
    #     target  = build_target(batch.obs_t, batch.obs_tH, dino,
    #                            mode=cfg.lam.recon_target if not pixel_baseline else "pixel")
    #     action  = batch.action_t if (idx in labeled) else None   # EARLY supervision on the seed
    #     loss, logs = lam.loss(feat_t, feat_tH, target, action_label=action)
    #     loss.backward(); opt.step(); opt.zero_grad()
    raise NotImplementedError("Fill the loop; everything it needs is defined above and in lam.py.")


def run_gate(lam, held_out) -> dict:
    """Encode held-out matched-action/diff-distractor pairs -> z, run the leakage probe."""
    import numpy as np
    from leakage_probe import acceptance_gate
    # Z, true_action, action_group, distractor_attr = encode_eval_set(lam, held_out)
    raise NotImplementedError(
        "Encode the held-out set to z, then: "
        "acceptance_gate(Z, true_action, action_group, distractor_attr, baseline_B=<vanilla LAM B>)."
    )


def main():
    ap = argparse.ArgumentParser(description="Track A LAM trainer (skeleton)")
    ap.add_argument("--config", default="config.py", help="(informational) config module path")
    ap.add_argument("--eval", metavar="CKPT", help="run the leakage-probe gate on a checkpoint")
    args = ap.parse_args()

    cfg: Config = DEFAULT
    print("Track A · LAM — config summary:")
    print(f"  front-end : {cfg.frontend.cosmos_variant} (frozen) + {cfg.frontend.dino_model} (frozen)")
    print(f"  LAM       : |C|={cfg.lam.codebook_size} N={cfg.lam.tokens_per_step} "
          f"gap_H={cfg.lam.frame_gap_H} recon_target={cfg.lam.recon_target}")
    print(f"  data      : early_label={cfg.data.early_label_fraction:.1%} "
          f"first_party_only={cfg.data.first_party_only} exclude_cutscenes={cfg.data.exclude_cutscenes}")
    print("  NOTE: skeleton — wire Cosmos/DINOv2 weights + M0 data, then implement the TODOs.")


if __name__ == "__main__":
    main()
