"""Memory stream + retrieval + reflection trigger (the heart of the Generative-Agents mind).

Park et al. 2023 retrieval: score = a*recency + b*importance + c*relevance, top-k.
Embedding here is a dependency-free hashing bag-of-words (lexical overlap) so retrieval RUNS without
a model; swap in a real sentence encoder (bge/gte) for production.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

EMB_DIM = 64


def embed(text: str) -> list[float]:
    """Deterministic hashing bag-of-words -> L2-normalized vector (stand-in for bge/gte)."""
    v = [0.0] * EMB_DIM
    for tok in re.findall(r"[a-z0-9]+", text.lower()):
        v[hash(tok) % EMB_DIM] += 1.0
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


@dataclass
class Memory:
    t: int                       # sim-time created
    kind: str                    # observation | reflection | plan | diary
    text: str
    importance: float            # 1..10
    emb: list[float] = field(default_factory=list)
    last_access: int = 0

    def __post_init__(self):
        if not self.emb:
            self.emb = embed(self.text)


class MemoryStream:
    def __init__(self, recency_decay: float = 0.99,
                 w_recency: float = 1.0, w_importance: float = 1.0, w_relevance: float = 1.0,
                 reflect_threshold: float = 30.0):
        self.mems: list[Memory] = []
        self.recency_decay = recency_decay
        self.w = (w_recency, w_importance, w_relevance)
        self.reflect_threshold = reflect_threshold
        self._importance_since_reflection = 0.0

    def add(self, m: Memory) -> None:
        m.last_access = m.t
        self.mems.append(m)
        if m.kind == "observation":
            self._importance_since_reflection += m.importance

    def retrieve(self, query: str, now: int, k: int = 8) -> list[Memory]:
        if not self.mems:
            return []
        q = embed(query)
        scored = []
        for m in self.mems:
            recency = self.recency_decay ** max(0, now - m.last_access)
            importance = m.importance / 10.0
            relevance = max(0.0, cosine(q, m.emb))
            a, b, c = self.w
            scored.append((a * recency + b * importance + c * relevance, m))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = [m for _, m in scored[:k]]
        for m in top:
            m.last_access = now           # accessing refreshes recency
        return top

    def should_reflect(self) -> bool:
        return self._importance_since_reflection >= self.reflect_threshold

    def mark_reflected(self) -> None:
        self._importance_since_reflection = 0.0

    def recent(self, kind: str | None = None, n: int = 20) -> list[Memory]:
        ms = [m for m in self.mems if kind is None or m.kind == kind]
        return ms[-n:]
