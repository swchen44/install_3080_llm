#!/usr/bin/env bash
set -euo pipefail
ROOT="/home/swchen/Downloads/ai/tools/comfyui-linux"
COMFY="$ROOT/ComfyUI-102350eb949bca599e450a904f0562ad3f551279"
PYTHON="$ROOT/.venv/bin/python"
LOG="/home/swchen/git/install_3080_llm/docs/research/logs/17-comfyui-dependencies.log"

while kill -0 74787 2>/dev/null; do sleep 30; done
if ! "$PYTHON" -m pip show torch >/dev/null 2>&1; then
  echo "ERROR: initial PyTorch install ended without installing torch." | tee -a "$LOG"
  exit 1
fi
{
  date --iso-8601=seconds
  echo "Installing ComfyUI requirements from $COMFY/requirements.txt"
  cd "$COMFY"
  "$PYTHON" -m pip install --no-cache-dir -r requirements.txt
  "$PYTHON" - <<'PY'
import torch, torchvision, torchaudio
print("torch", torch.__version__)
print("torchvision", torchvision.__version__)
print("torchaudio", torchaudio.__version__)
print("cuda_available", torch.cuda.is_available())
if not torch.cuda.is_available():
    raise SystemExit("CUDA is not available")
print("cuda_version", torch.version.cuda)
print("gpu", torch.cuda.get_device_name(0))
PY
} 2>&1 | tee -a "$LOG"
