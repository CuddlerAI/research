"""Track A · LAM — the future-leakage probe (THE acceptance gate; runnable).

Diagnoses whether learned latent actions `z` encode the agent's controllable action
(good) or action-correlated distractor motion (future leakage / collapse). Built from
held-out pairs with MATCHED agent action but DIFFERENT distractor conditions
(same input replayed over 2 backgrounds/HUD states, or augmentation: swap background,
inject particles, jitter camera).

Metrics (see ../papers/latent-action-failure.md):
  A: linear-probe accuracy  z -> true action          (want HIGH)
  B: exogenous-consistency  Var(z | same action, diff distractor)  (want LOW / ~0)
  D: distractor-probe       z -> distractor attribute  (want ~CHANCE)

Gate passes iff A high, B low, D ~ chance — all vs the vanilla-pixel-LAM collapse baseline.
The metric functions below use only numpy and actually run.
"""
from __future__ import annotations

import numpy as np


def _ridge_linear_probe_accuracy(Z: np.ndarray, y: np.ndarray, *, split: float = 0.7,
                                 lam: float = 1.0, seed: int = 0) -> float:
    """Closed-form ridge linear probe (one-hot regression + argmax) accuracy on a held-out split.

    Z: [N, d] latent actions (flattened).  y: [N] integer class labels.
    A linear probe (not a deep net) is deliberate: we test *linear decodability* of `z`.
    """
    rng = np.random.default_rng(seed)
    n = len(y)
    idx = rng.permutation(n)
    cut = int(n * split)
    tr, te = idx[:cut], idx[cut:]
    classes = np.unique(y)
    Y = (y[tr][:, None] == classes[None, :]).astype(np.float64)  # one-hot
    X = Z[tr]
    # W = (X^T X + lam I)^-1 X^T Y
    XtX = X.T @ X + lam * np.eye(X.shape[1])
    W = np.linalg.solve(XtX, X.T @ Y)
    pred = classes[np.argmax(Z[te] @ W, axis=1)]
    return float(np.mean(pred == y[te]))


def chance_level(y: np.ndarray) -> float:
    """Majority-class accuracy = the floor a probe should not beat for distractor attributes."""
    _, counts = np.unique(y, return_counts=True)
    return float(counts.max() / counts.sum())


def metric_A_action_decodability(Z: np.ndarray, true_action: np.ndarray) -> float:
    """A: how linearly decodable the agent action is from z (want HIGH)."""
    return _ridge_linear_probe_accuracy(Z, true_action)


def metric_B_exogenous_consistency(Z: np.ndarray, action_group: np.ndarray) -> float:
    """B: mean within-(same-action)-group variance of z across distractor conditions (want LOW).

    action_group: [N] id such that samples sharing an id have the SAME agent action but
    (by construction) different distractor conditions.
    """
    groups = np.unique(action_group)
    within = []
    for g in groups:
        Zg = Z[action_group == g]
        if len(Zg) >= 2:
            within.append(Zg.var(axis=0).mean())
    return float(np.mean(within)) if within else float("nan")


def metric_D_distractor_leakage(Z: np.ndarray, distractor_attr: np.ndarray) -> tuple[float, float]:
    """D: probe accuracy z -> distractor attribute, and the chance level (want acc ~ chance)."""
    return metric_A_action_decodability(Z, distractor_attr), chance_level(distractor_attr)


def acceptance_gate(Z: np.ndarray, true_action: np.ndarray, action_group: np.ndarray,
                    distractor_attr: np.ndarray, *, baseline_B: float | None = None,
                    A_floor: float = 0.5, D_margin: float = 0.05) -> dict:
    """Run the full gate. baseline_B = vanilla-pixel-LAM B (collapse ref); ours must be << it."""
    A = metric_A_action_decodability(Z, true_action)
    B = metric_B_exogenous_consistency(Z, action_group)
    D_acc, D_chance = metric_D_distractor_leakage(Z, distractor_attr)
    passed = (
        A >= A_floor
        and (D_acc - D_chance) <= D_margin
        and (baseline_B is None or B < 0.6 * baseline_B)   # ours << collapse baseline
    )
    return {
        "A_action_decodability": round(A, 4),
        "B_exogenous_variance": round(B, 6),
        "D_distractor_acc": round(D_acc, 4),
        "D_chance": round(D_chance, 4),
        "baseline_B": baseline_B,
        "PASS": bool(passed),
    }


if __name__ == "__main__":
    # Smoke test on synthetic data: a "good" z (encodes action, ignores distractor) should PASS.
    np.seterr(all="ignore")  # silence spurious macOS-Accelerate "matmul" FP warnings (results are exact)
    rng = np.random.default_rng(0)
    N, d = 600, 16
    action = rng.integers(0, 4, size=N)
    distractor = rng.integers(0, 3, size=N)
    good_z = np.eye(4)[action] @ rng.normal(size=(4, d)) + 0.01 * rng.normal(size=(N, d))
    bad_z = np.eye(3)[distractor] @ rng.normal(size=(3, d)) + 0.01 * rng.normal(size=(N, d))
    group = action  # same action id == same agent action
    print("good z:", acceptance_gate(good_z, action, group, distractor, baseline_B=1.0))
    print("bad  z:", acceptance_gate(bad_z, action, group, distractor, baseline_B=1.0))
