# WM Eval Benchmarks: WorldModelBench & WorldSimBench — Deep Read for Gate-2

> Deep-dive note · WorldModelBench [2502.20694] + WorldSimBench [2410.18072]; cross-verified vs arXiv HTML + project pages + GitHub. Compiled 2026-06-29. See survey §6.2 + [`../track_a_lam/`](../track_a_lam/) Gate 2. **The design references for our control-success eval.**

## 1) WorldModelBench — "judging video gen AS world models"
Judges video generators on **3 world-modeling dimensions** (minimizing general video quality): **Instruction-following** (0–3 ordinal), **Physical adherence** (5 binary laws: Newton-1st / mass-conservation / fluids / impenetrability / gravity → 0–5), **Common sense** (0–2). **Max 10.** Protocol: 350 image+text pairs, **7 domains** (driving/robotics/human/industrial/natural/gaming/animation), 56 subdomains; GPT-4o captions the action delta + manual verify; judging human-then-automated (~67K labels) → a fine-tuned **VILA-2B judger** (beats GPT-4o, +8.6%). 14 models: KLING 8.82 > Minimax 8.59 > … ; **best completes only ~61% of tasks; I2V < T2V; robotics/driving weakest.** **Crucially: no rollout, no control execution — scores video *properties* only.**

## 2) WorldSimBench — "video gen AS world simulators" (the one we want)
Model hierarchy S₀–S₃, targets **S₃ (actionable video)** with a **dual eval**:
- **Explicit Perceptual Evaluation** = human-preference *video quality* (HF-Embodied Dataset, 35,701 scored tuples, 20 criteria; a LoRA'd VideoLLM predicts scores).
- **Implicit Manipulative Evaluation = the part we care about:** do generated videos translate into **correct control signals in a closed loop?** Protocol: (a) sim gives obs+instruction → (b) generate predicted future frames → (c) a **video-to-action intermediary (pre-trained IDM OR goal-conditioned policy)** maps frames→control → (d) execute in-sim → (e) re-predict every k steps, repeat. Environments: **OE=Minecraft, AD=CARLA, RM=CALVIN** (7-DOF, train A,B,C→test D, success over 20 trials).

## 3) Metrics
- **WorldModelBench:** VLM-judger predictions of the 0–10 rubric; **explicitly minimizes realism scoring** (no FVD ranking); **no downstream-success protocol**.
- **WorldSimBench manipulative (control-relevant):** per-domain sim outcomes — OE: travel distance / dig depth / item counts; AD: Route Completion / Driving Score / collisions; **RM: average task success rate (CALVIN)**. Perceptual normalized 0–1. **No FVD as the gate** — manipulative = pure task success.

## 4) Limitations
- **WorldModelBench measures NO control utility** (instruction-following ≠ correct extracted action); 2B judge, 70% pairwise agreement; 350 prompts, no interaction.
- **WorldSimBench:** manipulative score is **entangled with the IDM/goal-policy** (a bad action head masks a good WM and vice-versa) — measures the *video→action pipeline*, not the generator alone (their DynamicCrafter case: good perceptual, poor long-horizon CALVIN → perceptual≠manipulative). 3 sims, dated models, **no real-robot/cross-embodiment transfer**.
- Neither targets **screen→robot / cross-embodiment** — both assume same-domain video→same-domain action.

## 5) FOR OUR PATH (Gate-2 design)
**Adopt WorldSimBench's Implicit Manipulative skeleton; demote WorldModelBench to a cheap pre-filter** (obvious physics/instruction failures only). It's the only one measuring what Gate-2 measures — *correct control signals, not pixels*.

**Minimal "does the LAM/WM yield correct control signals" eval for screen→robot:**
1. **Frozen decoder** (our LAM / inverse-dynamics head) so the WM is judged on action-extractability — exactly as WorldSimBench fixes its IDM. Hold constant across candidates.
2. From start obs + goal, roll the WM forward, decode latent-action→control, **execute closed-loop** in a screen-task sim (+ a held-out target embodiment for transfer), re-predict every k steps.
3. Score **task success + our Gate-2 metrics directly: Macro-F1 on discrete action/event labels + RPE on the continuous trajectory** — swap CALVIN-success/Driving-Score for our Macro-F1+RPE, keep the closed-loop harness.
4. Perceptual/FVD = **diagnostic only, never pass/fail**.

**Why FVD is not our gate:** realism rewards pixel fidelity orthogonal to (and divergent from — DynamicCrafter case) control correctness; a generator can be photoreal yet emit unactionable trajectories. Gate-2 asks "is the extracted action right" = Macro-F1+RPE, not reconstruction.

**3 takeaways:**
1. **Reuse the closed-loop video→action→execute→re-predict loop with a *frozen* action head**; report task success **and** Macro-F1/RPE (WorldSimBench's manipulative eval, re-pointed at our metrics).
2. **Disentangle WM-vs-decoder** (hold the LAM constant / ablate it) so a weak head doesn't mask a good WM — WorldSimBench's main blind spot.
3. **Demand a held-out embodiment/transfer split** (their gap) — screen→robot transfer must be our explicit Gate-2 axis.

**Sources:** [WorldModelBench](https://arxiv.org/abs/2502.20694) · [WorldSimBench](https://arxiv.org/abs/2410.18072) · [WorldSimBench project](https://iranqin.github.io/WorldSimBench.github.io/). *Flags: per-dimension judger error #s + PLCC single-sourced; the IDM-vs-goal-policy split per domain is fuzzy across sources (the dual-mechanism itself is confirmed).*
