# Paper deep-dives — cross-paper synthesis

> 23 load-bearing papers read in full (actual PDFs/HTML, numbers source-checked) on 2026-06-29 — **8 core-mechanism + 6 architecture/infra + 5 LAM/JEPA core + 4 baselines/eval** — feeding [the survey](../world_models_survey.md). One note per paper; this index is the **convergent picture for our path**.

## Batch 1 — core-mechanism notes

| Note | Role for our path | The number that matters |
|---|---|---|
| [genie](genie.md) | The **latent-action mechanism** (LAM = inverse-dynamics VQ; discard-at-inference) | **8 discrete codes** (built for playability, ≠ robot control); CoinRun control from ~**200** samples |
| [wham](wham.md) | **First-party-telemetry → obs+action WM** (our IP-clean template) | >1B obs-action pairs; **98×H100×5d** for 1.6B; **but had controller labels we lack** |
| [lapa](lapa.md) | End-to-end **unlabeled video → latent VLA → small robot align** | beats OpenVLA at **272 vs 21,500** GPU-h; gap-bridge = **~150 demos/skill** |
| [univla](univla.md) | The **distractor fix**: DINO-space LAM + language-conditioned task-centric codebook | **1/10 downstream data**; TI-only ablation collapses to **0.2%** (proves disentanglement) |
| [latent-action-failure](latent-action-failure.md) | **Why game video breaks latent actions** ("future leakage") + fixes | **2.5% early labels → 4.2×**, but recovers only **0.44** (~half) of full BC |
| [vpt](vpt.md) | **IDM pseudo-labeling** — robust but needs a labeled seed | **~100h** consented (video+input) is the empirical knee (1962h was overkill) |
| [dreamer4](dreamer4.md) | Closest **single PoC of the whole chain** (offline, unlabeled+small-labeled, imagination RL) | **~100h labeled (~4%)** → full action grounding; **10h → 53%** |
| [vjepa2-ac](vjepa2-ac.md) | The **Phase-3 control template** (frozen JEPA encoder + AC head + latent MPC) | **<62h** action-paired robot video; **16s/action** (15× < Cosmos); **uses real proprioception, not latent actions** |

## Batch 2 — architecture & infra notes

| Note | Role for our path | Key number / decision |
|---|---|---|
| [cosmos](cosmos.md) | Reusable **tokenizer infra** + pixel-generative "data-factory" foil | Adopt Cosmos-Tokenizer (frozen); but **4 min/action** → NOT an online planner |
| [groot](groot.md) | **2nd bridge template** (LAPA-early/IDM-late) + WM-as-data-factory | **Real teleop never removed** (1:1 co-train, ~10–13/task); our WM can "dream" but the IDM needs *our* robot set |
| [gaia](gaia.md) | Most mature **deployed** WM — operational lessons | WM's first payoff = **data-gen + evaluation**; **validate vs reality** (correlation gate) before trusting it |
| [diamond](diamond.md) | Diffusion WM = playable engine; **observation-WM backbone** choice | "details matter" favors diffusion on distractor screens; but ~10Hz@381M + **labeled actions** (template, not no-label) |
| [realtime-decoding](realtime-decoding.md) | How to make an observation-WM fast enough for imagination | Decode in **latent**, distill **≤4 steps** (Dreamer-4 shortcut / Self-Forcing); **x-prediction fights drift** |
| [tokenizers](tokenizers.md) | The video front-end: reuse vs build | **Cosmos CV4×8×8 continuous**; avoid 8× temporal; push distractor-robustness **into the LAM** |

## Architecture & build decisions (batch 2)

The batch-2 reads converge on a clean **two-track split** and a concrete build stack.

**Two-track architecture (the crystallized decision):**
- **Track A — the control path (load-bearing):** a compact **latent-state WM (JEPA/latent) → latent-action bridge → latent-space MPC**. The only route that plans cheaply (V-JEPA 2-AC **16 s** vs Cosmos **4 min**/action) and the one our embodied goal rides on.
- **Track B — the generative pixel/latent WM (Cosmos / diffusion / DIAMOND): offline only** — data-gen, eval, visualization, "dreams." **Never in the online control loop.** GAIA + GR00T confirm this is where deployed WMs actually pay off first.

**Concrete build stack (front-end → WM → LAM → control):**
1. **Front-end:** Cosmos-Tokenizer **CV4×8×8 (continuous, frozen)**; avoid 8× temporal (motion smear on low-Hz UI); benchmark reconstruction on held-out first-party clips. *Don't hand-roll a VQ.*
2. **Observation WM (if/when needed for imagination):** decode in **latent space**, distill to **≤4 steps** (Dreamer-4 shortcut forcing / Matrix-Game-2.0 Self-Forcing), **x-prediction + self-conditioned distillation to fight drift**, ~10 s context. Diffusion's "details matter" (DIAMOND) argues for it on distractor screens — but as an **offline imagination trainer, not an online planner**.
3. **LAM (the research delta):** **DINO-space, distractor-suppressed** (early 2.5% labels ＞ optical-flow ＞ language/caption conditioning), gated by the future-leakage probe. **Distractor-robustness lives here, not in the tokenizer.**
4. **Control:** V-JEPA-2-AC-style latent MPC; **real-teleop anchor** (GR00T: never zero; ~10–150 demos/skill); **validate the WM against reality** (GAIA correlation gate) before trusting any WM-based eval.

**Reuse vs build:** *reuse* Cosmos tokenizer (front-end), V-JEPA-2-AC planner (control loop), LAPA/UniVLA/GR00T latent-action recipe (the bridge). **Build:** the **distractor-robust LAM on our footage** + the **~50–100h capture pilot** that supervises it. Everything else is borrowed engineering; the LAM-on-distractor-heavy-video and its supervision are the genuine delta.

## Batch 3 — LAM / JEPA core notes (the one module we build)

| Note | Role for our path | Key |
|---|---|---|
| [jepa-theory](jepa-theory.md) | Theoretical case for Track A (predict-in-latent + latent MPC) | V-JEPA-2-AC validates it; **but JEPA may discard the SIGNAL** (tiny UI toggles/cursor) |
| [lapo](lapo.md) | The LAM **skeleton** (IDM+FDM+VQ; `<256`-label align) | literally the method 2502.00379 shows **collapses on distractors** → must harden |
| [villa-x](villa-x.md) | Newest ViLLA; proprio grounding + `c_e` | helps action-fidelity + cross-embodiment, **NOT distractors** (no proprio in screen video) |
| [dinov2](dinov2.md) | The LAM feature space | **UI is OOD** → use **registers** + a **pre-commit probe** before committing |
| [olaf-world](olaf-world.md) | The **TRANSFER** fix (verified real) | **SeqΔ-REPA**: align integrated latent to V-JEPA-2 Δφ; measure **transfer**, not reconstruction |

## The final LAM recipe (after the LAM/JEPA core reads)

The LAM is our one self-built module; batch 3 nails its design.

**Skeleton (LAPO):** IDM infers `z` from `(o_t, o_{t+1})`; FDM predicts `o_{t+1}` from past + `z`; the **VQ bottleneck** forces `z` to carry the delta. Align `z`→true action with **`<256` labeled transitions** — on *clean* data; our screens aren't clean, so:

**Four hardening moves (priority order):**
1. **DINOv2-with-registers feature space**, not pixels ([univla](univla.md), [dinov2](dinov2.md)) — *but validate per-domain first; UI is OOD for DINOv2.*
2. **Early 2.5–5% labels** as an auxiliary IDM loss *during* training ([latent-action-failure](latent-action-failure.md)) — supplied by the M0 seed.
3. **Optical-flow / exogenous-robust recon target** ([latent-action-failure](latent-action-failure.md)) — label-free.
4. **SeqΔ-REPA effect-alignment** to a frozen V-JEPA-2 Δφ ([olaf-world](olaf-world.md)) — the move that buys **cross-context TRANSFER**; flow alone does NOT transfer.

**villa-X note:** borrow its **masked joint flow-matching head** (forces real latent use) + **`c_e` embodiment factoring** (cross-embodiment), but NOT its proprio-FDM (no proprioception in screen video).

**Three gates:** (0) DINO-space **pre-commit probe**; (1) within-context **future-leakage probe** (runnable, `leakage_probe.py`); (2) cross-context **transfer probe** (the real bridge-feasibility test — Macro-F1 + RPE after ~1-min adaptation, **not** reconstruction).

**JEPA theory (the why + the catch):** predict-in-latent is the right control bet (validated end-to-end by V-JEPA-2-AC), **but its strength — discarding aleatoric pixels — is a UI-domain risk** (it may discard tiny but load-bearing controls). Keep a UI-aware auxiliary so the encoder can't drop them.

Code: [`../track_a_lam/`](../track_a_lam/) encodes all of the above (config defaults, the 5-term LAM loss, the runnable Gate-1 probe).

## Batch 4 — baselines & eval (locking the implementation)

| Note | Role for our path | Key |
|---|---|---|
| [repa](repa.md) | The technique **SeqΔ-REPA extends** | exact recipe: 3-layer SiLU head + token-wise **neg-cosine** + **λ=0.5 early**; **anneal**; **validate target on domain** |
| [eval-benchmarks](eval-benchmarks.md) | **Gate-2 design** (WorldModelBench + WorldSimBench) | adopt WorldSimBench **manipulative** (frozen head, closed-loop, task-success); **FVD never the gate** |
| [adaworld](adaworld.md) | Olaf-World's **main baseline** | borrow its **interface** (SVD WM + cheap adaptation), **not its objective** (pixel-recon entangles) = our **ablation baseline** |
| [directact](directact.md) | Olaf-World's direct-action baseline (**verified** = internal baseline, not a paper) | direct-action **can't pretrain on unlabeled video**; = the **cheap last-mile grounding head** (our M0 seed); latent's edge is a **low-label** claim |

### Implementation defaults locked (batch 4)
- **SeqΔ-REPA (from REPA):** 3-layer SiLU MLP projection head · token-wise **negative cosine** · **λ=0.5 then annealed** · align at the **early integration point** · **whiten Δφ** (low SNR) · **validate Δφ on UI first** (V-JEPA-2 is natural-video-trained → UI is OOD, same gate as DINOv2). *Now in [`config.py`](../track_a_lam/config.py) + [`effect_align.py`](../track_a_lam/effect_align.py).*
- **Gate-2 harness (from WorldSimBench):** closed-loop **video→action→execute→re-predict with a FROZEN action head**; score **task-success + Macro-F1/RPE**; **disentangle WM-vs-decoder** (hold the LAM constant); **held-out embodiment/transfer split**; FVD diagnostic-only.
- **Collapse baseline (= AdaWorld):** the AdaWorld-style **per-clip pixel LAM** is the documented "entangled / no-shared-frame" reference to beat; mirror its cross-context cosine-similarity + linear-probe diagnostics (= our [`transfer_probe.py`](../track_a_lam/transfer_probe.py)).

## The single most important convergent finding
**Four independent papers land on the same number: a small, ~50–100h labeled (video+input) set is the unlock — not zero, not thousands.**
- VPT: "could reduce [1962h] to as low as **100 hours**"; <50h and skills don't emerge.
- Dreamer 4: **~100h labeled (~4% of 2541h)** → 85% PSNR / 100% SSIM action grounding; **10h → 53%**.
- LAPA: real-robot gap-bridge = **~150 demos/skill**.
- Failure-line: **2.5% labels injected early → 4.2×** (and only labels-used-early, not late, work).

**Implication — the highest-leverage Phase-1 move is a ~50–100h first-party, separately-consented (screen+input) capture pilot.** That single asset is **dual-use**:
1. trains a **robust VPT-style supervised IDM** (90%+ accuracy → a real, decodable action space), and
2. supplies the **2.5%-early-label supervision** that stops latent-action learning from collapsing on our distractor-heavy footage.
It directly attacks our hardest constraint (survey §7.4: **no input capture → latent action mandatory**) by converting "pure unsupervised on the worst-case data" into "semi-supervised," which is the only regime with evidence of working.

## The distractor-suppression stack (for the LAM)
Game/companion screens are the documented worst case (HUD, particles, parallax, cutscenes, other agents = action-correlated exogenous motion). Stack, in priority order:
1. **Early labels** (2.5–5%, as an auxiliary IDM loss *during* LAM training) — highest leverage [latent-action-failure].
2. **Optical-flow / exogenous-robust reconstruction target** (DPFlow, label-free, provably distractor-consistent) instead of next-pixel [latent-action-failure].
3. **DINOv2 feature-space LAM** (not pixels) + manufactured **language/caption conditioning** for task-centric codes [univla].
4. **Cutscene detection & exclusion** (zero agent control = pure exogenous).
5. **Diagnostic gate — the "future-leakage probe"**: matched-action / different-distractor pairs; require `z`→action probe ↑, `Var(z | same action, diff distractor)` ↓, `z`→distractor probe → chance, before scaling.

## Phase-3 control template (once a latent predictor exists)
**V-JEPA 2-AC's latent-space CEM/MPC is directly liftable** (energy = L1 to goal-image latent, 800 samples, receding horizon, 16s/action) — architecture-agnostic, and where the 15× compute win over pixel WMs lives. Expect its **short-horizon + monocular-viewpoint fragility**; design evals around them.

## Sharpened roadmap deltas (vs the line's earlier framing)
The deep reads correct two over-optimistic assumptions:
- **"Phase 2 = directly replicate WHAM"** → **blocked**: WHAM's elegance depends on ground-truth controller logs; we have none. We get WHAM's *architecture* (ViT-VQGAN + interleaved decoder-only AR) but must *insert* latent-action inference. → ties back to the ~100h pilot.
- **"V-JEPA 2-AC = robot exit"** → true, but it **uses real end-effector proprioception, not latent actions**, and needs **action-paired data in the deployment action space**. Game video gets us the encoder, *not* the controller. Latent actions are **our genuine research delta**, assumed-away by every paper that "just works."

## The honest ceiling (state this in any proposal)
- Latent actions from distractor-heavy video recover only **~half** of fully-labeled BC (0.44, DCS) — a **de-risking tool, not a label replacement**.
- **Game-avatar-video → real-robot transfer is unproven** (LAPA validates human-hand→robot; the larger embodiment gap has no published evidence). Keep it a Phase-3 hypothesis, not an assumption.
- The full chain **"screen-capture play video → latent action → real robot control" has no public precedent** — our whitespace, and our risk.
