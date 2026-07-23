# Roadmap

Where the four models actually stand. A **gate** here is not a milestone we hope to hit — it is the
condition under which we *stop*. If a phase misses its gate, the work does not roll forward on
optimism.

Status vocabulary: **Alpha** = running, **Research** = reading and planning, **Blocked** = waiting
on something upstream, **Deferred** = explicitly postponed.

Last updated 2026-07. Live version: [diogenesmodel.com/models](https://diogenesmodel.com/models).

---

## The loop

```
        ┌─────────────────────────────────────────────────┐
        ▼                                                 │
   01 Visual  ──▶  02 World  ──▶  03 Action  ──▶  04 Player
   see             imagine        predict          act
```

Split across four models, one sentence becomes tractable: **see** what is on the screen, **imagine**
the world it implies, **predict** what an action would do to that world, **act** — then look again
at what actually happened.

Perception can be small and local. Imagination can be trained offline from video nobody labelled.
Dynamics can be learned from a fraction of a percent of real labels. Control can start narrow — one
game, played well — instead of pretending to be general on day one.

---

## 01 · Diogenes Visual Model — `Alpha`

*A game-tuned vision-language model that reads the screen in real time, on-device.*

Our own research says the honest thing first: a single model doing sub-second full-screen
understanding on a mid-range consumer card **is not achievable today**. The bottleneck is
architecture, not weights — so the architecture changed. Frame-diff gating (< 5 ms, no model) → a
light perception layer running continuously → an on-demand deep read that only wakes when the light
layer flags something worth understanding properly.

| Phase | | Status |
|---|---|---|
| **P0** Plumbing | Frame-diff gating and a faster capture loop. Pure engineering — gets *felt* latency down before any new weights exist. | In progress |
| **P1** Local layer | Light on-device perception layer. The privacy milestone: private applications get recognised locally, not in the cloud. | Next |
| **P2** Main model | Local 4B model as the deep-read tier. CUDA sidecar on Windows, MLX on Mac. | Planned |
| **P3** Our weights | Screen-domain distillation into our own small model. Where the flywheel starts paying for itself. | Planned |

**Licence discipline.** We start from openly licensed bases on purpose, and we read the licence
before the benchmark — distilling closed frontier models runs into "competitor model" clauses, so it
is not our main path.

---

## 02 · Diogenes World Model — `Research`

*An interactive, playable world model learned from gameplay video.*

We are not inventing a sixth paradigm. We read the field, track five families of approach, and pick
the lineage whose data requirements match the data we can actually collect. The through-line we care
about most: recent work shows you can carry the **knowledge** from unlabeled video and get
**action-conditioning** from only a small labeled set, in real time on a single GPU. That is exactly
the shape of what the flywheel produces.

| | | Status |
|---|---|---|
| **Survey** | Field survey published, CC BY 4.0. Method genealogy, benchmarks, open questions. | Done |
| **Benchmarks** | Evaluation criteria fixed *before* training — we decide how we would know it worked before spending anything on it. | Done |
| **Data** | Needs Visual and Action producing labels at volume first. | Blocked |
| **Training** | First world model on first-party footage. No weights, no numbers, nothing to claim yet. | Planned |

→ [`world-model-research/world_models_survey.md`](world-model-research/world_models_survey.md)

---

## 03 · Diogenes Action Model — `Research`

*A dynamics model that predicts how an action changes the world — turning unlabeled video into
transferable action understanding.*

**Distractors are the whole problem.** A latent action model trained naively on real screen video
learns the wrong thing: it latches onto everything that moves — HUD timers, particle effects, other
players — instead of what the person at the keyboard actually did. Every design decision exists to
kill that failure mode:

- Learn in **feature space, not pixel space** (DINOv2-with-registers) — object-centric, far harder
  to distract
- A **frozen continuous front-end** rather than a hand-rolled quantiser, avoiding the temporal smear
  that wrecks low-frequency UI motion
- **Inject a small fraction of real labels early**, as an auxiliary inverse-dynamics loss *during*
  training rather than only at decode time — the single highest-leverage fix
- A **label-free reconstruction target robust to exogenous motion**, so the model is not rewarded
  for predicting things the player did not cause
- **Effect alignment** against a frozen video-prediction backbone — the move that buys game → robot
  transfer; flow alone does not
- **Two probe gates, in order**: within-context leakage, then cross-context transfer

| | | Status |
|---|---|---|
| **Design** | Every choice traced to a specific deep read, not to taste. | Done |
| **Reference** | End-to-end pipeline validated on synthetic data. Vanilla fails all three probes; hardened passes all three. Runs today, no GPU. | Done |
| **Production** | The real model's forward passes. Interfaces encoded, heavy layers still `TODO`. | In progress |
| **Transfer** | Cross-embodiment probe on real footage — the claim we most want to test, and the one we have not earned yet. | Planned |

→ [`world-model-research/track_a_lam/`](world-model-research/track_a_lam/)

---

## 04 · Diogenes Player Model — `Alpha`

*An agent that sees the game through a VLM — and actually plays it, and wins.*

A deliberately narrow first target: not general competence, but **one game, played well enough to
beat bots**. A specific, falsifiable milestone beats an impressive-sounding general one. Behaviour
cloning first; every encoder starts from published open weights. Two tiers, two clocks — a policy
layer thinking in **seconds** driving a control layer acting in **milliseconds**, because plans and
reflexes are different problems and should not share a model.

| Phase | Gate | Status |
|---|---|---|
| **0** De-risk | Pipeline proven on free, natively-labelled data. Leakage and transfer probes pass. Costs nothing but time. | In progress |
| **1a** Aim | Beats a novice baseline on a 60-second drill, at **≤ 25 ms per frame**. | In progress |
| **1b** Deathmatch ← *core gate* | **K/D ≥ 1.5** vs easy bots and **≥ 1.0** vs medium, plus 30 minutes without a crash. | Next |
| **1c** Win a round | Win a complete objective-mode match — not just win fights. | Planned |
| **2** Generalise | More than one game. Optional, and only after Phase 1 clears. | Deferred |

Bot-play targets are set to match results already published for game-playing agents, so "good"
means something outside our own heads.

---

## The flywheel

The four faculties are not only a story about cognition — they are a production line. Each one makes
the next cheaper to train, and the last produces the data the first one needs.

```
gameplay video → semantic labels → re-labelled at scale → dynamics trained → self-play
  first-party      what is on        IDM infers the        an imaginable      policies trained
  · consented      the frame         inputs                world              in the dream
        ▲                                                                            │
        └──────────  more play → more video → better labels → a better world  ────────┘
```

**Data discipline.** First-party collection behind a consent gate. Offline or bot-only where it
matters — agent play happens against bots, not in other people's competitive matches. Never
third-party scraping: if the only way to get a dataset is to take it, we do without the dataset.

---

## What would change our mind

Stated in advance, so it counts:

- **Visual** — if the layered pipeline still cannot reach interactive latency on mid-range hardware,
  the on-device premise is wrong and perception belongs in the cloud after all.
- **World** — if the "unlabeled video + a small labeled set" result does not reproduce on
  first-party footage, the data thesis does not hold and the flywheel does not spin.
- **Action** — if the cross-context transfer probe fails on real footage, the game → robot bridge is
  not there, and the embodied claim should be retired rather than restated.
- **Player** — if the deathmatch gate is missed with clean data and a working pipeline, the problem
  is the approach, not the sample count.

If you think one of these is already settled, in either direction, we would like to hear it:
**contact@diogenesmodel.com**
