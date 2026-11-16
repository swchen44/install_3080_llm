# MiniMax H3 speed canary on RTX 3080 20GB

Date: 2026-11-15 (Asia/Taipei)  
Goal: identify H3 speed options that preserve the current 20-step quality baseline.  
GPU limit: 250 W throughout. No model weights were downloaded.

## Finding

Comfy Kitchen attention is available in the installed ComfyUI 0.45.0 / comfy-kitchen 0.2.41 environment. The small canary showed a 21.1% sampler-time reduction. More importantly, a full-size matched 3D run at 1344×768 and 294 frames reduced sampler time from 1:28:39 to 39:49 (2.23× throughput) and total ComfyUI time from 1:31:14 to 42:42 (2.14× throughput). The 250 W limit remained configured.

The full-size same-seed clips retain the same characters, duel, lighting, and scene style in the sampled frames, with no obvious collapse or structural artifact. Motion paths and poses differ; mean frame SSIM was 0.8391. This is a different trajectory, not pixel-identical output. The contact sheet covers six frames across the clip, not every frame or an audio-quality assessment. Kitchen is a strong speed option when this level of variation is acceptable.

## Research reviewed

| Source | User report / measured result | How it applies here |
|---|---|---|
| RTX 3080 20GB community post: https://lcz.me/topic/1306/4 | A modified GA102 / sm86 owner reports H3 FL2VA runs and a 4-step Turbo + SageAttention speedup. The post's task, steps, and quality target differ from our six-reference R2V baseline. | Closest GPU report; supports testing attention, but not a direct speed prediction. |
| Hugging Face MiniMax-H3 discussion #26: https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/26 | Users report SageAttention and EasyCache/Spectrum benefits, with conflicting results. A separate 5090 report found no Kitchen-attention gain. | Shows backend gains depend on GPU and workflow; validates measuring locally. |
| Reddit A/B discussion: https://www.reddit.com/r/comfyui/comments/1vrxppw/minimax_h3_speedup_test_turbo_lora_vs_kitchen/ | Reports differ on Turbo LoRA quality. Some users see softened faces/motion or audio issues; others recommend Kitchen attention as a routine speed path. | Supports keeping Turbo out of the first quality-focused experiment. |
| FirstBlockCache project: https://github.com/duckyshell/ComfyUI-MiniMaxH3-FirstBlockCache | Its RTX 5090 0.5 MP / 5 s / 20-step test reports 1.25× Safe and 1.44× Fast cache-only speed; quality metrics describe trajectory drift, and the author says 30-series compatibility is expected but not benchmarked. | Candidate for a later, separate RTX 3080 test. Not installed in this experiment. |
| ComfyLab RTX 3090 H3 test: https://comfylab.dev/blog/workflows/minimax-h3-comfyui-speed-vram-rtx-3090/ | Reports Sage Attention reduced render time by 27% for its 4-step workflow; later multi-GPU runs found same-seed Sage output close to default while Sol-Attn changed composition. | Ampere-adjacent, but different hardware and a Turbo workflow. Do not extrapolate the percentage. |
| Official ComfyUI H3 guide: https://docs.comfy.org/tutorials/video/minimax/minimax-h3 | Documents the native H3 workflows and available `turbo_mode` controls. | Reference for the model graph; this canary intentionally leaves the Turbo branch disabled. |

## Local matched canary

Both runs used the same 3D lcz.me challenge prompt, six reference images in the original order, INT8 ConvRot Ref2VA DiT and text encoder, FP16 video VAE, FP32 audio VAE, 20 steps, `res_multistep` sampler, `simple` scheduler, fixed seed `261662374822965`, reference size `match`, and 250 W GPU power limit. Resolution was intentionally reduced to 608×352 (the 0.2 MP selector setting); duration input was 2 seconds, which the H3 frame rule rounds to 56 frames / 2.333 seconds. This short canary isolates speed and checks gross scene changes; it is not the requested final-quality resolution.

| Backend | Denoising / sampler | Sampler wall time | Total ComfyUI prompt time | GPU peak draw | Peak VRAM |
|---|---|---:|---:|---:|---:|
| Default PyTorch | 20 steps / res_multistep | 57.2 s | 142.96 s | 249.95 W | 19,790 MiB |
| Comfy Kitchen INT8 attention | 20 steps / res_multistep | 45.1 s | 128.74 s | 249.52 W | 19,789 MiB |

### Full-size matched run against the saved PyTorch baseline

The existing 3D master output uses the same prompt, six references, seed `261662374822964`, 1344×768, 294 frames, 20 steps, INT8 ConvRot weights, and VAEs. The new Kitchen run changed only the process attention backend.

| Backend | Sampler time | Total ComfyUI time | Mean GPU draw | Peak GPU draw | Peak VRAM | Peak temperature |
|---|---:|---:|---:|---:|---:|---:|
| Default PyTorch | 1:28:39 | 1:31:14 | 247.37 W | 252.25 W | 19,799 MiB | 64°C |
| Comfy Kitchen INT8 attention | 39:49 | 42:42 | 240.13 W | 252.62 W | 19,788 MiB | 65°C |

The configured limit was 250 W for both. Telemetry can sample brief values above the configured limit. Kitchen used 2,389 s sampling and 2,562 s total execution, versus 5,319 s and 5,474 s in the saved PyTorch baseline. The output is native 12.25 s (294 frames) with 32 kHz stereo audio; the separately trimmed 12.00 s deliverable passed the existing video verifier.

Sampler time is read from ComfyUI's denoising progress; total time is ComfyUI's `Prompt executed in` line. The process restarted between arms and the same seed was used. Startup/model-loading behavior and OS file cache can affect these short total-time figures. Per-step improvement is a better indicator of the speed effect for this test.

Outputs (both include native stereo audio):

- PyTorch: `/home/swchen/Downloads/ai/tools/comfyui-linux/ComfyUI-102350eb949bca599e450a904f0562ad3f551279/output/video/h3-attention-minimax-h3-lcz3045-3d_00001_.mp4`
- Comfy Kitchen: `/home/swchen/Downloads/ai/tools/comfyui-linux/ComfyUI-102350eb949bca599e450a904f0562ad3f551279/output/video/h3-attention-minimax-h3-lcz3045-3d_00002_.mp4`
- Contact sheet: `docs/research/assets/h3-attention-canary/contact-sheet.png`
- Mean frame SSIM, PyTorch vs Kitchen: 0.817871. This measures frame alignment; it is not a perceptual-quality score.
- Output SHA-256: PyTorch `e89a353102fc968ca2f9d9c5cf5f5e115f48e9dcad28cf4ae9c8d3d00899bd6e`; Kitchen `c8351b2ca2364168471670bbe84ba2b112f76559da3effab0e67970c39885494`.

Full-size 3D outputs:

- PyTorch baseline: `/home/swchen/Downloads/ai/tools/comfyui-linux/ComfyUI-102350eb949bca599e450a904f0562ad3f551279/output/video/lcz3045_3d_00001_.mp4` (SHA-256 `bc440fba1aac2990169544e83d9541ca5c8a4253a5a1a8a78388e5cf9842edee`).
- Comfy Kitchen native clip: `/home/swchen/Downloads/ai/tools/comfyui-linux/ComfyUI-102350eb949bca599e450a904f0562ad3f551279/output/video/h3-attention-minimax-h3-lcz3045-3d_00003_.mp4` (SHA-256 `038a09cc24f502b02e229fcb86dc6b5fd13f20b56e124de95f2ddf2f368aa846`).
- Comfy Kitchen 12-second verified copy: `/home/swchen/Downloads/ai/tools/comfyui-linux/ComfyUI-102350eb949bca599e450a904f0562ad3f551279/output/video/h3-attention-3d-kitchen_12s.mp4` (SHA-256 `c973a0f76d758a268759c3a291fa4e9271038a66917023b7d8d0447cd8da1c24`).
- Full-size contact sheet: `docs/research/assets/h3-attention-fullsize/contact-sheet.png`; same-seed mean frame SSIM `0.839112`.

## Reproduction artifacts

- Saved API workflows: `docs/research/workflows/h3-attention-canary.api.json` (short canary) and `h3-attention-fullsize-kitchen.api.json` (full-size Kitchen run).
- UI-to-API conversion: `docs/research/workflows/h3-ui-to-api.py`.
- Run ComfyUI with per-second GPU telemetry and a 250 W cap guard: `docs/research/workflows/run_h3_attention_canary.sh pytorch` or `... kitchen`.
- Server logs: `docs/research/logs/18-h3-attention-20261115-223627-pytorch.log` and `18-h3-attention-20261115-223958-kitchen.log`.
- GPU telemetry: matching `docs/research/logs/19-h3-attention-gpu-*.csv` files.
- Full-size hashes, ffprobe metadata, and per-frame SSIM evidence: `docs/research/logs/20-h3-attention-fullsize-evidence.txt`.
- API request: `POST http://127.0.0.1:8188/prompt` with the saved JSON's `prompt` object. Both runs used the identical request graph.
- Seed used for both outputs: `261662374822965`.

## Recommendation and next step

### Power limit question — 2026-11-16

This GPU reports a 320 W default power limit and is currently configured to 250 W. During the full-size Kitchen run the GPU was often near 250 W at full utilization; a higher cap could allow higher clocks, but its H3 speed impact cannot be quantified from this single-power dataset. Power is not proportional to performance, and memory, offload, cooling, and CPU can limit gains. The 42:42 result is measured at 250 W only. An RTX 3090 owner reports workload-dependent behavior when tuning power across diffusion and other tasks: https://www.reddit.com/r/LocalLLaMA/comments/1egvoqj/rtx3090_power_tuning_results_on_llm_vision_tts/ . A 320 W H3 run has not been performed; the established 250 W limit remains in force.

Community power-cap data, researched 2026-11-16 (no local power experiment): https://aibacon.net/posts/rtx-3090-gpu-unlock-benchmark-250w-qwen3-8-27b-prefill-21-54-percent-ltx-2-5-video-18-percent-faster-less-energy-decode-flat.html reports a stock RTX 3090 H3 chain, three segments / 729 frames / 1184×672: 250 W 3,636 s and 223 Wh; 300 W 3,340 s and 246 Wh; 350 W 3,217 s and 274 Wh. Thus 350 W was 11.5% lower time than 250 W while measured GPU energy was 22.9% higher. Their stock LTX-2.5 three-part 30-second workload reports 624 / 582 / 568 s at 250 / 300 / 350 W respectively. The same source also reports a separately unlocked card; those figures must not be confused with the stock-card power comparison. Results are self-reported, mostly single runs, RTX 3090 rather than this 3080, and not the same H3 workflow or 320 W limit; they do not predict this machine's time. The researcher reports GPU energy rather than wall energy.

Another RTX 3090 user reported Stable Diffusion about 3.6 s/iteration at 350 W, 4.1 s at 80% (~280 W), and 4.4 s at 70% (~245 W): https://www.reddit.com/r/StableDiffusion/comments/17sv5ty/do_nvidia_30_series_gpus_experience_overheating/ . This is a different image workload and the author calls the measurements rough. No credible matched 3080 250 W versus 320 W H3 video result was found in this search.

Keep Turbo LoRA disabled for the quality-first master workflow for now. Multiple user reports associate low-step Turbo with softer or less stable motion, faces, colors, or audio, while quality varies with LoRA version, sampler and task.

For H3 runs where a changed motion trajectory is acceptable, enable Comfy Kitchen attention: the full-size test cut total 3D generation time by about 53% while retaining comparable scene and visual coherence in the sampled frames. Start ComfyUI with `docs/research/workflows/launch_comfyui_logged.sh --use-ck-attention`; the script records the flag and keeps the 250 W guard and telemetry. Keep default PyTorch attention when matching the exact previous motion matters. The verified Kitchen 12-second copy is ready; listen through the audio and review the full clip before using it as a final. A 3080 FirstBlockCache Safe test remains optional; its published timing is from an RTX 5090.
