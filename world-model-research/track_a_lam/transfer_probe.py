"""Gate 2 — cross-context TRANSFER probe (Olaf-World style; runnable on synthetic data).

The real bridge-feasibility test (Phase-1 G2): train the LAM on one context (game avatar),
FREEZE it, then linear-probe / few-shot adapt on a DIFFERENT context (robot camera) and measure
cross-context Macro-F1 + few-shot transfer error. Per olaf-world.md: reconstruction looking good
means nothing here — TRANSFER is the gate.

A *transferable* latent (shared coordinate frame, e.g. from SeqΔ-REPA) keeps cross-context Macro-F1
high and few-shot error low; a *per-context entangled* latent (LAPO/flow alone) collapses across
contexts. The metric functions below use only numpy and actually run.
"""
from __future__ import annotations

import numpy as np


def macro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    classes = np.unique(np.concatenate([y_true, y_pred]))
    f1s = []
    for c in classes:
        tp = np.sum((y_pred == c) & (y_true == c))
        fp = np.sum((y_pred == c) & (y_true != c))
        fn = np.sum((y_pred != c) & (y_true == c))
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if (prec + rec) else 0.0)
    return float(np.mean(f1s))


def _fit_ridge(X: np.ndarray, y: np.ndarray, lam: float = 1.0):
    classes = np.unique(y)
    Y = (y[:, None] == classes[None, :]).astype(np.float64)
    W = np.linalg.solve(X.T @ X + lam * np.eye(X.shape[1]), X.T @ Y)
    return W, classes


def _predict(W, classes, X):
    return classes[np.argmax(X @ W, axis=1)]


def cross_context_macro_f1(Z: np.ndarray, action: np.ndarray, context: np.ndarray,
                           train_ctx: int = 0, test_ctx: int = 1) -> float:
    """Train an action probe on train_ctx, evaluate Macro-F1 on test_ctx (zero adaptation)."""
    tr, te = context == train_ctx, context == test_ctx
    W, classes = _fit_ridge(Z[tr], action[tr])
    return macro_f1(action[te], _predict(W, classes, Z[te]))


def few_shot_transfer_error(Z: np.ndarray, action: np.ndarray, context: np.ndarray,
                            k_per_class: int = 5, test_ctx: int = 1, seed: int = 0) -> float:
    """Adapt the decoder on k labeled samples/class from test_ctx (~"1 min of labels"), measure
    error on the rest of test_ctx. Lower = better transfer (the RPE-after-adaptation analog)."""
    rng = np.random.default_rng(seed)
    te = np.where(context == test_ctx)[0]
    classes = np.unique(action[te])
    adapt = np.concatenate([rng.choice(te[action[te] == c], size=min(k_per_class, np.sum(action[te] == c)),
                                       replace=False) for c in classes])
    rest = np.array([i for i in te if i not in set(adapt)])
    W, cls = _fit_ridge(Z[adapt], action[adapt])
    return float(1.0 - np.mean(_predict(W, cls, Z[rest]) == action[rest]))


def transfer_gate(Z, action, context, *, f1_floor: float = 0.5, fewshot_err_ceiling: float = 0.3) -> dict:
    f1 = cross_context_macro_f1(Z, action, context)
    err = few_shot_transfer_error(Z, action, context)
    return {
        "cross_context_macro_f1": round(f1, 4),
        "few_shot_transfer_error": round(err, 4),
        "PASS": bool(f1 >= f1_floor and err <= fewshot_err_ceiling),
    }


if __name__ == "__main__":
    np.seterr(all="ignore")
    rng = np.random.default_rng(0)
    N, d, n_act = 800, 16, 4
    action = rng.integers(0, n_act, size=N)
    context = (np.arange(N) % 2)  # two contexts interleaved
    A = rng.normal(size=(n_act, d))                       # shared action->latent map
    Bmap = [rng.normal(size=(n_act, d)) for _ in range(2)]  # per-context maps (entangled)
    # TRANSFERABLE latent: same action -> same direction regardless of context (shared frame).
    transferable = A[action] + 0.05 * rng.normal(size=(N, d))
    # ENTANGLED latent: action encoding differs per context (per-context coordinate frame).
    entangled = np.stack([Bmap[c][a] for a, c in zip(action, context)]) + 0.05 * rng.normal(size=(N, d))
    print("transferable z:", transfer_gate(transferable, action, context))
    print("entangled    z:", transfer_gate(entangled, action, context))
