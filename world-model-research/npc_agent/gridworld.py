"""Fixed-map tile engine = the simulator (you own it -> free, action-labeled data, no IP/privacy).

Minimal but functional: walls, walkable floor, entities (objects/NPCs), BFS pathfinding, a small
discrete action space, and a symbolic local observation. The engine knows the action at every step,
so logged (obs, action) pairs are ground-truth labeled for free.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Optional

Pos = tuple[int, int]  # (row, col)
DIRS = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}


@dataclass
class Entity:
    id: str
    kind: str                 # "apple", "chest", "npc", ...
    pos: Pos
    state: dict = field(default_factory=dict)
    interactable: bool = True


class GridWorld:
    """grid: list[str] with '#'=wall, '.'=floor. Entities live on floor tiles."""

    def __init__(self, grid: list[str], entities: list[Entity], view_radius: int = 3):
        self.grid = [list(row) for row in grid]
        self.H, self.W = len(self.grid), len(self.grid[0])
        self.entities: dict[str, Entity] = {e.id: e for e in entities}
        self.view_radius = view_radius
        self.t = 0

    # --- geometry ---
    def walkable(self, p: Pos) -> bool:
        r, c = p
        return 0 <= r < self.H and 0 <= c < self.W and self.grid[r][c] != "#"

    def _bfs_next(self, start: Pos, goal: Pos) -> Optional[Pos]:
        """One step from start toward goal (4-connected BFS). None if unreachable/arrived."""
        if start == goal:
            return None
        seen, q = {start}, deque([(start, None)])
        first_step: dict[Pos, Pos] = {}
        while q:
            cur, step1 = q.popleft()
            for d in DIRS.values():
                nxt = (cur[0] + d[0], cur[1] + d[1])
                if nxt in seen or not self.walkable(nxt):
                    continue
                s1 = step1 or nxt           # remember the first move of this path
                if nxt == goal:
                    return s1
                seen.add(nxt)
                first_step[nxt] = s1
                q.append((nxt, s1))
        return None  # unreachable

    # --- observation ---
    def observe(self, pos: Pos) -> dict:
        r0, c0 = pos
        R = self.view_radius
        nearby = [
            {"id": e.id, "kind": e.kind, "pos": e.pos, "state": dict(e.state)}
            for e in self.entities.values()
            if abs(e.pos[0] - r0) <= R and abs(e.pos[1] - c0) <= R
        ]
        return {"t": self.t, "pos": pos, "nearby": nearby}

    # --- transition ---
    def step(self, agent_pos: Pos, action: tuple) -> tuple[Pos, dict]:
        """Execute one action. Returns (new_pos, result). result carries events for the memory stream."""
        self.t += 1
        kind = action[0]
        result = {"action": action, "ok": False, "events": []}

        if kind == "move":
            d = DIRS.get(action[1])
            nxt = (agent_pos[0] + d[0], agent_pos[1] + d[1]) if d else agent_pos
            if self.walkable(nxt):
                agent_pos, result["ok"] = nxt, True
        elif kind == "goto":
            nxt = self._bfs_next(agent_pos, tuple(action[1]))
            if nxt is not None and self.walkable(nxt):
                agent_pos, result["ok"] = nxt, True
            else:
                result["ok"] = (agent_pos == tuple(action[1]))  # already there
        elif kind == "interact":
            ent = self.entities.get(action[1])
            verb = action[2] if len(action) > 2 else "use"
            if ent and ent.interactable and _adjacent(agent_pos, ent.pos):
                result["ok"] = True
                result["events"].append(f"{verb} {ent.kind} at {ent.pos}")
                if verb == "eat" and ent.kind == "apple":
                    self.entities.pop(ent.id, None)  # consumed
        elif kind == "wait":
            result["ok"] = True

        # vision events: record entities now in view (the agent will store these as memories)
        for e in self.observe(agent_pos)["nearby"]:
            result["events"].append(f"saw {e['kind']} at {e['pos']}")
        return agent_pos, result


def _adjacent(a: Pos, b: Pos) -> bool:
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) <= 1


def demo_map() -> tuple[list[str], list[Entity], Pos]:
    """A small 12x12 room with a couple of interior walls, an apple (east) and a chest (west)."""
    grid = [
        "############",
        "#..........#",
        "#..####....#",
        "#..........#",
        "#....##....#",
        "#....##....#",
        "#..........#",
        "#...####...#",
        "#..........#",
        "#..........#",
        "#..........#",
        "############",
    ]
    entities = [
        Entity("apple1", "apple", (2, 9), {"edible": True}),
        Entity("chest1", "chest", (9, 2), {"locked": True}),
    ]
    start = (10, 1)
    return grid, entities, start
