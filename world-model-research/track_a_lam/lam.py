"""Track A · LAM — the Latent Action Model (THE self-built delta).

Architecture (Genie/LAPA/UniVLA lineage, distractor-hardened):
  IDM encoder  I(o_t, o_{t+H}) -> continuous a -> VQ(|C|=16, N=4) -> z      (inverse dynamics)
  FDM decoder  F(o_t, z)       -> predict target(o_{t+H})                   (forward dynamics)

Built in DINOv2 (registers) feature space (not pixels). Five loss terms:
  (1) feature-space reconstruction of an EXOGENOUS-ROBUST target (optical flow by default,
      else DINO features)                              -- latent-action-failure.md
  (2) VQ commitment                                   -- standard
  (3) codebook entropy bonus (utilization)            -- MAGVIT-v2 / tokenizers.md
  (4) EARLY auxiliary supervised loss on the ~2.5% labeled fraction (the highest-leverage
      distractor fix; applied DURING LAM training, not just at decode) -- latent-action-failure.md
  (5) SeqΔ-REPA effect alignment: cosine-align the INTEGRATED latent action (over a window)
      to the frozen V-JEPA-2 temporal feature delta Δφ -- the cross-context TRANSFER fix -- olaf-world.md

The decoder is discarded at inference (Genie); downstream a control signal replaces z, OR z
is decoded to real actions via a small grounding head trained on the M0 seed.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from config import LAMConfig


class VectorQuantizer(nn.Module):
    """N independent codebooks of size |C| -> N discrete tokens per step.

    Entropy bonus drives utilization (per-batch code entropy high, marginal entropy low),
    following the MAGVIT-v2 utilization objective. FSQ is a drop-in alternative (see tokenizers.md).
    """

    def __init__(self, codebook_size: int, tokens_per_step: int, dim: int):
        super().__init__()
        self.codebook_size = codebook_size
        self.tokens_per_step = tokens_per_step
        self.codebooks = nn.Parameter(torch.randn(tokens_per_step, codebook_size, dim))

    def forward(self, a: torch.Tensor):
        """a [B, N, dim] -> (z_q [B,N,dim], indices [B,N], vq_loss, entropy_bonus)."""
        raise NotImplementedError(
            "Nearest-code lookup per token; straight-through estimator; "
            "vq_loss = ||sg[a]-z_q||^2 + beta||a-sg[z_q]||^2; "
            "entropy_bonus = E[H(code|batch)] - H(E[code])."
        )


class LatentActionModel(nn.Module):
    def __init__(self, cfg: LAMConfig, feature_dim: int):
        super().__init__()
        self.cfg = cfg
        # IDM: sees DINO features of (o_t, o_{t+H}) -> N action tokens. Spatial-temporal
        # transformer w/ causal temporal mask so it stays online-usable.
        self.idm_encoder = None   # TODO: ST-transformer -> [B, N, dim]
        self.vq = VectorQuantizer(cfg.codebook_size, cfg.tokens_per_step, dim=feature_dim)
        # FDM: predict target(o_{t+H}) from features(o_t) + z ONLY (no extra history -> forces z to carry the change).
        self.fdm_decoder = None   # TODO: spatial transformer
        # Early-label head: map z -> ground-truth action space, supervised on the labeled fraction.
        self.label_head = None    # TODO: small MLP/classifier over the M0-seed action schema

    def encode_actions(self, feat_t, feat_tH):
        """(o_t, o_{t+H}) DINO features -> z (quantized latent actions). The inference path keeps only this."""
        raise NotImplementedError("idm_encoder -> vq")

    def loss(self, feat_t, feat_tH, target, action_label=None):
        """Compute the 4-term training loss for one batch.

        feat_t/feat_tH : DINO features of the frame pair.
        target         : exogenous-robust target of o_{t+H} (optical flow OR DINO features per cfg.recon_target).
        action_label   : ground-truth action for the labeled fraction, else None.
        """
        # z, idx, vq_loss, ent = self.vq(self.idm_encoder(feat_t, feat_tH))
        # pred = self.fdm_decoder(feat_t, z)
        # recon = F.mse_loss(pred, target)
        # total = w_recon*recon + w_vq*vq_loss - w_entropy*ent
        # if action_label is not None:  # EARLY supervision — the key distractor lever
        #     total = total + w_early_label * F.cross_entropy(self.label_head(z), action_label)
        # return total, {...}
        raise NotImplementedError("Wire all 5 terms per the docstring; see config.LAMConfig for weights.")

    def effect_alignment_loss(self, integrated_z, vjepa_delta):
        """SeqΔ-REPA (olaf-world.md): cosine-align the INTEGRATED latent action over a window to the
        frozen V-JEPA-2 temporal feature delta Δφ = φ(o_{t+W}) - φ(o_t). This is the cross-context
        TRANSFER fix — it supplies the shared coordinate frame that flow/recon alone do NOT.

        integrated_z : sum/aggregate of per-step latent actions over cfg.effect_window frames.
        vjepa_delta  : frozen V-JEPA-2 feature delta over the same window.

        Numpy reference + runnable smoke test: effect_align.py:seqd_repa_loss().
        """
        # return 1 - F.cosine_similarity(self.effect_proj(integrated_z), vjepa_delta, dim=-1).mean()
        raise NotImplementedError("Project integrated_z to vjepa dim; 1 - cosine_similarity. See effect_align.py.")


def build_target(obs_t, obs_tH, dino, mode: str):
    """Build the exogenous-robust reconstruction target.

    mode == 'optical_flow' : label-free, provably distractor-consistent (latent-action-failure.md Prop 4.8).
    mode == 'dino_feature'  : predict next DINO features (weaker against distractors).
    """
    if mode == "optical_flow":
        raise NotImplementedError("Compute DPFlow(obs_t, obs_tH) as the target (no labels needed).")
    elif mode == "dino_feature":
        raise NotImplementedError("target = dino.features(obs_tH).detach()")
    raise ValueError(f"unknown recon target mode: {mode}")
