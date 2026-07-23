# VPT (Video PreTraining): Deep Read for Diogenes Lab's "Game Video → Actions" Path

> Deep-dive note · Baker et al., [arXiv:2206.11795](https://arxiv.org/abs/2206.11795), NeurIPS 2022; read from the actual PDF (cdn.openai.com/vpt/Paper.pdf). Compiled 2026-06-29. See survey §5/§7. **The most battle-tested "game video → actions" recipe — and the source of our "~100h pilot" number.**

## 1) Problem & core idea
Web video shows *what happened on screen*, never *which keys/mouse moved* — sequential-decision domains lack action labels. VPT = **semi-supervised imitation**: collect a *small* labeled set of (video + recorded input), train an **Inverse Dynamics Model (IDM)** that infers actions from frames, use it to **pseudo-label a web-scale unlabeled corpus**, then **behavior-clone** a foundation policy. Key bet: **inverting dynamics is far easier/more data-efficient than modeling human behavior** → the IDM needs orders of magnitude less labeled data than a policy would.

## 2) Method — precise
**(a) IDM.** **Non-causal** — predicts `a_t` from *past AND future* frames `p(a_t|o_1…o_T)`. Input = **128 consecutive 128×128 frames**, one action/frame. First layer a **3-D conv** (temporal kernel 5 → sees t−2…t+2, "extremely important"), then non-causal ResNet → Transformer. **~0.5B params.** Action space = native human interface @**20 Hz** (binary keys + foveated-binned relative mouse). **Accuracy: 90.6% keypress, 0.97 R² mouse.** Trained 20 epochs, **4 d × 32 A100**.
**(b) Contractor seed.** Upwork contractors @$20/h recorded screen + keys + mouse. The headline IDM used **1962 hours**. *(Total project ~4,500 h, ~$160k.)* **Crucial nuance:** they *project* most results could be had with "**$2000 worth of data**" — a projection from the ablation, **not what they used** (best IDM = 1962 h ≈ $40k). Don't conflate.
**(c) Unlabeled corpus.** Web search → **~270k h** raw → contractor-trained clean/unclean classifier → **~70k h "clean"** (web_clean).
**(d) Foundation BC.** 0.5B params, 30 epochs, **~9 d × 720 V100**. Zero-shot chops trees, hunts, crafts crafting tables.
**(e) RL fine-tune.** PPG + **auxiliary KL-to-frozen-prior** (prevents catastrophic forgetting). **Iron pickaxe >80%, diamonds ~20%, diamond pickaxe 2.5%** of 10-min episodes — first agent to craft diamond tools. From random init, RL gets ~nothing — unlearnable without the prior.

## 3) Data efficiency — THE key numbers
- **IDM vs BC on the *same* labels:** IDM is **~2 orders of magnitude more data-efficient** than a BC policy on identical contractor data — the pipeline's central justification.
- **How little labeling works (§4.6, Fig. 9 — the number we care about):** IDMs on **≥10 h** already enable some crafting; rate climbs steeply to **100 h, then plateaus**. Crafting tables emerge at **≥50 h**. Verdict verbatim: *"we could reduce that number [1962 h] to as low as **100 hours**."*
- **Foundation-data scaling:** zero-shot crafting only emerges at **>5,000 h** pseudo-labeled; stone tools only at full ~70k h.

## 4) Limitations
(i) **Needs *some* labels** (IDM still needs real video+input, ≥~100 h useful). (ii) **Same-domain assumption** (one game; cross-title shift untested). (iii) **Loss ≠ downstream performance** (slow iteration). (iv) **Web-video provenance** — scraped YouTube, no licensing/consent framework. (v) **Weak steerability**.

## 5) FOR OUR PATH (Diogenes Lab: unlabeled game/companion video, no input capture)
VPT is **the most battle-tested "game video → actions" recipe**, but it has the gate we currently fail: **it needs a labeled seed (input capture)**. The good news (§4.6) is *how small* the seed can be.

- **Minimal consented input-capture pilot.** A lightweight recorder (frame buffer + key/mouse log at native rate) + a **separately-consented** session program: target **~100 hours** of (screen + input) on the *exact* title/build, a handful of operators (~$ low-four-figures + tooling). 100 h is the empirical knee; <50 h and crafting-equivalent skills don't emerge; >100 h flattens. Consent explicit, scoped to action-telemetry, **separate from the unlabeled-video corpus**. *(Input capture is a separate, stronger-consent track.)*
- **Supervised IDM vs unsupervised latent-action — the real trade-off.** VPT's **supervised IDM is robust** (90.6%/0.97) and gives a *real, decodable* action space, but **needs labels**. Label-free latent-action methods (Genie/LAPO/LAPA, Dreamer 4) need **no input capture**, but [latent-action-failure](latent-action-failure.md) (Nikulin 2502.00379) shows they're **distractor-fragile** — busy companion screens (animated avatars, chat, ads) are exactly where they collapse without some ground-truth supervision. Neither extreme is free: VPT pays in labels; pure latent pays in fragility.
- **Recommended hybrid.** Capture the **~100 h consented seed** → train a **VPT-style supervised IDM** (robust, decodable) → pseudo-label the corpus → BC a prior — **AND** use that same seed as the **2.5% supervisory signal that stabilizes a latent-action model** (per Nikulin), scaling to corpus regions/titles the IDM didn't cover. **The seed is dual-use: IDM trainer + latent-action regularizer.**

**3 takeaways.** (1) **~100 h of consented (video+input) is the unlock** — VPT's own ablation says 1962 h was overkill; budget a small pilot, not a labeling factory. (2) **Non-causal IDM is the trick** — past+future frames is why so few labels suffice; keep it offline (pseudo-labeling, not real-time). (3) **For companion screens, go hybrid, not pure-latent** — busy UIs are the distractor regime where label-free latent breaks; spend the small label budget to keep it robust.

**Source:** [arXiv 2206.11795](https://arxiv.org/abs/2206.11795) · [PDF](https://cdn.openai.com/vpt/Paper.pdf). *(OpenAI blog returned 403 — paper supersedes it.)*
