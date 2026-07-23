"""NPC sandbox config — all knobs in one place."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Config:
    view_radius: int = 3
    # retrieval weights: score = w_recency*recency + w_importance*importance + w_relevance*relevance
    w_recency: float = 1.0
    w_importance: float = 1.0
    w_relevance: float = 1.5
    recency_decay: float = 0.99
    reflect_threshold: float = 15.0      # Σ importance of new observations -> trigger reflection (=learning)
    days: int = 2
    max_ticks_per_day: int = 150
    persona: str = "a curious villager who likes apples"
    goal: str = "find and eat an apple (food)"


DEFAULT = Config()
