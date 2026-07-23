# WHAM / Muse (Microsoft Research + Ninja Theory, *Nature* 2025) — Deep Read for Diogenes Lab

> Deep-dive note · sources: [Nature s41586-025-08600-3](https://www.nature.com/articles/s41586-025-08600-3) · [MSR Muse blog](https://www.microsoft.com/en-us/research/blog/introducing-muse-our-first-generative-ai-model-designed-for-gameplay-ideation/) · [WHAMM article](https://www.microsoft.com/en-us/research/articles/whamm-real-time-world-modelling-of-interactive-environments/) · [HF microsoft/wham](https://huggingface.co/microsoft/wham). Compiled 2026-06-29. See survey §2/§6/§7. **Our IP-clean first-party-data blueprint — but it had action labels we lack.**

## 1) Problem & core idea
WHAM ("**W**orld **and** **H**uman **A**ction **M**odel"; product **Muse**) generates game **visuals, controller actions, or both**. The "**and**" is load-bearing: unlike a pure pixel world model (Genie, GameNGen), WHAM jointly models the **observation stream and the human action stream** in one sequence → (a) roll out frames given frame+action (world model), (b) predict the action a player *would* take (policy), or (c) both jointly. Goal is **gameplay ideation**, not photoreal. Three evaluated properties (verbatim in Nature): **consistency, diversity, persistency**.

## 2) Architecture — precise
- **Visual tokenizer:** "~**300M ViT-VQGAN**" → each **300×180 image = 540 discrete tokens**. Codebook size not surfaced — *flag unverified*.
- **Action tokenizer:** Xbox controller discretized — "**x/y of left & right joysticks into 11 buckets**" + button/stick combos (~16 inputs) → a small fixed token set appended **after** each frame's image tokens.
- **Backbone:** **decoder-only causal transformer**, next-token prediction over an **alternating sequence [540 image tokens][action tokens][540 image tokens]…**. This interleaving is the crux — observations+actions are one AR stream, so action-conditioning is "free."
- **Sizes/context:** released **200M & 1.6B** (paper sweep 15M–894M; the "206M" in common summaries is *not* exact → **200M**). **Context = 5,560 tokens = 1 s = 10 (obs, action) pairs.** Blog's "minute-long consistent generations" = rollout length, not context.

**WHAMM (real-time follow-up):** swaps AR decoding for **MaskGIT parallel decoding** → **10+ fps real-time at 640×360**. ViT-VQGAN patch 20 → **576 tokens/640×360**. Two-stage **~500M Backbone + ~250M Refinement**. **Context only 0.9 s (9 frames).** Trained on **Quake II**, "**only 1 week of data**" with pro testers (vs 7 years for WHAM).

## 3) Data — critical (this is the precedent)
- Game: Ninja Theory's **Bleeding Edge** (Xbox 4v4, 2020).
- Volume: "**over 1 billion observation, action pairs**" / **>7 years continuous play** (blog); Nature: **~500,000 trajectories ≈ 1.4 B frames**, all 7 maps.
- Players: **27,990**. Resolution: **300×180**.
- **Action capture = first-party controller logging.** Because MS/Ninja Theory own Bleeding Edge, they instrumented the client to log **exact controller input** per frame → the (obs, action) pairing is **ground-truth, not inferred**.
- Open-sourced: **200M + 1.6B weights**, the **WHAM Demonstrator**, a **sample dataset** (test split only) — **not** the full ~1 B-pair corpus. License: **MSR License (academic only)**.
- Consent: HF card says "**one year's anonymized gameplay**"; **no explicit player-consent statement published** — *flag*.

## 4) Compute
**98 × H100 × 5 days** for WHAM-1.6B — on the **HF model card** + secondary coverage. **MSR blog softens to "up to ~100 GPUs"**, no day count. Discrepancy is presentational (rounds 98→~100). **Nature body didn't expose the exact GPU/day figure** (likely Methods/Extended Data) → treat **98×H100×5d as model-card-grade, not paper-quoted**. ≈ **490 H100-days ≈ ~12k H100-hours** for 1.6B on ~1.4B frames.

## 5) Limitations (stated, HF card verbatim)
"**Limited context length (10s)**"; "**Limited image resolution (300×180)** … fixed"; "**Inference … too slow for real-time**"; "**Trained on a single game, very specialized.**" The "~1 image/sec" figure common in summaries is the WHAMM blog's *comparative* characterization of WHAM's slow AR inference — **not a precise paper number** (precise: context = 1 s / 10 frames at 10 Hz playback; inference "too slow for real-time"). Persistency needs **multiple input frames (5+ > 1)**.

## 6) FOR OUR PATH (Diogenes Lab)
**The template fits; one assumption breaks.** WHAM proves **first-party-telemetry → obs+action world model** end-to-end and is IP-clean precisely because MS owned Bleeding Edge — exactly our dodge (own companion/game video, no third-party game IP). **But WHAM had ground-truth action labels from controller logging — we do not capture input** (survey §7.4). WHAM's elegance (interleave real action tokens, predict next token) is **unavailable to us**: screen-only video gives the observation stream but a **missing action stream**.

**3 concrete takeaways:**
1. **We cannot replicate WHAM directly — we need latent actions.** Insert a learned action representation (VQ-VAE over frame-pair deltas, à la Genie/LAPA) *between* frames to synthesize the action tokens WHAM got free from controllers. WHAM = the architecture (ViT-VQGAN + interleaved decoder-only AR); latent-action inference = the bridge. Plan a small **labeled-input pilot** (instrument *our own* client to log inputs on a subset, separately consented) to validate the latent space against truth — copying WHAM's first-party logging where we *can*. (This is the same pilot the VPT route wants.)
2. **Size Phase-1 from these anchors.** WHAM-1.6B = **~98 H100 × 5 d (~12k H100-hrs) on ~1.4 B frames**. A **200M-class** model is the right Phase-1 target (it shipped & works); a latent-action 200M model on tens of millions of frames should land in the **low-thousands of H100-hours (~$5–20k cloud)** — budget one validating run + 2–3 ablations, not a 1.6B from scratch.
3. **Match WHAM's data discipline.** **300×180 was sufficient** for dynamics — **start low-res** (resolution is their #1 limitation, not a prerequisite). Build the corpus as **(frame, [latent]action) pairs at ~10 Hz, ~1 s / 10-frame context**, and lock down **anonymization + explicit consent up front** — the one place WHAM's public posture is thin and our companion-data setting is far more sensitive (ties to the consent gate).

**Net:** WHAM = our IP-clean blueprint + compute/data yardstick; the delta we must engineer is **latent action inference** to replace the controller logs we won't have.
