"""GenerativeAgent — the perceive -> remember -> retrieve -> (reflect) -> plan -> act loop.

Cognition (importance/reflect/diary/plan) is delegated to an LLM interface (MockLLM by default).
The agent owns embodiment: position, visited set, frontier exploration. "Learning" emerges because
planning conditions on retrieved memories + reflections (see llm.MockLLM.plan_action).
"""
from __future__ import annotations

from collections import deque

from config import Config, DEFAULT
from gridworld import GridWorld, Pos, DIRS
from memory import Memory, MemoryStream
from llm import LLM, MockLLM


class GenerativeAgent:
    def __init__(self, world: GridWorld, start: Pos, llm: LLM | None = None, cfg: Config = DEFAULT):
        self.world = world
        self.pos = start
        self.cfg = cfg
        self.llm = llm or MockLLM()
        self.mem = MemoryStream(cfg.recency_decay, cfg.w_recency, cfg.w_importance,
                                cfg.w_relevance, cfg.reflect_threshold)
        self.visited: set[Pos] = {start}
        self._logged: set[str] = set()           # dedupe identical event memories

    # nearest reachable unvisited floor tile (the exploration frontier)
    def _frontier(self) -> Pos | None:
        seen, q = {self.pos}, deque([self.pos])
        while q:
            cur = q.popleft()
            for d in DIRS.values():
                nxt = (cur[0] + d[0], cur[1] + d[1])
                if nxt in seen or not self.world.walkable(nxt):
                    continue
                if nxt not in self.visited:
                    return nxt
                seen.add(nxt)
                q.append(nxt)
        return None

    def _remember(self, text: str, kind: str = "observation") -> None:
        if kind == "observation" and ("saw" in text) and text in self._logged:
            return                                # log a sighting once
        self._logged.add(text)
        self.mem.add(Memory(t=self.world.t, kind=kind, text=text,
                            importance=self.llm.score_importance(text)))

    def tick(self) -> dict:
        retrieved = self.mem.retrieve(self.cfg.goal, now=self.world.t, k=8)
        reflections = [m.text for m in self.mem.recent("reflection", 5)]
        obs = self.world.observe(self.pos)
        ctx = {
            "name": "NPC", "persona": self.cfg.persona, "goal": self.cfg.goal,
            "pos": self.pos, "nearby": obs["nearby"],
            "memory_texts": [m.text for m in retrieved],
            "reflections": reflections,
            "frontier": self._frontier(),
        }
        action, reason = self.llm.plan_action(ctx)
        self.pos, result = self.world.step(self.pos, action)
        self.visited.add(self.pos)
        for ev in result["events"]:
            self._remember(ev)
        if self.mem.should_reflect():
            self._reflect()
        return {"action": action, "reason": reason, "result": result}

    def _reflect(self) -> list[str]:
        recent = [m.text for m in self.mem.recent(None, 25)]
        insights = self.llm.reflect("NPC", recent)
        for ins in insights:
            self.mem.add(Memory(t=self.world.t, kind="reflection", text=ins, importance=8.0))
        self.mem.mark_reflected()
        return insights

    def write_diary(self, day: int) -> str:
        top = sorted(self.mem.recent(None, 40), key=lambda m: m.importance, reverse=True)[:6]
        entry = self.llm.write_diary("NPC", day, [m.text for m in top])
        self.mem.add(Memory(t=self.world.t, kind="diary", text=entry, importance=5.0))
        return entry
