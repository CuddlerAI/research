# JEPA Theory & Vision — the case FOR predict-in-latent (Track A) — Deep Read

> Deep-dive note · LeCun "A Path Towards Autonomous Machine Intelligence" (OpenReview 2022) + I-JEPA [2301.08243] + V-JEPA [2404.08471] + V-JEPA 2/-AC [2506.09985]; primary sources verified, some LeCun-PDF phrasings marked paraphrase. Compiled 2026-06-29. See survey §3 + [vjepa2-ac](vjepa2-ac.md). **The theoretical justification for Track A.**

## 1) Core thesis (LeCun's architecture)
A single differentiable architecture around a **world model** that predicts future states so an agent **plans, not reacts**. Modules: perception; world model (predict futures, fill unobserved state); **cost** = immutable **intrinsic cost** + trainable **critic** (predicts future intrinsic cost = value); **actor** (proposes action sequences); short-term memory; **configurator** (primes all modules for the current task). Actor modes: **Mode-1** reactive policy; **Mode-2 deliberative** — "uses the world model to predict consequences before execution," optimizing actions against cost via MPC. **Mode-2 = the architectural ancestor of Track A.**

## 2) JEPA mechanics — precise
A **Joint Embedding Predictive Architecture** is an **energy-based model** E(x,y): encoders → s_x, s_y; a **predictor** ŝ_y = Pred(s_x, z) with latent **z** absorbing the unpredictable/multimodal part of y; energy = prediction error **in latent space** `‖Pred(s_x,z) − s_y‖`. The loss is **between representations, not in input/pixel space** — what separates JEPA from generative/autoencoding (reconstruct pixels) and from contrastive (needs negatives). Central failure = **representation collapse** (constant encoder). Prevention families: **(i) contrastive** (negatives), **(ii) VICReg-style info-max** (variance floor + decorrelation, non-contrastive), **(iii) distillation / EMA teacher + stop-grad** (BYOL/DINO/iBOT). I-JEPA & V-JEPA use **(iii)**.

## 3) Why predict latent, not pixels
Pixels carry large **aleatoric** content (texture, exact motion, occlusion) that's intrinsically unpredictable; regressing it wastes capacity on noise. Predict **representations** that can *discard* it. Verbatim: I-JEPA blog — "abstract prediction targets for which unnecessary pixel-level details are potentially eliminated… more semantic features"; V-JEPA — "predict in latent space [has] the flexibility to eliminate irrelevant or unpredictable pixel-level details." Evidence: I-JEPA is **non-generative**, beats contrastive AND masked-autoencoder (pixel) baselines; V-JEPA leads pixel methods on **Something-Something-v2** (fine-grained motion, ~+21 pts over DINOv2 frozen) — the empirical case that latent feature-prediction captures **dynamics**, not just appearance.

## 4) Limitations / critiques
- **"Is it a world model?"** I-JEPA/V-JEPA are *representation* learners (masked prediction, no actions/rollout) — they show the **objective**, not closed-loop control; that's only concrete with **V-JEPA 2-AC**.
- **Eval is indirect** (frozen-probe accuracy, not predictive likelihood); latent space non-interpretable → collapse/shortcuts hard to detect.
- **Aleatoric/epistemic conflation:** z absorbing "unpredictable" content can also absorb genuinely *task-relevant* hard-to-predict content → can be invariant to exactly what you needed.
- **Dynamics/physics depth unproven:** strong short-horizon motion; long-horizon/contact/counterfactual unestablished; autoregressive latent rollout **drifts**.

## 5) FOR OUR PATH (Track A)
**V-JEPA 2-AC IS the template:** freeze the V-JEPA 2 encoder, post-train a ~300M action-conditioned block-causal predictor on **<62h unlabeled robot video** to predict next-frame representation given proprioception+action; control = **latent MPC** (energy = L1 to **goal-image embedding**, CEM, receding horizon). Zero-shot ~80% pick-place vs Octo ~15% / Cosmos ~0% at 16s vs minutes/action — the quantitative argument for latent over pixel-generative WMs.

**Where JEPA's assumptions break on distractor-heavy UI:**
- **(a) "Discard unpredictable detail" can discard the SIGNAL** — small toggles, badges, focus rings, cursor are a tiny high-frequency fraction of a busy screen; JEPA may treat them as noise. **This is the UI-domain risk** (compounds the [dinov2](dinov2.md) OOD concern).
- **(b) Camera-pose sensitivity → resolution/DPI/layout/theme shifts** in UI (no canonical coordinate frame).
- **(c) Rollout drift + discrete sparse-reward UI transitions** (a click flips state discontinuously) stress an L1-in-latent energy tuned for smooth physical motion.

**3 takeaways:**
1. **Adopt V-JEPA-2-AC's frozen-encoder / action-conditioned-predictor / CEM-MPC recipe** as the Track-A reference (not the pixel-WM alternative) — theoretically + empirically validated end-to-end.
2. **JEPA's strength (discarding aleatoric pixels) is its UI-domain risk** — budget collapse/invariance auditing and keep a **UI-aware auxiliary** (mask key widgets, or VICReg-style variance regularization) so the encoder cannot drop the controls. Ties to the [dinov2](dinov2.md) pre-commit probe.
3. **Plan short-horizon receding-horizon image-goal control, not long autoregressive dreams** — long-horizon drift + image-goal (vs language) are V-JEPA-2-AC's own open problems and will be worse on discrete UI dynamics.

**Sources:** [LeCun 2022](https://openreview.net/pdf?id=BZ5a1r-kVsf) · [I-JEPA 2301.08243](https://arxiv.org/abs/2301.08243) · [V-JEPA 2404.08471](https://arxiv.org/abs/2404.08471) · [V-JEPA 2 2506.09985](https://arxiv.org/abs/2506.09985). *Flag: some LeCun-PDF phrasings are faithful paraphrase, not confirmed verbatim; V-JEPA-2-AC per-task %s approximate.*
