#!/usr/bin/env bash
set -euo pipefail
MODEL_ROOT="/home/swchen/Downloads/ai/models/comfyui/ComfyUI/models/vae"
verify() {
  local name="$1" expected_size="$2" expected_sha="$3" file="$MODEL_ROOT/$1" actual_size actual_sha
  actual_size="$(stat -c '%s' "$file")"
  if [[ "$actual_size" != "$expected_size" ]]; then
    echo "SIZE MISMATCH: $file ($actual_size != $expected_size)" >&2
    return 1
  fi
  actual_sha="$(sha256sum "$file" | cut -d ' ' -f 1)"
  if [[ "$actual_sha" != "$expected_sha" ]]; then
    echo "SHA256 MISMATCH: $file ($actual_sha != $expected_sha)" >&2
    return 1
  fi
  echo "VERIFIED $name size=$actual_size sha256=$actual_sha"
}
verify minimax_h3_video_vae_fp16.safetensors 5207808496 7c1f131492e7eddacaac9069a61b81bdd39de5cc96561e677c5eab1cdce5e522
verify minimax_h3_audio_vae_fp32.safetensors 605254808 8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48
