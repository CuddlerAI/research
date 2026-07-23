"""End-to-end demo (no LLM/GPU needed): one NPC, fixed map, 2 days.

Shows explore -> interact(eat apple) -> memory -> reflection(=learning) -> diary, and MEASURES
learning: day-1 the NPC must explore to find the apple; day-2 it recalls the location and goes
straight there (ticks-to-apple day2 << day1). Swap MockLLM for a real 7-14B model for real cognition.

Run:  python3 run_demo.py
"""
from __future__ import annotations

from config import DEFAULT as CFG
from gridworld import GridWorld, Entity, demo_map
from agent import GenerativeAgent


def run_day(agent: GenerativeAgent, world: GridWorld, start, day: int):
    # respawn the apple + reset the body (memory persists across days — that's the point)
    if "apple1" not in world.entities:
        world.entities["apple1"] = Entity("apple1", "apple", (2, 9), {"edible": True})
    agent.pos = start
    agent.visited = {start}
    n_reflections_before = len(agent.mem.recent("reflection", 999))

    ticks_to_apple = None
    for i in range(1, CFG.max_ticks_per_day + 1):
        step = agent.tick()
        if any("eat apple" in ev for ev in step["result"]["events"]):
            ticks_to_apple = i
            break

    new_reflections = agent.mem.recent("reflection", 999)[n_reflections_before:]
    diary = agent.write_diary(day)
    return ticks_to_apple, [r.text for r in new_reflections], diary


def main():
    grid, entities, start = demo_map()
    world = GridWorld(grid, entities, view_radius=CFG.view_radius)
    agent = GenerativeAgent(world, start, cfg=CFG)

    print("NPC sandbox demo — fixed 12x12 map, goal:", CFG.goal)
    print("=" * 64)
    results = []
    for day in range(1, CFG.days + 1):
        ticks, reflections, diary = run_day(agent, world, start, day)
        results.append(ticks)
        got = f"ate the apple in {ticks} ticks" if ticks else "did NOT find the apple"
        print(f"\nDAY {day}: {got}")
        for r in reflections:
            print(f"   reflection (learned): {r}")
        print(f"   diary: {diary}")

    print("\n" + "=" * 64)
    print("LEARNING CHECK (ticks-to-apple):", results)
    if len(results) >= 2 and results[0] and results[1]:
        verdict = "PASS — recalled the location, much faster" if results[1] < results[0] else "no speedup"
        print(f"  day1={results[0]}  day2={results[1]}  ->  {verdict}")
    print(f"\nmemory stream size: {len(agent.mem.mems)} "
          f"(obs={sum(m.kind=='observation' for m in agent.mem.mems)}, "
          f"reflections={sum(m.kind=='reflection' for m in agent.mem.mems)}, "
          f"diary={sum(m.kind=='diary' for m in agent.mem.mems)})")
    print("NOTE: cognition here is a deterministic MockLLM; wire llm.OpenAILLM/VLLMLLM for real NPCs.")


if __name__ == "__main__":
    main()
