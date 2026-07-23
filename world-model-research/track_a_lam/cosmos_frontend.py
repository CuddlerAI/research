"""Track A · LAM — frozen front-end wrappers (REUSE, don't build).

- CosmosFrontend: the open Cosmos CV4x8x8 *continuous* tokenizer, frozen. Used to
  benchmark reconstruction on our footage and (optionally) as the WM latent space.
- DinoEncoder: DINOv2 patch features, frozen. The LAM is built in THIS space
  (object-centric, distractor-robust) per univla.md.

Both are stubs: wire up real weights before running. py_compile-safe (imports
are not executed at compile time).
"""
from __future__ import annotations

import torch
import torch.nn as nn

from config import FrontendConfig


class CosmosFrontend(nn.Module):
    """Frozen Cosmos-Tokenizer-CV4x8x8 (continuous). Encode frames -> latents.

    Decision (tokenizers.md / cosmos.md): adopt frozen; benchmark recon PSNR/rFVD
    on held-out HakkoAI clips first; fine-tune the DECODER only if artifacts hurt.
    Use 4x temporal (NOT 8x) to preserve low-Hz cursor/contact frames.
    """

    def __init__(self, cfg: FrontendConfig):
        super().__init__()
        self.cfg = cfg
        self.model = None  # TODO: load Cosmos tokenizer from cfg.cosmos_weights
        if cfg.freeze_cosmos:
            for p in self.parameters():
                p.requires_grad_(False)

    @torch.no_grad()
    def encode(self, frames: torch.Tensor) -> torch.Tensor:
        """frames [B,T,C,H,W] -> continuous latents [B,T',Lc,h,w]."""
        raise NotImplementedError("Load + call the frozen Cosmos CV4x8x8 encoder.")

    @torch.no_grad()
    def reconstruct(self, frames: torch.Tensor) -> torch.Tensor:
        """For the recon-quality benchmark gate (DAVIS != UI; measure on our clips)."""
        raise NotImplementedError("encode->decode for reconstruction PSNR/rFVD benchmark.")


class DinoEncoder(nn.Module):
    """Frozen DINOv2 patch-feature encoder. The LAM reconstructs/predicts in THIS space."""

    def __init__(self, cfg: FrontendConfig):
        super().__init__()
        self.cfg = cfg
        self.model = None  # TODO: load DINOv2 (cfg.dino_model)
        if cfg.freeze_dino:
            for p in self.parameters():
                p.requires_grad_(False)

    @torch.no_grad()
    def features(self, frames: torch.Tensor) -> torch.Tensor:
        """frames [B,C,H,W] -> patch features [B,Np,D] (no CLS pooling — keep spatial)."""
        raise NotImplementedError("Return DINOv2 spatial patch tokens.")
