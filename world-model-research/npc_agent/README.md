# NPC sandbox — fixed-map explore/interact + diary + learning (runnable)

> Reference implementation of [`../npc_world_agent_plan.md`](../npc_world_agent_plan.md):
> a fixed-map tile engine (= the simulator you own → free, action-labeled data, no IP/privacy) + a
> **Generative-Agents mind** (memory stream → retrieval → **reflection = learning** → daily **diary** → plan/act).

**Status: runnable with a deterministic `MockLLM`** (no LLM/GPU needed) — it proves the whole loop and
*measures* learning. Swap in a real 7–14B model (`llm.OpenAILLM` / `VLLMLLM`, prompt templates already in
`llm.py`) for real cognition.

## Run
```bash
python3 run_demo.py
```
Demo result (1 NPC, 12×12 map, goal "find and eat an apple", 2 days):
```
DAY 1: ate the apple in 40 ticks
   reflection (learned): Apples can be found near (2, 9).
   diary: [Day 1] I spotted an apple while exploring. I finally ate it — satisfying!
DAY 2: ate the apple in 16 ticks            # recalled the location -> much faster
LEARNING CHECK (ticks-to-apple): [40, 16]  ->  PASS
```
Day-1 the NPC has no memory → explores. Day-2 it **retrieves the remembered apple location + the reflection**
→ goes straight there. That speedup **is** the learning, and it's the falsifiable eval from the plan (§9).

## File map
| File | Role |
|---|---|
| `gridworld.py` | Tile engine: walls, entities, BFS pathfinding, discrete actions, symbolic local obs (= the simulator) |
| `memory.py` | Memory stream: `Memory` nodes, hashing embedding (stand-in for bge/gte), retrieval `recency+importance+relevance`, reflection trigger |
| `llm.py` | LLM interface + **MockLLM** (rule-based, memory-driven planning) + the production prompt templates (importance/reflect/diary/plan) |
| `agent.py` | `GenerativeAgent`: perceive→remember→retrieve→(reflect)→plan→act; daily diary |
| `config.py` | All knobs (view radius, retrieval weights, reflection threshold, days, ticks) |
| `run_demo.py` | The end-to-end demo + the learning check |

## Plug in a real LLM (production)
Implement `llm.LLM` against your model (vLLM-served 7–14B, or an API) using the four prompt templates in
`llm.py` (`P_IMPORTANCE / P_REFLECT / P_DIARY / P_PLAN`). Everything else (engine, memory, retrieval, the
loop) stays. For multi-agent scaling + budget, see the plan §13.

## What's a stand-in vs real
- **Real & runnable:** the engine, memory stream + retrieval, reflection trigger, the loop, the learning metric.
- **Stand-in (MockLLM):** importance scoring, reflection synthesis, diary writing, action planning — deterministic
  rules so it runs offline. A real LLM makes these open-ended/believable; the *architecture* is unchanged.
