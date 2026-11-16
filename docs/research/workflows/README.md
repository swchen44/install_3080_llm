# lcz.me 3045 ComfyUI workflows

## Source and inputs

- Challenge: <https://lcz.me/topic/3045>
- Official R2V UI workflow template: `video_minimax_h3_r2v.official.json`
- Template source: <https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json>
- Template SHA-256: `a79f1a8ae7d250f9da8b0f4e636e202526c37457b808e74fdf25de7ceed96574`
- Builder: `build_lcz3045_workflows.py`
- References: `../assets/minimax-h3-lcz3045/manifest.json`; copied to `~/Downloads/ai/tools/comfyui-linux/ComfyUI-102350eb949bca599e450a904f0562ad3f551279/input/lcz3045/`.

## Prepared workflows

- `minimax-h3-lcz3045-3d.json`
- `minimax-h3-lcz3045-2d.json`

Both JSON files use the six references in manifest order, 1344×768, a 12-second duration input, 20 steps, seed `261662374822964` with fixed seed behavior, and the same INT8 ConvRot DiT, text encoder, FP16 video VAE, FP32 audio VAE, sampler and scheduler. The only intended difference is the style sentence in the prompt. The optional Turbo LoRA branch is removed: ComfyUI validates the inactive switch branch and rejects it when its optional LoRA file is absent.

The H3 native frame rule rounds 12 seconds to 294 frames (12.25 seconds at 24 fps). Trim the resulting MP4 to 12.00 seconds after generation. Preserve the original 12.25-second files as evidence.

## Attention canary

`h3-attention-canary.api.json` is the short 0.2 MP / 2-second-input / 20-step R2V graph, run with the same fixed seed under default PyTorch attention and `--use-ck-attention`. `h3-ui-to-api.py` converts the saved UI graph; `run_h3_attention_canary.sh pytorch|kitchen` starts ComfyUI with the 250 W cap guard and one-second GPU telemetry. Results and output hashes are in `../minimax-h3-speed-canary-20261115.md`.

`h3-attention-fullsize-kitchen.api.json` is the measured 0.984375 MP / 12-second-input workflow (native 294 frames) with the original fixed 3D seed. It was run with the same graph and `--use-ck-attention`, then finalized through `finalize_12s.sh`; the full-size output and telemetry are listed in the speed report and `logs/20-h3-attention-fullsize-evidence.txt`.

## Run evidence to collect

For each style, preserve the exact workflow JSON, ComfyUI console log, original MP4, trimmed MP4, and `ffprobe` output. Record total wall time from queue start to completed output, sampling time if the console provides it, peak VRAM, peak host RAM, GPU power and temperature, ComfyUI version, Python/Torch/CUDA versions, and model hashes. Keep the GPU power limit at 250 W for both runs.

## Execution status

The paired 3D/2D workflows passed JSON, resolution-selector, and reference-order checks and completed on the RTX 3080. Their measured results are in `../minimax-h3-3080-lcz3045.md`. The selector uses 16:9 and 0.984375 MP in ComfyUI's 1024×1024 pixel units, with a multiple of 32; this resolves to exactly 1344×768.

- 3D SHA-256: `f1f9c7ce24682a51c805a884834e87a5987ba6ae5a3feaadae9b0002f54f20ad`
- 2D SHA-256: `ce64154a7a22d02f8d2ceb10621a8b1287eab92b7cee0d67925f624c5350697a`

`launch_comfyui_logged.sh` starts the local server only when the GPU cap is 250 W, records system/GPU telemetry, and writes separate server and telemetry logs under `docs/research/logs/`. Pass optional ComfyUI flags through it, for example `launch_comfyui_logged.sh --use-ck-attention` for the tested Kitchen backend; the actual arguments are included in the log.

`finalize_12s.sh` preserves the generated 12.25-second source, writes a separate 288-frame/24-fps/12-second copy, and saves `ffprobe` metadata beside that copy. It refuses to overwrite an existing output.

`verify_h3_vaes.sh` checks the full expected byte sizes and official Hugging Face SHA-256 values for both downloaded VAE files. Run it only after both transfers complete.

`verify_12s_video.py` checks that a finalized clip has 1344×768 video, 288 frames at 24 fps, and a 12.000-second container duration. `finalize_12s.sh` runs it after ffprobe and exits on a mismatch.

`verify_lcz3045_workflows.py` verifies that the selector computes 1344×768, all six images connect in challenge order, and both styles share 294 frames, 20 steps, one fixed seed, and the requested models. Recorded result: `../logs/16-lcz3045-workflow-preflight.json`.

`install_comfyui_deps_after_torch.sh` waits for the active pinned PyTorch install, installs the reused ComfyUI source's `requirements.txt`, then records package versions and checks CUDA visibility. It writes the setup result to `docs/research/logs/17-comfyui-dependencies.log`.
