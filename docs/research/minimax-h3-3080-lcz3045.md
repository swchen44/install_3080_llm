# MiniMax H3 on RTX 3080 20GB — lcz.me topic 3045

Research and experiment preparation log. Updated 2026-11-15 (Asia/Taipei).

## Acceleration follow-up — Comfy Kitchen attention

After the original 20-step 3D and 2D outputs, a matched full-size 3D run tested Comfy Kitchen INT8 attention on the RTX 3080. With the same prompt, six references, seed, 1344×768 resolution, 294 frames and 20 steps, sampler time fell from 1:28:39 to 39:49; total ComfyUI time fell from 1:31:14 to 42:42. The generated 12-second copy passed the existing 288-frame verifier. Six sampled frames retained the same scene and style with different action trajectories; full-frame SSIM was 0.839112, which measures alignment rather than perceptual quality. Keep this as a faster option when changed motion details are acceptable. Logs, video hash, workflow and community sources: [H3 speed research](minimax-h3-speed-canary-20261115.md) and [HTML summary](minimax-h3-speed-canary-20261115.html).


## Final results — 2026-11-15

Both requested style variants completed successfully on the RTX 3080 with the 250 W power limit configured. Each used the same six reference images, prompt except for the style wording, fixed seed, INT8 ConvRot DiT and text encoder, 20 sampling steps, 1344×768 output, and no Turbo LoRA. The original ComfyUI output preserves the valid 294-frame (12.25 s) H3 clip; the separate final file trims six frames to exactly 288 frames / 12.000 s. The video verification script passed all checks for both final clips.

| Style | Sampler | ComfyUI total | Final file | Subjective review of six frames (0–10 s) |
|---|---:|---:|---|---|
| 3D CGI | 1:28:39 | 1:31:14 | `lcz3045_3d_12s.mp4` | Cinematic volumetric rendering, strong flame trails and depth; poses and small details shift between shots. |
| 2D anime | 1:29:05 | 1:31:18 | `lcz3045_2d_12s.mp4` | Clearer cel-shaded anime finish and strong orange action arcs; poses, faces and weapon details shift between sampled shots. |

The 2D sampler was 26 seconds slower than 3D; total ComfyUI execution differed by four seconds. This single-seed, single-prompt comparison does not establish a general speed or quality advantage. Visually, both communicate the duel and style prompts well in the sampled frames; 2D more directly matches the traditional-anime wording, while 3D looks more volumetric.

### Measured resources

Telemetry was sampled once per second during each ComfyUI execution window. Both runs held GPU load at 100% through sampling, with the 250.00 W limit configured. Sensor readings can briefly exceed the configured limit by a small amount.

| Metric | 3D | 2D |
|---|---:|---:|
| Mean measured GPU draw | 247.37 W | 247.88 W |
| Maximum measured GPU draw | 252.25 W | 252.38 W |
| Peak VRAM | 19,799 MiB | 19,945 MiB |
| Peak GPU temperature | 64°C | 64°C |
| Minimum host RAM available | 63.8 GiB | 63.6 GiB |
| Minimum free swap | 7.63 GiB | 7.63 GiB |
| OOM | No | No |

The active time windows include model initialization and VAE decode, so mean power is lower than the steady sampling draw. Host RAM peaked near 62.1 GiB used during the 2D run; swap stayed almost entirely free.

### Deliverables

Output directory: `/home/swchen/Downloads/ai/tools/comfyui-linux/ComfyUI-102350eb949bca599e450a904f0562ad3f551279/output/video/`

- [3D CGI final clip](</home/swchen/Downloads/ai/tools/comfyui-linux/ComfyUI-102350eb949bca599e450a904f0562ad3f551279/output/video/lcz3045_3d_12s.mp4>) — SHA-256 `09013fb27f1733b0ed44f396ec2ab3a0f20f711e0a46fc290580b6992ceb3ef5`.
- [2D anime final clip](</home/swchen/Downloads/ai/tools/comfyui-linux/ComfyUI-102350eb949bca599e450a904f0562ad3f551279/output/video/lcz3045_2d_12s.mp4>) — SHA-256 `7e45054751b328f8fa383d08fe96e052c05937c187e311663cfeb282e6fd8b4b`.
- [3D six-frame contact sheet](assets/minimax-h3-lcz3045/lcz3045-3d-contact-sheet.png) · [2D six-frame contact sheet](assets/minimax-h3-lcz3045/lcz3045-2d-contact-sheet.png).
- Full source and final file hashes: [video manifest](logs/17-video-manifest.sha256).

Both untouched 12.25 s sources remain beside the final files. The checksums, workflow JSON, environment log, GPU/memory telemetry, ffprobe metadata, and six-frame reviews are retained in `docs/research/` for reproduction.

## Objective

Reproduce the lcz.me MiniMax H3 challenge on this machine, prioritizing visual quality on an RTX 3080 20GB capped at 250 W. Produce two 1344×768 reference-to-video results using all six supplied images: one 3D CGI style and one traditional 2D anime style. Preserve the challenge prompt and record workflow JSON, environment, run times, GPU power, logs, output metadata, and post-processing.

Challenge: <https://lcz.me/topic/3045>

## Challenge specification verified from the post

- Required model: MiniMax H3.
- Output: two videos, each nominally 12 seconds at 1344×768.
- Inputs: three Kenshin references and three Shishio references.
- Prompt is identical except for the style switch: `3D CGI animation` or `2D traditional anime`.
- Submission evidence requested: hardware, workflow screenshot or JSON, acceleration settings, complete generation log and total time.

The challenge post is the authority for the target. Keep its English prompt unchanged; the two exact variants are in `docs/research/prompts/`.

## Runtime constraint: 12 seconds is not an exact native frame length

ComfyUI's native H3 node uses 24 fps and snaps the frame count to `17k+5`. The nearest valid frame count at or above 12 seconds is 294 frames, or 12.25 seconds. To submit a 12.00-second file while preserving a valid native H3 generation, generate 294 frames and trim six frames (0.25 seconds) from the end with ffmpeg. Keep both original and trimmed outputs, and record both durations. Verify with `ffprobe` before submission. Do not hide the trim in the generation-time number.

Source: ComfyUI native node schema and constraint: <https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py>.

## Hardware and local state

- GPU: NVIDIA GeForce RTX 3080, 20,480 MiB reported VRAM.
- Power limit: 250.00 W (confirmed with `nvidia-smi`; this remains the limit for experiments).
- Host RAM: 128 GiB per the established machine inventory.
- Free root filesystem after Q2 cleanup and H3 weight arrival: 110 GiB (`df -h /home/swchen`).
- Six challenge reference images are already stored at `docs/research/assets/minimax-h3-lcz3045/`; `manifest.json` records original source URLs, dimensions, byte counts, and SHA-256.
- The user placed both main H3 weights at `~/Downloads/ai/models/comfyui/ComfyUI/models/`. Their SHA-256 values match the official Comfy-Org files:
  - `diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors`, 20,970,379,616 bytes, `9255f52b6677845ad238f20dfaafa94727053694127ab7f255c048f0f9365779`.
  - `text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors`, 27,141,342,152 bytes, `bc2ced0fbea64757fa9acddccfc0b3f4819d1dcf1da6c124d690d368be283923`.
- Reuse these weights; the assistant has not downloaded any model larger than 10 GB.
- H3 video and audio VAEs were fetched from official Comfy-Org links and installed into the same model tree; both verified against official SHA-256 values and each is below 10 GB.
- The existing ComfyUI source archive was reused and extracted to `~/Downloads/ai/tools/comfyui-linux/ComfyUI-102350eb949bca599e450a904f0562ad3f551279`. Its tar SHA-256 is `32b4f0004223e622e20d71b2e48d4bd80110c15e861bd0d91f3b5212b913020c`; it contains the native H3 node. `extra_model_paths.yaml` points to the downloaded model directory so the weights are not copied.
- System Python 3.12 lacked venv support; `python3.12-venv` was installed with sudo. ComfyUI runs from the isolated venv at `~/Downloads/ai/tools/comfyui-linux/.venv`, using PyTorch 2.9.1+cu130, ComfyUI 0.45.0, and CUDA 13.0.
- Both requested videos completed; see Final results above. The earlier setup timeline below preserves the intermediate states as they were observed.

## Web evidence and what it supports

### Same GPU class and memory size

A lcz.me user reports an RTX 3080 20GB (modified GA102, sm86), ComfyUI 0.30 portable, Torch 2.9.1/cu130, and H3 FL2VA using pruned INT8 DiT plus NVFP4 text encoder. They report 5-second I2V at 768p in 541–604 s with 10-step baseline, and 279.7 s with 4-step Turbo LoRA plus SageAttention. This is useful proof that this unusual 20GB card can run H3. It is not a quality-first result for our task: it uses FL2VA, I2V, fewer reference images, and Turbo. Their post says the accelerated quality looked close to their 10-step baseline, but this is a single-user visual assessment, not a blind quality evaluation.

Source: <https://lcz.me/topic/1306/4>.

### Ampere reference data

A reproducibility report on an RTX 3090 24GB (Ampere, sm86) tests the pruned INT8 ConvRot DiT plus INT8 ConvRot text encoder. At 1376×768, 124 frames, 20 steps, it reports 90.2 s/step and about 33.3 minutes sampling time; at 243 frames and 0.8 MP, it reports 167.2 s/step. It also reports that NVFP4 operations were emulated on that Ampere setup and that SageAttention did not improve its measured H3 workload compared with xformers. These numbers are not predictions for our 20GB card; fewer VRAM and a 250 W cap may make it slower. They do show why resolution, frame count, and offloading must be logged.

Source and raw measurements: <https://github.com/Rinne414/ComfyUI-MiniMaxH3-Tools/blob/master/research/README.md>.

### Official ComfyUI workflow guidance

ComfyUI documents R2V support for reference inputs and native audio. Its open weights target about 1 megapixel, 24 fps, and up to about 15 seconds. The lcz challenge resolution is about 1.03 megapixels, close to this target. R2V can accept multiple reference assets. The MiniMax local-run guide says FL2VA can have better raw quality, while Ref2VA is the variant needed for the challenge's six images; choose Ref2VA for the main run because it satisfies the task's reference requirement.

Sources: <https://docs.comfy.org/tutorials/video/minimax/minimax-h3> and <https://github.com/MiniMax-AI/awesome-minimax-h3-integration/blob/main/docs/run-h3-locally.md>.

## Quality-first baseline proposal

Use the native ComfyUI H3 R2V workflow and the Ref2VA variant, with no Turbo LoRA or sparse-attention modification in the first baseline. Use the INT8 ConvRot DiT and INT8 ConvRot Qwen3-VL text encoder, FP16 video VAE, and FP32 audio VAE. The Ampere reproducibility report identifies INT8 ConvRot as a better-supported choice than NVFP4 on sm86. This is a conservative compatibility choice, not a claim that quality differences have been measured on this machine.

Initial baseline controls:

1. Set GPU power limit to 250 W and record it at start and end.
2. Use ComfyUI's official H3 R2V template and save the exact workflow JSON.
3. Load all six challenge images in the same order for both videos.
4. Keep the exact challenge prompt; change only the style parenthetical.
5. Use 20 denoising steps as the first quality-oriented baseline; preserve sampler, scheduler, seed, reference resize mode, and all other settings across the pair. Capture the actual workflow values in the run log rather than assuming template defaults.
6. Generate the valid 294-frame (12.25 s) clip, then make and verify a 12.00 s trimmed submission copy.
7. Record model hashes, ComfyUI commit/version, Python/Torch/CUDA versions, node versions, cold-start/model-load time, text-encode time if available, sampling time, VAE/audio decode time, total wall time, peak VRAM/RAM, GPU power and temperatures, and output `ffprobe` metadata.
8. After the baseline, consider a separate controlled speed/quality A/B with 8-step or 4-step Turbo. Never substitute it for the baseline without labeling it.

The 20-step and 294-frame settings are the proposed experiment settings, not measured outcomes. The lcz poster's reported 4-step speed does not establish that a 20-step six-reference 12-second render will meet a real-time or short-wait target. A 12-second, near-1MP H3 render may take a long time; first run should be treated as a throughput pilot.

## Main model weights received and verified

Both files above the 10 GB threshold are already available locally. Do not download them again:

1. Ref2VA INT8 ConvRot diffusion model — 21 GB, SHA-256 `9255f52b6677845ad238f20dfaafa94727053694127ab7f255c048f0f9365779`.
   - Page: <https://huggingface.co/Comfy-Org/MiniMax-H3/blob/main/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors>
   - Direct download: <https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors>
   - Local path: `~/Downloads/ai/models/comfyui/ComfyUI/models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors`
2. Qwen3-VL-32B INT8 ConvRot text encoder — 27.1 GB, SHA-256 `bc2ced0fbea64757fa9acddccfc0b3f4819d1dcf1da6c124d690d368be283923`.
   - Page: <https://huggingface.co/Comfy-Org/MiniMax-H3/blob/main/text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors>
   - Direct download: <https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors>
   - Local path: `~/Downloads/ai/models/comfyui/ComfyUI/models/text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors`

The optional NVFP4 text encoder is not part of this run. It would be another model larger than 10 GB and is not needed for the chosen INT8 baseline.

Required smaller files: FP16 video VAE (about 5.2 GB) and FP32 audio VAE (about 0.6 GB). Transfers are in progress:

- <https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors>
- <https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors>

The two main weights total about 48.1 GB decimal. The root filesystem now has about 110 GiB free, enough for the selected H3 weights, VAE files, and isolated runtime. The 128 GiB host RAM gives room for offloading but does not solve PCIe transfer time.

## Reference images

Image order and checksums are in `docs/research/assets/minimax-h3-lcz3045/manifest.json`. The prompt variants are in `docs/research/prompts/minimax-h3-lcz3045-3d.txt` and `docs/research/prompts/minimax-h3-lcz3045-2d.txt`.

## Reproducible challenge workflows

The challenge post requires MiniMax H3, 1344×768, two 12-second outputs, the six supplied references, and the same prompt with only the style changed. It also asks participants to provide hardware details, a workflow or JSON, acceleration details, and a complete run log with total time. The post says to upload videos to YouTube; this project report records local output and measurement evidence.

The official Comfy-Org R2V template was saved as `docs/research/workflows/video_minimax_h3_r2v.official.json` (SHA-256 `a79f1a8ae7d250f9da8b0f4e636e202526c37457b808e74fdf25de7ceed96574`). Paired workflows were prepared from it:

- `docs/research/workflows/minimax-h3-lcz3045-3d.json`
- `docs/research/workflows/minimax-h3-lcz3045-2d.json`
- Builder: `docs/research/workflows/build_lcz3045_workflows.py`

Both workflows use all six references in manifest order, 1344×768, 20 steps, fixed seed `261662374822964`, INT8 ConvRot DiT and text encoder, and the FP16 video VAE with FP32 audio VAE. They disable the template's optional Turbo LoRA. The workflow asks for 12 seconds; the native H3 frame grid rounds this to 294 frames (12.25 seconds at 24 fps), so the final local copy must be trimmed to exactly 12 seconds. Both workflows passed structural checks and were run in ComfyUI; final outputs and measurements are summarized above.

The official template and challenge requirements are linked in Sources below. The six reference file hashes are verified against the asset manifest.

Pre-run audit found that the official template's 0.4 MP Resolution Selector is connected to the H3 width and height inputs. Its connected values override the node's displayed 1344×768 defaults and would produce only 864×480. The workflow builder now sets the selector to 16:9, 0.984375 MP using ComfyUI's 1024×1024 pixel units, and a 32-pixel multiple; this resolves to exactly 1344×768. Both prepared JSONs pass the resolution calculation and reference-order check. No run used the incorrect template size.

The complete preflight checks are saved in `docs/research/logs/16-lcz3045-workflow-preflight.json`; rerun them with `python3 docs/research/workflows/verify_lcz3045_workflows.py`.

Machine inventory for the experiment: Intel Xeon E5-2666 v3 (10 cores / 20 threads), GeForce RTX 3080 with 20,480 MiB VRAM, NVIDIA driver 595.99.02, and 125 GiB host RAM. The root filesystem is a 452.7 GB Samsung NVMe partition with 104.7 GiB free at the latest inventory. Runtime versions are Python 3.12.3, ComfyUI source 0.45.0, and ffmpeg 6.1.1-3ubuntu5. The GPU power limit is 250 W.

## Sources

- Challenge requirements and exact prompt: <https://lcz.me/topic/3045>
- Official ComfyUI R2V workflow template: <https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json>
- Direct RTX 3080 20GB H3 experience (4-step/Turbo, NVFP4, SageAttention): <https://lcz.me/topic/1306/4>
- Official ComfyUI H3 guide: <https://docs.comfy.org/tutorials/video/minimax/minimax-h3>
- MiniMax integration hardware and model guide: <https://github.com/MiniMax-AI/awesome-minimax-h3-integration/blob/main/docs/run-h3-locally.md>
- Ampere RTX 3090 reproducibility measurements: <https://github.com/Rinne414/ComfyUI-MiniMaxH3-Tools/blob/master/research/README.md>
- Official Comfy-Org model inventory: <https://huggingface.co/Comfy-Org/MiniMax-H3>
- H3 frame grid in ComfyUI: <https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py>

## Environment and generation timeline

Final state: both local videos are generated, trimmed and verified. ComfyUI used the previously downloaded source and main model weights; only the sub-10 GB VAEs required downloads. Setup and per-run chronological checkpoints follow for reproduction. Historical statements in those timestamped checkpoints describe the system at that checkpoint, not its final state.

### Live status checkpoint — 2026-11-15 17:23 CST

- The video VAE partial file is 1,203,015,680 bytes of 5,207,808,496 bytes (23.1%). Its `curl` process is active. The audio VAE has not started; the shell command queues it after video completes.
- PyTorch 2.9.1/cu130 installation is still active in the isolated `.venv`; `pip` has not returned, so package installation is not yet verified complete.
- `ffmpeg` 6.1.1-3ubuntu5 is installed. The user model directory contains both verified main weights; no duplicate model download was started.
- Available disk is 107 GiB. The RTX 3080 remains capped at 250 W, idle at 14.45 W with 191 MiB VRAM used.
- No ComfyUI server or generation is running. This is environment setup only; no video result or speed/quality measurement exists yet.
- Active process IDs at this checkpoint: video VAE `curl` 74275; PyTorch `pip` 74787. See `docs/research/logs/12-comfyui-h3-setup.txt` for transfer URLs and environment paths.

### Live status checkpoint — 2026-11-15 17:30 CST

- Video VAE is 1,395,617,792 / 5,207,808,496 bytes (26.8%); `curl` PID 74275 is still active. Audio VAE has not started.
- PyTorch 2.9.1/cu130 install remains active as PID 74787. The requested packages are not yet installed in the venv.
- Both six-reference workflows and the original official R2V template are saved. All six reference image hashes match the manifest. Workflow structure checks confirm six connected references, 1344×768, 294 frames, 20 steps and a fixed seed.
- Free disk is 107 GiB. GPU remains capped at 250 W and idle. No ComfyUI run, generated video, timing or quality result exists yet.

### Live status checkpoint — 2026-11-15 17:35 CST

- Video VAE is 1,519,071,232 / 5,207,808,496 bytes (29.2%); `curl` PID 74275 remains active.
- PyTorch installation remains active as PID 74787. The main Torch 2.9.1/cu130 wheel had downloaded 237 / 612.6 MB at this checkpoint; the packages are not installed yet.
- GPU remains capped at 250 W, drawing 14.86 W with 192 MiB used. No generation has started.

### Resume checkpoint — 2026-11-15 17:39 CST

- Video VAE is 1,635,893,248 / 5,207,808,496 bytes (31.4%); `curl` PID 74275 is active.
- PyTorch install is still active as PID 74787; `pip show` confirms Torch, torchvision and torchaudio are not yet installed.
- Free disk is 106 GiB. RTX 3080 power cap is 250 W; current draw is 14.47 W with 192 MiB VRAM used. No ComfyUI server or generation is running.

### Live checkpoint — 2026-11-15 17:41 CST

- Video VAE is 1,664,286,720 / 5,207,808,496 bytes (32.0%).
- The Torch 2.9.1/cu130 wheel is 524.8 / 612.6 MB (85.7%); `pip` is still active.
- RTX 3080 is idle at 20.02 W with 192 MiB used; cap remains 250 W. No render has started.

### Live checkpoint — 2026-11-15 17:45 CST

- Video VAE is 1,774,505,984 / 5,207,808,496 bytes (34.1%).
- Torch, torchvision and torchaudio main wheels have downloaded. Pip is fetching NVIDIA NCCL and other CUDA dependencies; packages are not installed yet.
- GPU remains capped at 250 W and idle (19.62 W, 191 MiB). No ComfyUI render has started.

### Live checkpoint — 2026-11-15 17:47 CST

- Video VAE is 1,911,054,336 / 5,207,808,496 bytes (36.7%); its transfer is active.
- Pip is downloading the NVIDIA NCCL wheel. Torch packages are not installed yet.
- Free disk is 106 GiB. GPU power cap is 250 W; current draw is 14.23 W with 191 MiB used. No render has started.

### Live checkpoint — 2026-11-15 17:49 CST

- Video VAE is 1,990,803,456 / 5,207,808,496 bytes (38.2%).
- The NVIDIA NCCL wheel is 28.7 / 193.9 MB; pip remains active.
- GPU cap remains 250 W, draw is 17.93 W, and VRAM use is 191 MiB. No generation has started.

### Live checkpoint — 2026-11-15 17:53 CST

- Video VAE is 2,220,277,760 / 5,207,808,496 bytes (42.6%).
- NVIDIA NCCL is 46,929,920 / 193,900,000 bytes (24.2%); PyTorch install remains active.
- GPU cap remains 250 W, draw 16.52 W, VRAM use 192 MiB. No ComfyUI render has started.

### Live checkpoint — 2026-11-15 17:55 CST

- Video VAE is 2,345,250,816 / 5,207,808,496 bytes (45.0%).
- NVIDIA NCCL is 57,000,000 / 193,900,000 bytes (29.4%). PyTorch installation is still active.
- GPU cap remains 250 W, draw is 14.19 W, and VRAM use is 192 MiB. No ComfyUI run has started.

### Live checkpoint — 2026-11-15 17:57 CST

- Video VAE is 2,480,050,176 / 5,207,808,496 bytes (47.6%).
- NVIDIA NCCL is 67,153,920 / approximately 193,900,000 bytes (34.6%). PyTorch installation remains active.
- GPU cap remains 250 W, draw is 14.64 W, and VRAM use is 192 MiB. No ComfyUI run has started.

### Live checkpoint — 2026-11-15 17:59 CST

- Video VAE is 2,604,847,104 / 5,207,808,496 bytes (50.0%).
- NVIDIA NCCL is 76,584,960 / approximately 193,900,000 bytes (39.5%). PyTorch install remains active.
- GPU cap remains 250 W, draw 15.05 W, VRAM use 192 MiB. No render has started.

### Live checkpoint — 2026-11-15 18:01 CST

- Video VAE is 2,782,892,032 / 5,207,808,496 bytes (53.4%).
- NVIDIA NCCL is 87,070,720 / approximately 193,900,000 bytes (44.9%). Pip remains active.
- GPU cap remains 250 W, current draw 14.15 W, and VRAM use 191 MiB. No ComfyUI run has started.

### Live checkpoint — 2026-11-15 18:04 CST

- Video VAE is 2,963,402,752 / 5,207,808,496 bytes (56.9%).
- NVIDIA NCCL is 99,215,360 / approximately 193,900,000 bytes (51.2%). PyTorch install remains active.
- GPU cap remains 250 W, current draw 13.96 W, and VRAM use 191 MiB. No render has started.

### Live checkpoint — 2026-11-15 18:06 CST

- Video VAE is 3,064,553,472 / 5,207,808,496 bytes (58.8%).
- NVIDIA NCCL is 105,953,280 / approximately 193,900,000 bytes (54.6%). PyTorch install remains active.
- GPU cap remains 250 W, current draw 14.64 W, and VRAM use 191 MiB. No render has started.

### Live checkpoint — 2026-11-15 18:09 CST

- Video VAE is 3,268,923,392 / 5,207,808,496 bytes (62.8%).
- NVIDIA NCCL is 122,204,160 / approximately 193,900,000 bytes (63.0%). PyTorch install remains active.
- GPU cap remains 250 W, current draw 14.16 W, and VRAM use 191 MiB. No render has started.

### Live checkpoint — 2026-11-15 18:11 CST

- Video VAE is 3,433,070,592 / 5,207,808,496 bytes (65.9%).
- NVIDIA NCCL is 136,734,720 / approximately 193,900,000 bytes (70.5%). PyTorch install remains active.
- GPU cap remains 250 W, current draw 13.91 W, and VRAM use 191 MiB. No render has started.
- A verification watcher (session 60414) will run `verify_h3_vaes.sh` after both sequential VAE transfers terminate and will append checksum evidence to the setup log.

### Live checkpoint — 2026-11-15 18:13 CST

- Video VAE is 3,569,311,744 / 5,207,808,496 bytes (68.5%).
- NVIDIA NCCL is 146,206,720 / approximately 193,900,000 bytes (75.4%). Pip remains active.
- GPU cap remains 250 W, draw 14.61 W, and VRAM use 191 MiB. No render has started.

### Live checkpoint — 2026-11-15 18:15 CST

- Video VAE is 3,676,958,720 / 5,207,808,496 bytes (70.6%).
- NVIDIA NCCL is 151,808,000 / approximately 193,900,000 bytes (78.3%). PyTorch install remains active.
- GPU cap remains 250 W, current draw 19.54 W, and VRAM use 191 MiB. No render has started.

### Live checkpoint — 2026-11-15 18:19 CST

- Video VAE is 3,911,811,072 / 5,207,808,496 bytes (75.1%).
- NVIDIA NCCL is 167,843,840 / approximately 193,900,000 bytes (86.6%). PyTorch install remains active.
- GPU cap remains 250 W, draw 15.27 W, and VRAM use 193 MiB. No ComfyUI run has started.
- Corrected the official template's connected 0.4 MP Resolution Selector before any run. The prepared workflows now calculate to exactly 1344×768.

### Live checkpoint — 2026-11-15 18:20 CST

- `verify_lcz3045_workflows.py` passes on both workflows; output is saved in the research logs.
- Video VAE is 4,005,527,552 / 5,207,808,496 bytes (76.9%).
- NVIDIA NCCL is 173,660,160 / approximately 193,900,000 bytes (89.5%). Pip remains active.
- GPU cap remains 250 W, draw 14.39 W, and VRAM use 192 MiB. No ComfyUI run has started.

### Live checkpoint — 2026-11-15 18:21 CST

- Video VAE is 4,078,985,216 / 5,207,808,496 bytes (78.3%).
- NVIDIA NCCL is 180,910,080 / approximately 193,900,000 bytes (93.3%). PyTorch install remains active.
- GPU cap remains 250 W, draw 14.12 W, and VRAM use 192 MiB. No ComfyUI run has started.

### Live checkpoint — 2026-11-15 18:23 CST

- Video VAE is 4,173,717,504 / 5,207,808,496 bytes (80.1%).
- NVIDIA NCCL is 189,644,800 / approximately 193,900,000 bytes (97.8%). PyTorch installation remains active.
- GPU cap remains 250 W, draw is 15.00 W, and VRAM use is 192 MiB. No render has started.

### Live checkpoint — 2026-11-15 18:24 CST

- Video VAE is 4,253,003,776 / 5,207,808,496 bytes (81.7%).
- NVIDIA NCCL wheel download completed. Pip is fetching Triton 3.5.1 (170.5 MB); Torch packages are not installed yet.
- GPU power cap remains 250 W. No ComfyUI run has started.

### Live checkpoint — 2026-11-15 18:26 CST

- Video VAE is 4,291,076,096 / 5,207,808,496 bytes (82.4%).
- Triton 3.5.1 wheel is 82,790,400 / 170,500,000 bytes (48.6%). Pip remains active.
- GPU cap remains 250 W, draw 14.05 W, and VRAM use is 212 MiB. No render has started.

### Live checkpoint — 2026-11-15 18:27 CST

- Video VAE is 4,335,976,448 / 5,207,808,496 bytes (83.3%).
- Triton 3.5.1 wheel is 130,170,880 / 170,500,000 bytes (76.4%). Pip remains active.
- GPU cap remains 250 W, draw 14.02 W, and VRAM use 210 MiB. No render has started.

### Live checkpoint — 2026-11-15 18:29 CST

- Video VAE is 4,392,075,264 / 5,207,808,496 bytes (84.3%).
- Triton wheel download completed. Pip is fetching small dependencies; Torch is still not installed.
- GPU cap remains 250 W, draw is 13.91 W, and VRAM use is 210 MiB. No render has started.

### Live checkpoint — 2026-11-15 18:30 CST

- Video VAE is 4,504,129,536 / 5,207,808,496 bytes (86.5%).
- Pip remains active; `pip show` finds no Torch packages yet.
- GPU cap remains 250 W, draw 14.31 W, and VRAM use 210 MiB. No render has started.

### Live checkpoint — 2026-11-15 18:32 CST

- Video VAE is 4,606,197,760 / 5,207,808,496 bytes (88.4%).
- PyTorch pip is fetching Pillow and SymPy after fsspec/networkx. Torch packages are not installed yet.
- GPU cap remains 250 W, draw is 14.11 W, and VRAM use is 210 MiB. No render has started.

### Live checkpoint — 2026-11-15 18:33 CST

- Video VAE is 4,702,351,360 / 5,207,808,496 bytes (90.3%).
- PyTorch pip is fetching NumPy 2.5.4 and final small dependencies; Torch is not installed yet.
- GPU cap remains 250 W, draw 19.11 W, and VRAM use 154 MiB. No render has started.

### Live checkpoint — 2026-11-15 18:35 CST

- Video VAE is 4,808,937,472 / 5,207,808,496 bytes (92.3%).
- PyTorch install remains active; Torch was not yet visible in `pip show`.
- GPU cap remains 250 W, draw 13.84 W, and VRAM use 209 MiB. No render has started.
- Dependency watcher session 98711 will install ComfyUI's `requirements.txt` and capture a CUDA visibility check after the PyTorch install completes.

### Live checkpoint — 2026-11-15 18:41 CST

- PyTorch installation completed successfully: Torch 2.9.1+cu130, torchvision 0.24.1+cu130, torchaudio 2.9.1+cu130.
- ComfyUI `requirements.txt` installation is active (PID 95428); it is downloading the 29.6 MB frontend wheel.
- Video VAE is 5,203,689,472 / 5,207,808,496 bytes (99.92%). Audio VAE will download after it.
- GPU power cap is 250 W; current draw is 16.34 W and VRAM use is 207 MiB. No ComfyUI server or render has started.

### Live checkpoint — 2026-11-15 18:42 CST

- Video VAE download completed at the expected size of 5,207,808,496 bytes. SHA-256 verification is scheduled after the audio VAE transfer.
- Audio VAE is 80,470,016 / 605,254,808 bytes (13.3%) and still downloading.
- ComfyUI requirements installation remains active on its 29.6 MB frontend wheel.
- GPU cap is 250 W; current draw is 14.63 W and VRAM use is 207 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:44 CST

- Audio VAE is 200,192,000 / 605,254,808 bytes (33.1%).
- ComfyUI requirements install remains active. Pip has not logged completion of the 29.6 MB frontend wheel; live TLS connections from pip were present at 18:43 CST.
- GPU cap is 250 W; current draw is 15.85 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:45 CST

- Audio VAE is 271,818,752 / 605,254,808 bytes (44.9%).
- Pip remains active on the ComfyUI frontend wheel. Its TLS connections are still established, but no completion line has appeared.
- GPU cap is 250 W; current draw is 15.60 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:46 CST

- Audio VAE is 341,901,312 / 605,254,808 bytes (56.5%).
- Pip remains active on the ComfyUI frontend wheel; TCP counters show response data arriving.
- GPU cap is 250 W; current draw is 14.06 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:47 CST

- Audio VAE is 403,066,880 / 605,254,808 bytes (66.6%).
- Pip remains active on the 29.6 MB ComfyUI frontend wheel.
- GPU cap is 250 W; current draw is 14.56 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:48 CST

- Audio VAE is 463,712,256 / 605,254,808 bytes (76.6%).
- Pip is still active on the frontend wheel. At 18:48, its process had written 24,014,848 bytes and had active TLS sockets; pip does not show a progress percentage.
- GPU cap is 250 W; current draw is 14.00 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:49 CST

- Audio VAE is 534,581,248 / 605,254,808 bytes (88.3%).
- Pip has moved past the ComfyUI frontend wheel and is collecting dependency metadata. Requirements installation remains active.
- GPU cap is 250 W; current draw is 14.07 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:50 CST

- Audio VAE is 593,199,104 / 605,254,808 bytes (98.0%).
- ComfyUI requirements installation remains active; the log shows the frontend wheel and dependency metadata.
- GPU cap is 250 W; current draw is 19.89 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:51 CST

- Both VAE files completed and passed expected size plus official SHA-256 checks. See `logs/12-comfyui-h3-setup.txt`.
- ComfyUI requirements installation completed its 29.6 MB frontend wheel and 24.6 MB embedded-docs wheel. It is downloading `comfy_kitchen` (69.2 MB).
- GPU cap is 250 W; current draw is 14.30 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:52 CST

- Both VAE files remain verified against their official sizes and SHA-256 values.
- Pip completed the 69.2 MB `comfy_kitchen` wheel and is downloading `comfyui_workflow_templates_media_api` (100.1 MB).
- GPU cap is 250 W; current draw is 13.90 W and VRAM use is 147 MiB. Free disk is 100 GiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:53 CST

- Both VAE files passed verification.
- Pip remains active on `comfyui_workflow_templates_media_api` (100.1 MB); its active TLS socket had received 230,498,438 bytes cumulatively at 18:53.
- GPU cap is 250 W; current draw is 14.99 W and VRAM use is 147 MiB. Free disk is 100 GiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:54 CST

- Pip completed `comfyui_workflow_templates_media_api` (100.1 MB) and began `comfyui_workflow_templates_media_assets_01` (94.2 MB).
- Both VAEs remain verified. GPU cap is 250 W; current draw is 14.65 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:55 CST

- Pip completed `media_assets_01` (94.2 MB) and began `media_assets_02` (83.2 MB). Requirements installation is still active.
- Both VAEs remain verified. GPU cap is 250 W; current draw is 17.90 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:56 CST

- Pip completed `media_assets_02` (83.2 MB) and began `comfyui_workflow_templates_media_image` (89.4 MB).
- Both VAEs remain verified. GPU cap is 250 W; current draw is 18.94 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:57 CST

- Pip completed `media_image` (89.4 MB) and began `media_other` (89.1 MB).
- Both VAE files remain verified. GPU cap is 250 W; current draw is 19.69 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 18:58 CST

- Pip completed `media_other` (89.1 MB) and began `media_video` (104.3 MB).
- Both VAE files remain verified. GPU cap is 250 W; current draw is 13.88 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 19:00 CST

- Pip moved past the workflow media bundles and is downloading remaining Python dependencies; latest log shows SciPy 1.18.1 (35.3 MB).
- Both VAE files remain verified. GPU cap is 250 W; current draw is 13.89 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 19:01 CST

- Pip is downloading remaining dependencies, including PyAV 19.0.2 (35.0 MB), after SciPy.
- Free disk is 99 GiB. GPU cap is 250 W; current draw is 19.27 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 19:02 CST

- Dependency downloads completed. Pip is installing the collected ComfyUI requirements.
- Free disk is 97 GiB. GPU cap is 250 W; current draw is 13.90 W and VRAM use is 147 MiB. No server or render has started.

### Live checkpoint — 2026-11-15 19:03 CST

- ComfyUI requirements installation completed successfully. Torch 2.9.1+cu130, torchvision 0.24.1+cu130, and torchaudio 2.9.1+cu130 are installed.
- CUDA visibility check passed: `torch.cuda.is_available()` is True, CUDA 13.0 is reported, and NVIDIA GeForce RTX 3080 is detected.
- GPU cap remains 250 W; idle draw is 13.96 W and VRAM use is 147 MiB. Next: start ComfyUI and validate model/node loading before rendering.

### Live checkpoint — 2026-11-15 19:04 CST

- ComfyUI is live at `127.0.0.1:8188`. The server exposes native `MiniMaxH3ReferenceToVideo` nodes.
- Model selectors list the exact local INT8 ConvRot DiT and text encoder plus both verified VAEs.
- Startup reports 20,053 MiB VRAM, DynamicVRAM and two async offload streams. GPU cap is 250 W; idle VRAM is 371 MiB. No workflow has been queued.

### Live checkpoint — 2026-11-15 19:05 CST

- The first UI queue attempt was rejected by prompt validation because the optional Turbo LoRA file is absent. The generation did not start.
- The builder now removes the LoRA and switch nodes and directly wires the base DiT plus the fixed 20-step node. Both workflows pass structural preflight; the official frontend converts the 3D workflow to 25 API nodes with no LoRA node.
- Updated workflow hashes are recorded in `workflows/README.md`. Retrying 3D next.

### Live checkpoint — 2026-11-15 19:11 CST

- 3D prompt `884e6eb5-633d-4fcf-910e-60b035231048` is running. One job is active and the queue is empty.
- GPU cap is 250 W; draw is 249.12 W, VRAM use is 15,031 MiB, and temperature is 46°C.
- Host RAM use is 19 GiB of 125 GiB, with 106 GiB available.
- The server log shows the video VAE and 25.9 GB text encoder staged for dynamic VRAM offload. Sampling progress has not appeared yet.

### Live checkpoint — 2026-11-15 19:12 CST

- 3D run reached sampler initialization at 0/20 steps. Main DiT reports 19,995 MB staged; text encoder reports 25,882 MB staged with dynamic offload.
- GPU cap is 250 W; draw is 249.47 W, VRAM use is 12,889 MiB, and temperature is 55°C.
- Host RAM use is 37 GiB of 125 GiB, with 88 GiB available. One job is running, none pending; no OOM has occurred.

### Live checkpoint — 2026-11-15 19:13 CST

- One 3D prompt remains active. Progress is still 0/20 with “Model Initializing” for approximately 80 seconds.
- GPU cap is 250 W; draw is 249–250 W, VRAM use is 16,483 MiB, and temperature is 60°C.
- Host RAM use is 43 GiB of 125 GiB, with 82 GiB available. No OOM or queue error is present.

### Live checkpoint — 2026-11-15 19:14 CST

- GPU utilization reached 100%; power draw is 249.83 W, VRAM use is 18,155 MiB, and temperature is 61°C.
- Host RAM use is 46 GiB of 125 GiB, with 78 GiB available.
- The progress display remains “Model Initializing” at 0/20. One prompt is active; no OOM has occurred.

### Live checkpoint — 2026-11-15 19:15 CST

- GPU utilization is 100%; power draw is 249.07 W, VRAM use is 19,795 MiB, and temperature is 62°C.
- Host RAM use is 51 GiB of 125 GiB, with 74 GiB available.
- The run still shows “Model Initializing” at 0/20. One prompt is active; no OOM has occurred.

### Live checkpoint — 2026-11-15 19:17 CST

- Model initialization completed; the 3D sampler reached 1/20 (5%) after 4m26s elapsed.
- First-step average is 266.65 s/step. A naïve linear estimate is about 84 minutes for 20 steps; this is provisional because it includes initialization and only one step.
- GPU utilization is 100%; draw is 245.60 W, VRAM use is 19,703 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. One prompt is active; no OOM has occurred.

### Live checkpoint — 2026-11-15 19:19 CST

- Sampler remains at 1/20; the second step has not completed yet.
- GPU utilization is 100%; draw is 248.68 W, VRAM use is 19,703 MiB, and temperature is 62–63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. One prompt is active; no OOM has occurred. Runtime projection remains provisional.

### Live checkpoint — 2026-11-15 19:21 CST

- Sampler reached 2/20 (10%) at 8m51s elapsed; mean is 265.61 s/step.
- At this rate, about 80 minutes remain for 3D. This estimate is still provisional.
- GPU utilization is 100%; draw is 249.92 W, VRAM use is 19,671 MiB, and temperature is 62°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred.

### Live checkpoint — 2026-11-15 19:22 CST

- Sampler remains at 2/20. GPU utilization is 100%; draw is 248.95 W, VRAM use is 19,671 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. One prompt is active; no OOM has occurred.
- One-second GPU and host RAM telemetry continues in logs 14 and 15.

### Live checkpoint — 2026-11-15 19:24 CST

- Sampler remains at 2/20; the current step has run about 3m14s.
- GPU utilization is 100%; draw is 250.13 W, VRAM use is 19,671 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. One job is active; no error or OOM has occurred.

### Live checkpoint — 2026-11-15 19:24:50 CST

- Sampler reached 3/20 (15%) at 13m17s; mean is 266.29 s/step. About 75 minutes remain at this rate.
- GPU utilization is 100%; draw is 249.63 W, VRAM use is 19,671 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred.

### Live checkpoint — 2026-11-15 19:25 CST

- Sampler remains at 3/20; the current step has run about one minute, within the observed ~4m25s/step pace.
- GPU utilization is 100%; draw is 248.27 W, VRAM use is 19,575 MiB, and temperature is 64°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred.

### Live checkpoint — 2026-11-15 19:28 CST

- Sampler remains at 3/20; the fourth step has run about 3m10s, near the observed ~4m25s cadence.
- GPU utilization is 100%; draw is 247.88 W, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. Queue is stable; no OOM has occurred.

### Live checkpoint — 2026-11-15 19:29:41 CST

- Sampler reached 4/20 (20%) at 17m43s elapsed; mean is 266.11 s/step. About 71 minutes remain at this rate.
- GPU utilization is 100%; draw is 248.76 W, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred.

### Live checkpoint — 2026-11-15 19:31 CST

- Sampler remains at 4/20; the fifth step has run about two minutes.
- GPU utilization is 100%; draw is 248.85 W, VRAM use is 19,575 MiB, and temperature is 62°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. One job is active; no OOM has occurred.

### Live checkpoint — 2026-11-15 19:33 CST

- Sampler remains at 4/20; the fifth step has run about 3m30s.
- GPU utilization is 100%; draw is 249.48 W, VRAM use is 19,575 MiB, and temperature is 62°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred.

### Live checkpoint — 2026-11-15 19:34 CST

- Sampler remains at 4/20; the fifth step has run about five minutes, roughly 30 seconds beyond the prior mean.
- GPU utilization is 100%; draw is 249.91 W, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. The queue is active; no OOM has occurred.

### Live checkpoint — 2026-11-15 19:35:04 CST

- Sampler reached 5/20 (25%) at 22m09s elapsed; mean is 266.34 s/step.
- About 66m35s remain. Projected 3D completion is around 20:42 CST if this pace holds.
- GPU utilization is 100%; draw is 249.75 W, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred.

### Live checkpoint — 2026-11-15 19:37 CST

- Sampler remains at 5/20; the sixth step has run about three minutes.
- GPU utilization is 100%; draw is 249.62 W, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred.

### Live checkpoint — 2026-11-15 19:39:12 CST

- Sampler reached 6/20 (30%) at 26m35s elapsed; mean is 265.99 s/step.
- About 62m04s remain. Projected completion is around 20:41 CST if this pace holds.
- GPU utilization is 100%; draw is 249.39 W, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred.

### Live checkpoint — 2026-11-15 19:41 CST

- Sampler remains at 6/20; the seventh step has run about 4m48s, a little slower than the prior mean.
- GPU utilization is 100%; draw is 247.89 W, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred.

### Live checkpoint — 2026-11-15 19:43 CST

- Sampler reached 7/20 (35%) at 31m02s elapsed; mean is 266.37 s/step.
- About 57m42s remain. Projected completion is around 20:41 CST if the pace holds.
- GPU utilization is 100%; draw is 248.89 W, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred.

### Live checkpoint — 2026-11-15 19:45 CST

- Sampler remains at 7/20; the eighth step has run about one minute.
- GPU utilization is 100%; draw is 248.34 W, VRAM use is 19,575 MiB, and temperature is 62°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. One job is active; no OOM has occurred.

### Live checkpoint — 2026-11-15 19:47 CST

- Sampler remains at 7/20; the eighth step has run about 2m08s.
- GPU utilization is 100%; draw is 249.10 W, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred; telemetry is active.

### Live checkpoint — 2026-11-15 19:47:31 CST

- Sampler reached 8/20 (40%) at 35m29s elapsed; mean is 266.76 s/step.
- About 53m21s remain. Projected completion is around 20:41 CST if the pace holds.
- GPU utilization is 100%; draw is 245.87 W, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred.

### Live checkpoint — 2026-11-15 19:49 CST

- Sampler remains at 8/20; the ninth step has run about 2m06s.
- GPU utilization is 100%; draw is 249.77 W, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. One job is active; no OOM has occurred.

### Live checkpoint — 2026-11-15 19:51 CST

- Sampler remains at 8/20; the ninth step has run about 4m11s.
- GPU utilization is 100%; draw is 245–250 W, VRAM use is 19,575 MiB, and temperature is 63–64°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. The queue is active; no error or OOM has occurred.

### Live checkpoint — 2026-11-15 19:52:05 CST

- Sampler reached 9/20 (45%) at 39m55s elapsed; mean is 266.83 s/step.
- About 48m55s remain. Projected completion is around 20:41 CST if this pace holds.
- GPU utilization is 100%; draw is 249.76 W, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred.

### Live checkpoint — 2026-11-15 19:55 CST

- Sampler remains at 9/20; the tenth step has run about 3m18s.
- GPU utilization is 100%; draw is 248.62 W, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. The queue is active; no OOM has occurred.

### Live checkpoint — 2026-11-15 19:57:27 CST

- Sampler reached 10/20 (50%) at 44m22s elapsed; mean is 266.16 s/step.
- About 44m21s remain. Projected completion is around 20:41 CST if this pace holds.
- GPU utilization is 100%; draw is 248.62 W, VRAM use is 19,575 MiB, and temperature is 62°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred.

### Live checkpoint — 2026-11-15 19:59 CST

- Sampler remains at 10/20; the eleventh step has run about one minute.
- GPU utilization is 100%; draw is 249.58 W, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. One job is active; no error or OOM has occurred.

### Live checkpoint — 2026-11-15 20:01:10 CST

- Sampler reached 11/20 (55%) at 48m48s elapsed; mean is 266.71 s/step.
- About 40 minutes remain. Projected completion is around 20:41 CST if this pace holds.
- GPU utilization is 100%; draw is 249.19 W, VRAM use is 19,575 MiB, and temperature is 62°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM has occurred.

### Live checkpoint — 2026-11-15 20:03 CST

- Sampler remains at 11/20; the twelfth step has run about 3m27s.
- GPU utilization is 100%; draw is 248.95 W, VRAM use is 19,575 MiB, and temperature is 62°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. The queue is active; no error or OOM has occurred.

### Live checkpoint — 2026-11-15 20:05:45 CST

- Sampler reached 12/20 (60%) at 53m14s elapsed; mean is 265.73 s/step.
- Eight steps remain, about 35m26s at the observed pace; projected completion is around 20:41 CST.
- GPU utilization is 100%; observed draw is 248.30 W with the 250 W cap configured, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use is 52 GiB of 125 GiB, with 72 GiB available. No OOM or sampler error has occurred.

### Live checkpoint — 2026-11-15 20:10:10 CST

- Sampler reached 13/20 (65%) at 57m40s elapsed; mean is 265.84 s/step.
- Seven steps remain, about 31 minutes at the observed pace; projected completion is around 20:41 CST.
- GPU utilization is 100%; draw is 249.77 W with the 250 W cap configured, VRAM use is 19,575 MiB, and temperature is 63°C.
- Host RAM use remains 52 GiB, with 72 GiB available. No OOM or sampler error has occurred.

### Live checkpoint — 2026-11-15 20:14:29 CST

- Sampler reached 14/20 (70%) at 1h02m06s elapsed; mean is 266.08 s/step.
- Six steps remain, about 26m36s at the observed pace; projected completion is around 20:41 CST.
- GPU utilization is 100%; draw is 244.88 W with the 250 W cap configured, VRAM use is 19,575 MiB, and temperature is 64°C.
- No OOM; host memory remains stable.

### Live checkpoint — 2026-11-15 20:18:44 CST

- Sampler reached 15/20 (75%) at 1h06m32s elapsed; mean is 265.92 s/step.
- Five steps remain, about 22m09s at the observed pace; projected completion is around 20:41 CST.
- GPU utilization is 100%; draw is 249.74 W with the 250 W cap configured, VRAM use is 19,575 MiB, and temperature is 63°C.
- No OOM or sampler error has occurred.

### Live checkpoint — 2026-11-15 20:23:33 CST

- Sampler reached 16/20 (80%) at 1h10m58s elapsed; mean is 265.69 s/step.
- Four steps remain, about 17m42s at the observed pace; projected completion is around 20:41 CST.
- GPU utilization is 100%; draw is 249.74 W with the 250 W cap configured, VRAM use is 19,575 MiB, and temperature is 63°C.
- No OOM or sampler error; host memory remains stable.

### Live checkpoint — 2026-11-15 20:27:49 CST

- Sampler reached 17/20 (85%) at 1h15m23s elapsed; mean is 265.40 s/step.
- Three steps remain, about 13m16s at the observed pace; projected completion is around 20:41 CST.
- GPU utilization is 100%; draw is 248.96 W with the 250 W cap configured, VRAM use is 19,641 MiB, and temperature is 63°C.
- No OOM or sampler error has occurred.

### Live checkpoint — 2026-11-15 20:32:04 CST

- Sampler reached 18/20 (90%) at 1h19m48s elapsed; mean is 265.43 s/step.
- Two steps remain, about 8m50s at the observed pace; projected completion is around 20:41 CST.
- GPU utilization is 100%; draw is 249.04 W with the 250 W cap configured, VRAM use is 19,571 MiB, and temperature is 63°C.
- No OOM or sampler error has occurred.

### Live checkpoint — 2026-11-15 20:36:19 CST

- Sampler reached 19/20 (95%) at 1h24m14s elapsed; mean is 265.61 s/step.
- The final step is estimated at about 4m25s. Sampler should end near 20:41 CST, followed by VAE decode and video mux/write; final completion time is not yet known.
- GPU utilization is 100%; draw is 249.26 W with the 250 W cap configured, VRAM use is 19,511 MiB, and temperature is 63°C.
- No OOM or sampler error has occurred.

### 3D CGI run completed — 2026-11-15

Prompt `884e6eb5-633d-4fcf-910e-60b035231048` succeeded. The sampler completed 20 steps in **1h28m39s**; ComfyUI reports total prompt execution of **1h31m14s**.

- Native 12.25 s source: `/home/swchen/Downloads/ai/tools/comfyui-linux/ComfyUI-102350eb949bca599e450a904f0562ad3f551279/output/video/lcz3045_3d_00001_.mp4` (1344×768, 24 fps, 294 frames; 11,894,700 bytes; SHA-256 `bc440fba1aac2990169544e83d9541ca5c8a4253a5a1a8a78388e5cf9842edee`).
- Final 12 s file: same directory, `lcz3045_3d_12s.mp4` (1344×768, 24 fps, 288 frames, 12.000 s; 18,652,984 bytes; SHA-256 `09013fb27f1733b0ed44f396ec2ab3a0f20f711e0a46fc290580b6992ceb3ef5`). The verification script passed all five target checks.
- Visual sample sheet at `assets/minimax-h3-lcz3045/lcz3045-3d-contact-sheet.png` uses frames at 0, 2, 4, 6, 8, and 10 s. The sword duel and flame effects read clearly; composition shifts across shots and some pose/detail changes are visible.
- GPU telemetry over 19:11:25–20:42:41 (5,474 one-second samples): mean draw 247.37 W; measured peak 252.25 W with the configured 250 W limit; peak VRAM 19,799 MiB; peak temperature 64°C.
- Host RAM available reached 63.8 GiB minimum; swap free stayed at or above 7.63 GiB. No OOM occurred.

The 2D workflow was then validated at 25 nodes, with no LoRA node, and queued around 20:44 CST under prompt `6ed32790-6713-4674-ae97-e6eee8e9af34`.

### 2D live checkpoint — 2026-11-15 20:49:29 CST

- Sampler reached 1/20 (5%); model initialization plus the first step took 4m25s, mean 265.70 seconds per step.
- Estimated 19 steps / 84m08s remain; projected sampling completion is near 21:54 CST, followed by VAE decode and file write.
- GPU load 100%; draw 249.02 W with 250 W configured limit; VRAM 19,715 MiB; temperature 63°C.
- Host RAM: 58 GiB used, 67 GiB available. No OOM.

### 2D live checkpoint — 2026-11-15 20:54:07 CST

- Sampler reached 2/20 (10%) at 8m55s elapsed; mean 267.85 seconds per step; 18 steps / 1h20m21s remain.
- Revised projected sampling completion is around 22:14 CST. The earlier 21:54 estimate was a time arithmetic error and omitted the remaining interval.
- GPU load 100%; draw 248.90 W; VRAM 19,707 MiB; temperature 62°C. No OOM.

### 2D live checkpoint — 2026-11-15 20:58:34 CST

- Sampler reached 3/20 (15%) at 13m29s; observed mean 273.46 seconds per step; 17 steps / 1h17m28s remain.
- Revised projected sampling completion is around 22:16 CST.
- GPU load 100%; draw 249.85 W; VRAM 19,704 MiB; temperature 63°C. No OOM.

### 2D live checkpoint — 2026-11-15 21:02:55 CST

- Sampler reached 4/20 (20%) at 18m04s; mean 275.83 seconds per step; 16 steps / 1h13m33s remain.
- Projected sampling end remains around 22:16 CST.
- GPU load 100%; draw 249.03 W; configured limit 250 W; VRAM 19,459 MiB; temperature 63°C. No OOM.

### 2D live checkpoint — 2026-11-15 21:07:18 CST

- Sampler reached 5/20 (25%) at 22m31s; mean 266.44 seconds per step; 15 steps / 1h06m36s remain.
- Projected sampling end is around 22:14 CST.
- GPU load 100%; draw 245.69 W; VRAM 19,454 MiB; temperature 64°C. No OOM.

### 2D live checkpoint — 2026-11-15 21:11:41 CST

- Sampler reached 6/20 (30%) at 26m57s; mean 266.34 seconds per step; 14 steps / 1h02m08s remain.
- Projected sampling end is around 22:14 CST.
- GPU load 100%; draw 248.73 W; configured limit 250 W; VRAM 19,430 MiB; temperature 63°C. No OOM.

### 2D live checkpoint — 2026-11-15 21:16:05 CST

- Sampler reached 7/20 (35%) at 31m24s; mean 266.25 seconds per step; 13 steps / 57m41s remain.
- Projected sampling end is around 22:14 CST.
- GPU load 100%; telemetry draw 249.67 W; VRAM 19,497 MiB; temperature 63°C. No OOM.

### 2D live checkpoint — 2026-11-15 21:20:58 CST

- Sampler reached 8/20 (40%) at 35m49s; mean 265.77 seconds per step; 12 steps / 53m09s remain.
- Projected sampling end is around 22:14 CST.
- GPU load 100%; draw 245.77 W; VRAM 19,477 MiB; temperature 63°C. No OOM.

### 2D live checkpoint — 2026-11-15 21:25:21 CST

- Sampler reached 9/20 (45%) at 40m16s; mean 266.35 seconds per step; 11 steps / 48m49s remain.
- Projected sampling end is around 22:14 CST.
- GPU load 100%; draw 248.77 W; VRAM 19,404 MiB; temperature 63°C. No OOM.

### 2D live checkpoint — 2026-11-15 21:29:39 CST

- Sampler reached 10/20 (50%) at 44m41s; mean 265.77 seconds per step; 10 steps / 44m17s remain.
- Projected sampling end is around 22:14 CST.
- GPU load 100%; draw 249.56 W; VRAM 19,404 MiB; temperature 63°C. No OOM.

### 2D live checkpoint — 2026-11-15 21:34:02 CST

- Sampler reached 11/20 (55%) at 49m07s; mean 266.02 seconds per step; 9 steps / 39m54s remain.
- Projected sampling end is around 22:14 CST.
- GPU load 100%; draw 249.63 W; VRAM 19,404 MiB; temperature 63°C. No OOM.

### 2D live checkpoint — 2026-11-15 21:38:23 CST

- Sampler reached 12/20 (60%) at 53m34s; mean 266.27 seconds per step; 8 steps / 35m30s remain.
- Projected sampling end is around 22:14 CST.
- GPU load 100%; draw 248.46 W; VRAM 19,404 MiB; temperature 63°C. No OOM.

### 2D live checkpoint — 2026-11-15 21:42:41 CST

- Sampler reached 13/20 (65%) at 58m00s; mean 266.10 seconds per step; 7 steps / 31m02s remain.
- Projected sampling end is around 22:14 CST.
- GPU load 100%; telemetry draw 248.87 W; VRAM 19,404 MiB; temperature 63°C. No OOM.

### 2D live checkpoint — 2026-11-15 21:47:36 CST

- Sampler reached 14/20 (70%) at 1h02m26s; mean 266.08 seconds per step; 6 steps / 26m36s remain.
- Projected sampling end is around 22:14 CST.
- GPU load 100%; telemetry draw 248.49 W; VRAM 19,404 MiB; temperature 63°C. No OOM.

### 2D live checkpoint — 2026-11-15 21:52:04 CST

- Sampler reached 15/20 (75%) at 1h06m52s; mean 266.32 seconds per step; 5 steps / 22m11s remain.
- Projected sampling end is around 22:14 CST.
- GPU load 100%; draw 249.38 W; VRAM 19,404 MiB; temperature 63°C. No OOM.

### 2D live checkpoint — 2026-11-15 21:56:19 CST

- Sampler reached 16/20 (80%) at 1h11m18s; mean 266.28 seconds per step; 4 steps / 17m45s remain.
- Projected sampling end is around 22:14 CST.
- GPU load 100%; draw 249.22 W; VRAM 19,404 MiB; temperature 63°C. No OOM.

### 2D live checkpoint — 2026-11-15 22:00:36 CST

- Sampler reached 17/20 (85%) at 1h15m45s; mean 266.49 seconds per step; 3 steps / 13m19s remain.
- Projected sampling end is around 22:14 CST.
- GPU load 100%; observed draw 250.44 W; VRAM 19,404 MiB; temperature 63°C. No OOM.

### 2D live checkpoint — 2026-11-15 22:04:53 CST

- Sampler reached 18/20 (90%) at 1h20m11s; mean 266.44 seconds per step; 2 steps / 8m52s remain.
- Projected sampling end is around 22:14 CST; VAE decode and file write follow.
- GPU load 100%; draw 245.28 W; VRAM 19,404 MiB; temperature 64°C. No OOM.

### 2D live checkpoint — 2026-11-15 22:09:47 CST

- Sampler reached 19/20 (95%) at 1h24m38s; mean 266.80 seconds per step; final step estimated about 4m26s.
- Sampling should finish near 22:14 CST; VAE decode and file write follow.
- GPU load 100%; draw 249.93 W; VRAM 19,404 MiB; temperature 63°C. No OOM.
