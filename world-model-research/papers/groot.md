# NVIDIA GR00T N1 (+ DreamGen / GR00T-Dreams) — Deep Read for Diogenes Lab

> Deep-dive note · [arXiv 2503.14734](https://arxiv.org/abs/2503.14734) (GR00T N1) + [DreamGen 2505.12705](https://arxiv.org/abs/2505.12705) + GR00T N1.5 (GEAR, Jun 2025); verified, vendor claims disambiguated. Compiled 2026-06-29. See survey §4/§5. **Second production template for our latent-action bridge + the "WM-as-data-factory" route.**

## 1) Problem & core idea
Robot data is scarce/embodiment-locked. GR00T N1 = NVIDIA's open VLA foundation model (Apache-2.0) using a **data pyramid** (abundant action-less human/web video → sim + neural-generated video → scarce real teleop) fused into one cross-embodiment policy via a **dual-system** design: slow **VLM "System 2"** + fast **diffusion-transformer "System 1"**.

## 2) Architecture — precise
- **System 2** = **Eagle-2 VLM** (SmolLM2 + SigLIP), 224² → 64 tokens/frame, ~10 Hz on L40; taps **mid-layer (12th) LLM embeddings**.
- **System 1** = **Diffusion Transformer + flow-matching** action head, cross-attends System-2 tokens, **embodiment-specific encoders/decoders**; action chunk **H=16**, **K=4** denoise steps → 16-action chunk = **63.9 ms** → ~**120 Hz** control. Jointly trained end-to-end. **Total 2.2B (1.34B VLM).**
- **Latent action + IDM = the cross-embodiment trick (= LAPA).** A **VQ-VAE** encodes (xₜ, xₜ₊H) → discrete latent zₜ; decoder reconstructs xₜ₊H from (xₜ, zₜ). Action-less video → a **pseudo-embodiment** whose latent actions are flow-matching targets. Separately an **IDM** infers pseudo-actions for sim/neural video. **Ablation: LAPA wins low-data; IDM overtakes as data grows** (higher pseudo-label quality).

## 3) Data engine — two distinct NVIDIA engines (don't conflate)
**(a) Isaac GR00T Blueprint (GTC Mar 2025)** — fed N1. Cosmos **Transfer** + Omniverse + **DexMimicGen** → **780k sim trajectories ≈ 6,500 h in 11 h**; **synthetic+real = +40% over real-only** for N1. *(The 780k/11h & +40% are THIS blueprint, not DreamGen.)*
**(b) DreamGen / GR00T-Dreams (the loop relevant to us):** fine-tune a video WM on a little target-robot video → prompt with image+language → hallucinate "dreams" → **IDM/LAPA extracts pseudo-actions** → train policy on **"neural trajectories."** Paper WM = **WAN2.1**; blueprint = Cosmos Predict-2 + Cosmos Reason. NVIDIA claims **"GR00T N1.5 in 36 h vs ~3 months manual."** **Real data still needed:** DreamGen co-trains **1:1 with as few as 10–13 real traj/task**; neural-only underperforms. **Synthetic augments, real anchors — never zero real.**

## 4) Results
- Sim: RoboCasa 32.1% (vs DP 25.6); DexMimicGen 66.5% (vs 56.1). Real GR-1: **76.8%** avg (vs DP 46.4); **at 10% data 42.6% vs 10.2%**.
- Neural-trajectory ablation: +4.2/+8.8/+6.8% (RoboCasa 30/100/300-demo). DreamGen generalization: pick-place-only N1 = **0%** novel verbs → DreamGen **43.2%** seen / **28.5%** unseen env, 22 novel behaviors.
- N1.5 (frozen Eagle-2.5 + FLARE): language-following **46.6→93.3%**.

## 5) Limitations / vendor-claim caveats
"**N1.5 in 36 h**" mixes generation wall-clock with "development" — marketing, rode on 1.5k-L40 / 1k-H100 fleets (the 240k-RoboCasa set alone = 54 h on 1500 L40s). 780k/+40% = the GTC Cosmos-Transfer blueprint, *not* DreamGen. Pseudo-action quality caps gains; eval is short-horizon, NVIDIA-favorable embodiments; heavy Cosmos/Omniverse coupling.

## 6) FOR OUR PATH
- **Second template for the bridge.** GR00T validates **LAPA's VQ-VAE latent-action codebook** as production-grade and adds the **LAPA-early / IDM-late crossover** + a *unified* latent space across human+sim+real. **Takeaway 1: build the codebook on our screen video like LAPA, but plan an IDM upgrade once we have any real-action pairs** — that's where GR00T's quality gains came from.
- **Could our game WM be the "dreamer"?** Yes — exactly the DreamGen role. **Takeaway 2: our game WM can "dream," but DreamGen needs a *robot-grounded* WM (WAN2.1/Cosmos fine-tuned on the embodiment); game-pixel dreams give latent actions, not metric robot actions → the IDM must be trained on *our* small real-robot set to ground them.**
- **Honest caveat, confirmed.** GR00T/DreamGen **never remove real teleop** (best = 1:1 co-train, 10–13 real traj/task). **Takeaway 3: budget first-party real teleop as the non-negotiable anchor; treat WM dreams + latent actions as a multiplier (their +40% / 0%→43% deltas), not a replacement; copy DreamGen Bench (instruction-following + physics-alignment) as a go/no-go gate** (WM-bench score correlated with downstream policy success).

**Sources:** [GR00T N1](https://arxiv.org/abs/2503.14734) · [DreamGen](https://arxiv.org/abs/2505.12705) · [GR00T N1.5](https://research.nvidia.com/labs/gear/gr00t-n1_5/). *Flags: "36h"/"+40%" are blog claims w/o released controlled ablations; repo now at N1.7 (Apr 2026) — N1/N1.5 specs above are historical record.*
