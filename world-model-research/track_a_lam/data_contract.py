"""Track A · LAM — data contract.

Defines exactly what a training/eval sample is, including the compliance fields
that the M0 capture pilot must populate (consent, first-party, cutscene flag).
The LAM consumes frame PAIRS (o_t, o_{t+H}); the optional action label exists only
for the ~2.5% labeled fraction from the M0 seed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Protocol, Sequence, runtime_checkable

# NB: arrays are typed loosely (Any-like) to keep this dependency-free for py_compile.
Array = "np.ndarray | torch.Tensor"  # documentation only


@dataclass
class ActionLabel:
    """Ground-truth input for a frame, present ONLY for the M0-seed labeled fraction.

    Captured by the separately-consented input recorder (NOT a main-product key/mouse hook).
    """
    keys: Sequence[int]          # multi-hot pressed keys at this frame
    pointer_dx: float            # relative pointer/touch delta x
    pointer_dy: float            # relative pointer/touch delta y
    pointer_bins: Optional[Sequence[int]] = None  # foveated-binned (VPT-style), if discretized


@dataclass
class FramePair:
    """One LAM training unit: (o_t, o_{t+H}) plus optional supervision/targets."""
    obs_t: "Array"                       # frame at t (uint8 HWC or pre-encoded latent)
    obs_tH: "Array"                      # frame at t+H
    flow_t_tH: Optional["Array"] = None  # optional precomputed optical flow target (exogenous-robust)
    action_t: Optional[ActionLabel] = None  # present only for the labeled fraction
    distractor_attrs: dict = field(default_factory=dict)  # eval-only: bg id, has_hud, n_other_agents, camera_state...


@dataclass
class Clip:
    """A contiguous recording. The compliance fields are mandatory for training use."""
    frames: "Array"                      # [T, H, W, C] or [T, latent...]
    fps: float
    # --- compliance / provenance (the capture pilot must fill these) ---
    source: str                          # first-party content id (NEVER third-party game frames for training)
    consent_id: Optional[str] = None     # auditable, revocable consent record id
    first_party: bool = True
    is_cutscene: bool = False            # pure-exogenous; excluded from LAM training
    has_input_labels: bool = False       # True only for the M0-seed labeled fraction
    actions: Optional[Sequence[ActionLabel]] = None  # len == T-? if has_input_labels


def is_trainable(clip: Clip, *, first_party_only: bool = True,
                 exclude_cutscenes: bool = True, require_consent: bool = True) -> bool:
    """Gate a clip against the compliance contract before it can enter LAM training."""
    if first_party_only and not clip.first_party:
        return False
    if exclude_cutscenes and clip.is_cutscene:
        return False
    if require_consent and not clip.consent_id:
        return False
    return True


@runtime_checkable
class FramePairDataset(Protocol):
    """Minimal dataset interface the trainer expects."""
    def __len__(self) -> int: ...
    def __getitem__(self, i: int) -> FramePair: ...
    def labeled_indices(self) -> Sequence[int]:
        """Indices whose FramePair.action_t is not None (the ~2.5% M0-seed fraction)."""
        ...


def sample_frame_pairs(clip: Clip, gap_H: int) -> list[FramePair]:
    """Materialize (o_t, o_{t+H}) pairs from a clip. TODO: real slicing + flow precompute."""
    raise NotImplementedError("Implement frame-pair sampling + optional flow precompute.")
