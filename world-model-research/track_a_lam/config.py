"""Track A · LAM — all hyperparameters in one place.

Defaults encode the deep-read decisions (see README.md). Override per run.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FrontendConfig:
    # Cosmos tokenizer: continuous, 4x temporal (NOT 8x — motion smear on low-Hz UI).
    cosmos_variant: str = "Cosmos-Tokenizer-CV4x8x8"   # continuous, spatial 8x, temporal 4x
    cosmos_weights: str | None = None                  # path/hub id; None => must be set before run
    freeze_cosmos: bool = True
    # DINOv2 feature space for the LAM (object-centric, distractor-robust).
    # REGISTERS variant: flat UI panels/backgrounds are worst-case for the high-norm artifact token (dinov2.md).
    dino_model: str = "dinov2_vitb14_reg"
    freeze_dino: bool = True
    # PRE-COMMIT probe before trusting DINO space: UI is OOD for DINOv2 (trained on natural images);
    # run PCA + dense-NN + outlier-norm on ~200 real frames first (dinov2.md). Fallback: light DINO finetune.
    validate_dino_first: bool = True
    # Frozen V-JEPA 2 encoder, used twice on purpose: (a) the SeqΔ-REPA effect-alignment target (olaf-world.md),
    # (b) the Track-A control encoder family (V-JEPA 2-AC, jepa-theory.md).
    vjepa_encoder: str = "vjepa2_vitg16"
    input_resolution: tuple[int, int] = (180, 320)     # H, W — start low-res (WHAM used 300x180)
    fps: int = 10                                       # align to existing capture pipeline (~10Hz)


@dataclass
class LAMConfig:
    # Latent action codebook — small / task-centric (UniVLA: |C|=16, N=4).
    codebook_size: int = 16            # |C|
    tokens_per_step: int = 4           # N
    frame_gap_H: int = 5               # frames between (o_t, o_{t+H}); ~0.5s at 10fps. Calibrate per content.
    encoder_dim: int = 768
    encoder_depth: int = 8
    # Loss weights.
    w_recon: float = 1.0               # feature-space reconstruction (DINO features or flow target)
    w_vq: float = 0.25                 # VQ commitment
    w_entropy: float = 0.1             # codebook-utilization entropy bonus (MAGVIT-v2 style)
    w_early_label: float = 1.0         # auxiliary supervised IDM loss on the labeled fraction
    w_effect_align: float = 0.5        # SeqΔ-REPA λ; REPA (repa.md) uses 0.5 as a safe floor — then anneal
    # Distractor-suppression switches.
    recon_target: str = "optical_flow"  # {"dino_feature", "optical_flow"} — flow is exogenous-robust, label-free
    use_language_conditioning: bool = False  # UniVLA task-centric; needs manufactured captions (see univla.md)
    # TRANSFER hardening (the 4th move; the one that buys cross-context game->robot transfer — flow alone does NOT).
    # SeqΔ-REPA: align the INTEGRATED latent action over a window to the frozen V-JEPA-2 temporal delta Δφ.
    use_effect_alignment: bool = True
    effect_window: int = 8             # integrate per-step latents over this many frames before aligning
    # SeqΔ-REPA implementation defaults copied from REPA (repa.md):
    effect_proj_layers: int = 3        # 3-layer MLP + SiLU projection head (trained; target frozen; discarded at inference)
    effect_align_early: bool = True    # align at the FIRST integration point, not the output head (REPA: late = worse)
    effect_anneal: bool = True         # decay/early-stop λ once the model's rep surpasses the target ("REPA Works Until It Doesn't")
    whiten_delta: bool = True          # Δφ subtracts two noisy features -> low SNR; normalize/whiten before cosine
    validate_vjepa_delta_first: bool = True  # V-JEPA-2 is natural-video-trained; UI is OOD -> verify Δφ separates real UI transitions first


@dataclass
class DataConfig:
    # The M0 capture-pilot seed supplies the labeled fraction (see the capture-pilot plan).
    early_label_fraction: float = 0.025   # 2.5% — the failure-line "early labels" lever (2.5% -> 4.2x)
    exclude_cutscenes: bool = True        # pure-exogenous, zero agent control -> drop
    first_party_only: bool = True         # IP red line: no third-party game frames in training
    require_consent_id: bool = True       # every clip must carry an auditable consent id


@dataclass
class TrainConfig:
    batch_size: int = 32
    lr: float = 1e-4
    max_steps: int = 100_000
    seed: int = 0
    run_collapse_baseline: bool = True    # also train an AdaWorld-style per-clip PIXEL LAM = the documented "entangled / no-shared-frame" collapse reference (adaworld.md)


@dataclass
class Config:
    frontend: FrontendConfig = field(default_factory=FrontendConfig)
    lam: LAMConfig = field(default_factory=LAMConfig)
    data: DataConfig = field(default_factory=DataConfig)
    train: TrainConfig = field(default_factory=TrainConfig)


DEFAULT = Config()
