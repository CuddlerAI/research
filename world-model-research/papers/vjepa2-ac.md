# V-JEPA 2-AC — Deep Read for Diogenes Lab's Phase-3 Plan

> Deep-dive note · Assran et al., *V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning*, [arXiv 2506.09985](https://arxiv.org/abs/2506.09985) (Meta FAIR, 2025); verified vs abstract/ar5iv/HTML, Tables 2–3. Compiled 2026-06-29. See survey §3/§4/§7. **Our Phase-3 template — but it uses real proprioception, not latent actions.**

## 1) Problem & core idea
Learn world models that **understand, predict, plan** mostly by *observation* (internet video), then fine-tune for *action* with a tiny robot-interaction set. JEPA's defining choice: **predict in representation space, not pixels** (L1 loss vs an EMA teacher, Eq. 1). For control this matters — pixel prediction wastes capacity on photometric detail irrelevant to *where the gripper goes*; latent prediction keeps planning cheap → the **16 s vs 4 min/action** gap vs a pixel-diffusion baseline.

## 2) Method — precise
**(a) V-JEPA 2 pretraining.** Encoder **ViT-g, ~1B params**, **3D-RoPE**; predictor a smaller ViT. Masked-denoising in representation space, **L1 loss**, stop-grad + EMA teacher. Data: **>1M hours internet video + ~1M images** ("VideoMix22M": SSv2, Kinetics, HowTo100M, YT-Temporal-1B, ImageNet). ~**252K iters**, progressive: 16 frames@256² → cooldown 64 frames@384² (**8.4× GPU-time reduction** claim).

**(b) V-JEPA 2-AC.** **Freeze the ViT-g encoder**; train a new action-conditioned predictor: **300M-param transformer, 24 layers, 16 heads, 1024 hidden, GELU**. **Block-causal attention** (each patch attends to action, end-effector state, and patch features from current + all previous timesteps; AR over time, bidirectional within frame). **Actions are 7-D** (3 position + 3 orientation + 1 gripper), encoded as the **delta** in end-effector state between frames. Objective = **teacher-forcing loss** (Eq. 2) **+ rollout loss** (Eq. 3, T=2 steps ahead from its own predictions); both L1 in the frozen encoder's feature space.

**(c) Planning.** **MPC with Cross-Entropy Method (CEM)**, receding-horizon: optimize an action sequence, execute first action, re-observe, replan. Cost = **energy = L1 distance between imagined future latent and goal-image latent** (Eq. 5). **800 CEM samples, 10 refinement steps**; actions in an **L1-ball radius 0.075** (~13 cm/step). Deployed lookahead is very short (**horizon ≈1**, Table 3). **16 s per action on a single RTX 4090.**

## 3) Data
- **Pretrain:** >1M h internet video (no robot data).
- **AC fine-tune:** **"less than 62 hours of unlabeled robot videos from the Droid dataset"** — a subset (clips ≥4 s, ~**23k trajectories**), single-arm **Franka**. DROID full ≈350 h → roughly one-sixth. *(350h is external context; the paper frames its slice as "<62h".)*
- **What "unlabeled" means (verbatim):** "do not use additional meta-data indicating any reward, what type of task… or whether the demonstration was successful." They **do** use raw video **and the end-effector state signal** (→ the 7-D actions). **So: no task/reward labels, but proprioceptive action traces ARE used.** ← crux for us.

## 4) Results — exact
Two **unseen labs**, Franka + Robotiq, **monocular uncalibrated RGB**, ~10 trials/task. Table 2 (Lab1/Lab2):

| Task | V-JEPA 2-AC | Octo | Cosmos |
|---|---|---|---|
| Reach | 100/100 | 100 | 80 |
| Grasp cup | 70/60 | ~15 | 0 |
| Grasp box | 30/20 | 0 | 20 |
| Reach-w/-cup | 90/60 | ~15 | — |
| Pick-&-place cup | 80/80 | ~15 | 0 |
| Pick-&-place box | 80/50 | ~10 | 0 |

Dominates Octo (BC generalist) on grasp/pick-place and Cosmos (diffusion WM) while planning **16× faster (16 s vs ~4 min/action)**. Non-robot benchmarks: **77.3 SSv2, 39.7 R@5 EK-100, 84.0 PerceptionTest**. Admitted failure: with the **robot base out of frame**, the action axis is under-determined from monocular input → they **hand-picked a camera position**. (Azimuth sweep promised in §11.4 — *not readable in fetch; don't cite specific degradation numbers*.)

## 5) Limitations the authors admit
1. **Short horizon / error accumulation** (latent rollouts degrade with length).
2. **Monocular camera-pose sensitivity** (no calibration, base off-screen → manual camera placement).
3. **Image-goals only** (energy needs a goal *image*; no language goals).

## 6) For our path — the Phase-3 template
Exactly our target shape: **self-sup latent WM (huge unlabeled video) → frozen encoder + small AC predictor (tiny interaction set) → latent-space MPC/CEM with image goals.** But the load-bearing caveat:

**~62h of *robot* video — paired with end-effector action traces — was still required.** The encoder learns physics/affordances from passive video, but the **action→latent-transition mapping cannot be learned without action-paired data**, and here that pairing is **robot-specific** (7-D Franka end-effector deltas). No transfer experiment from non-robot action-paired video. So "does it need *robot* video specifically?" → **it needs action-labeled video in the deployment embodiment's action space — our game video has no such labels in a robot's action space.**

**3 concrete takeaways:**
1. **Pretrain is reusable; the AC head is not free.** Companion/game footage can plausibly stand in for the passive-video representation-learning stage, but **Phase-3 still needs an action-paired interaction set in the deployment action space** — budget a *small first-party robot teleop set with logged end-effector poses* (their bar: <62h, ~23k trajectories). Game video alone gets us the encoder, not the controller.
2. **Latent actions are the bridge we'd have to *add*.** V-JEPA 2-AC sidesteps latent-action inference by **using real proprioception**. To exploit *unlabeled* game action we must **insert a latent-action model** (the LAM on our roadmap) to infer pseudo-actions — this paper does **not** solve that and assumes it away. **That's our genuine research delta, not borrowed engineering.**
3. **Latent-space MPC is the cheap, copyable win.** The CEM-in-latent planner (800 samples, energy = L1-to-goal-image, receding horizon, 16 s/action on a 4090) is **architecture-agnostic and directly liftable** once we have *any* action-conditioned latent predictor — and it's where the 16× compute advantage over pixel WMs lives. Plan our control loop on this from day one; expect the same **short-horizon + viewpoint-fragility** failure modes and design evals around them.

**Sources:** [arXiv](https://arxiv.org/abs/2506.09985) · [ar5iv](https://ar5iv.labs.arxiv.org/abs/2506.09985) · [HTML v1](https://arxiv.org/html/2506.09985v1).
> *Flags: DROID ~350h total is external context (paper says only "<62h"); §11.4 azimuth quantification not verified; Octo per-cell %s approximate (ordering V-JEPA 2-AC ≫ Octo ≫/≈ Cosmos is solid).*
