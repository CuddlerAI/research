"""LLM interface for the NPC mind + a deterministic MockLLM so the whole loop RUNS with no LLM/GPU.

The four cognitive ops (importance scoring, reflection=learning, diary, planning) are exactly the
Generative-Agents prompts. MockLLM implements them with simple rules (memory-driven planning makes
"learning" REAL, not cosmetic). Swap in OpenAILLM/VLLMLLM (prompts below) for production.
"""
from __future__ import annotations

import re

# --- production prompt templates (wire these into OpenAILLM/VLLMLLM) ---
P_IMPORTANCE = ("On a scale of 1-10, rate the poignancy of this memory "
                "(1=mundane like walking, 10=major like finding food when starving): {obs}\nRating:")
P_REFLECT = ("Recent memories of {name}:\n{mems}\nList 3 high-level insights about {name} or its world, "
             "each with supporting memory. Insights:")
P_DIARY = ("Write {name}'s first-person diary entry for day {day}, reflecting on events and feelings.\n"
           "Today's key memories:\n{mems}\nDiary:")
P_PLAN = ("{name} ({persona}). Goal: {goal}.\nState: {state}\nRelevant memories: {mems}\n"
          "Recent insights: {reflections}\nWhat does {name} do next? Output one action.")

_LOC = re.compile(r"\((\d+),\s*(\d+)\)")


class LLM:
    def score_importance(self, obs: str) -> float: raise NotImplementedError
    def reflect(self, name: str, mems: list[str]) -> list[str]: raise NotImplementedError
    def write_diary(self, name: str, day: int, mems: list[str]) -> str: raise NotImplementedError
    def plan_action(self, ctx: dict): raise NotImplementedError


class MockLLM(LLM):
    """Deterministic stand-in. Real cognition needs a 7-14B model; this proves the loop + learning."""

    def score_importance(self, obs: str) -> float:
        o = obs.lower()
        if "eat" in o or "ate" in o or "found" in o:
            return 9.0
        if "saw apple" in o or "chest" in o:
            return 7.0
        if "saw" in o:
            return 4.0
        return 1.0  # moved / waited

    def reflect(self, name: str, mems: list[str]) -> list[str]:
        # "learning": consolidate where things are seen into a durable, high-importance insight.
        apple_locs = {m.group(0) for t in mems if "apple" in t.lower() for m in [_LOC.search(t)] if m}
        insights = []
        if apple_locs:
            insights.append(f"Apples can be found near {sorted(apple_locs)[0]}.")
        insights.append(f"{name} has been exploring and remembering where useful things are.")
        return insights

    def write_diary(self, name: str, day: int, mems: list[str]) -> str:
        ate = any("eat apple" in m.lower() for m in mems)
        saw = [m for m in mems if "saw apple" in m.lower()]
        body = "I wandered the room a lot today. " if not saw else "I spotted an apple while exploring. "
        body += "I finally ate it — satisfying!" if ate else "Still hungry, will look again tomorrow."
        return f"[Day {day}] {body}"

    def plan_action(self, ctx: dict):
        # 1) eat an adjacent apple
        for e in ctx["nearby"]:
            if e["kind"] == "apple" and _adjacent(ctx["pos"], tuple(e["pos"])):
                return ("interact", e["id"], "eat"), "apple within reach -> eat"
        # 2) go to an apple we can SEE now
        for e in ctx["nearby"]:
            if e["kind"] == "apple":
                return ("goto", tuple(e["pos"])), "apple in view -> approach"
        # 3) go to a REMEMBERED apple location (this is the learned behavior)
        for t in ctx["memory_texts"] + ctx["reflections"]:
            if "apple" in t.lower():
                m = _LOC.search(t)
                if m:
                    return ("goto", (int(m.group(1)), int(m.group(2)))), "recall apple location -> go"
        # 4) explore toward an unvisited frontier tile
        if ctx.get("frontier"):
            return ("goto", ctx["frontier"]), "explore frontier"
        return ("wait",), "nothing to do"


def _adjacent(a, b) -> bool:
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) <= 1
