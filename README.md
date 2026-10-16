# Diogenes Lab — Research

Open research from **Diogenes Lab**: an open lab building models
that see, imagine, and play virtual worlds.

This repository holds the reading, the method notes and the code skeletons behind that work —
published as we go, including the parts that did not survive verification.

> **我们公开推理过程，而不只是结论。**
> 中文与英文在文档中并行；术语与参考文献保持英文。

---

## The stack this research serves

Four models, one loop. Not four products — four faculties of a single agent, each feeding the next.

| | Model | Faculty | What it does |
|---|---|---|---|
| 01 | **Visual** | Perceive | Reads the screen in real time, on-device |
| 02 | **World** | Imagine | Learns an interactive world from gameplay video |
| 03 | **Action** | Predict | Predicts how an action changes the world |
| 04 | **Player** | Act | Plays the game — and wins |

See **[ROADMAP.md](ROADMAP.md)** for where each one actually stands, including what is blocked and
what has not been earned yet.

---

## What is in here

### [`world-model-research/`](world-model-research/)

A research knowledge base on world models and the unlabeled-video → control bridge.

**Start here**

| Document | What it answers |
|---|---|
| [`world_models_survey.md`](world-model-research/world_models_survey.md) | The field, by method genealogy: model-based RL → generative game worlds → video prediction/JEPA → embodied & driving → latent action. Includes §9, an explicit list of what we are still unsure about. |
| [`world_model_benchmarks.md`](world-model-research/world_model_benchmarks.md) | Which benchmarks exist, catalogued by *what they measure* rather than by who published them. |
| [`latent_action_cross_embodiment.md`](world-model-research/latent_action_cross_embodiment.md) | The most uncertain and most load-bearing link in the whole thesis: how a "move" in a game becomes a robot action. |
| [`robotics_transfer.md`](world-model-research/robotics_transfer.md) | The embodiment gap, stated honestly, and the routes across it. |
| [`training_plan.md`](world-model-research/training_plan.md) | How `(obs, action)` trajectories become a model that predicts the world. |

**[`papers/`](world-model-research/papers/)** — 24 deep reads (Genie, DIAMOND, Dreamer 4, VPT, WHAM,
V-JEPA 2-AC, Cosmos, LAPO/LAPA, UniVLA, GR00T …). Each note is a *read*, not an abstract: what the
paper actually shows, what it does not, and what we would take from it.

**[`track_a_lam/`](world-model-research/track_a_lam/)** — a distractor-robust **Latent Action Model**
skeleton. Interfaces and design decisions are encoded and every choice is traced to a specific paper
read. The heavy forward passes are still `TODO`, but the pipeline *logic* is validated end to end by
[`minimal_lam_demo.py`](world-model-research/track_a_lam/minimal_lam_demo.py) — pure numpy, runs now,
no GPU:

> On synthetic distractor-heavy data the **vanilla pixel LAM fails all three diagnostics**
> (action-decodability 0.28 ≈ chance, distractor-leak 0.77, transfer-F1 0.21 ≈ chance) while the
> **hardened design passes** (decodability 1.0, transfer-F1 1.0).

That is a result about the *design*, not about a trained model. We would rather say so than let the
numbers imply otherwise.

**[`npc_agent/`](world-model-research/npc_agent/)** — a runnable gridworld generative-agent demo
(memory, reflection, a diary) for the AI-NPC sandbox plan.

---

## How we work

Five commitments, in the order they bind:

1. **Open science.** Notes, surveys, weights and datasets go out as far as licensing lets them.
   Publishing the reasoning matters more than publishing the result.
2. **Verified by refutation.** Load-bearing numbers face independent verifiers whose job is to
   **refute** them. Two of three refutations and the claim is dropped — not softened, not
   caveated. This is the rule we most often lose arguments to.
3. **Efficient and self-sufficient.** Small models, local first. Every encoder starts from published
   open weights; we never pre-train one from scratch. The expensive part is the data pipeline, not
   the GPU bill.
4. **Compliant by design.** First-party collection behind a consent gate; offline or bot-only where
   it matters; never third-party scraping. If the only way to get a dataset is to take it, we do
   without the dataset.
5. **Embodied ambition.** Games are where we prove it. General embodied intelligence, including
   transfer to robots, is where it points.

### Why games

Games are the most signal-dense, consequence-verifiable and compliantly collectable source of
embodied data we know of. Every frame has a ground truth about what happened next, the environment
resets for free, and — unlike the physical world — nobody gets hurt when the policy is bad.

Games are the starting point, not the destination. The loop an agent learns here is the loop a robot
needs.

---

## What is *not* in here

Internal operating material — cost models, compute budgets, contributor incentives, stop-loss
thresholds, unreleased product state — is deliberately excluded. Some research notes exist that we
have not finished clearing for release. This repository contains only the material cleared for publication.

If a document here references something you cannot find, that is why.

---

## Licence

| | |
|---|---|
| Documentation and research notes | [CC BY 4.0](LICENSE-CC-BY-4.0.txt) |
| Code (`track_a_lam/`, `npc_agent/`) | [Apache-2.0](LICENSE-Apache-2.0.txt) |

Cited papers, benchmarks and datasets remain under their own licences; the notes are ours, the work
they describe is not.

## Citing

```bibtex
@misc{diogenes_lab_research,
  author       = {Diogenes Lab},
  title        = {Diogenes Lab Research: world models, latent action, and the unlabeled-video to control bridge},
  year         = {2026},
  howpublished = {\url{https://github.com/CuddlerAI/research}},
  note         = {CC BY 4.0}
}
```

## Contact

Found something wrong? That is the most useful thing you can tell us.

Please open an issue in this repository with the relevant document, claim, and supporting evidence.
