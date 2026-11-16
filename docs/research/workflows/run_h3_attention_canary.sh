#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/swchen/Downloads/ai/tools/comfyui-linux"
COMFY="$ROOT/ComfyUI-102350eb949bca599e450a904f0562ad3f551279"
PYTHON="$ROOT/.venv/bin/python"
LOG_DIR="/home/swchen/git/install_3080_llm/docs/research/logs"
MODE="${1:-pytorch}"
case "$MODE" in
  pytorch) EXTRA=() ;;
  kitchen) EXTRA=(--use-ck-attention) ;;
  *) echo "mode must be pytorch or kitchen" >&2; exit 2 ;;
esac
CAP="$(nvidia-smi --query-gpu=power.limit --format=csv,noheader,nounits | head -n 1 | xargs)"
case "$CAP" in 250|250.0|250.00) ;; *) echo "Expected 250 W cap, found $CAP W" >&2; exit 2 ;; esac
RUN_ID="$(date '+%Y%m%d-%H%M%S')-$MODE"
SERVER_LOG="$LOG_DIR/18-h3-attention-$RUN_ID.log"
GPU_LOG="$LOG_DIR/19-h3-attention-gpu-$RUN_ID.csv"
{
  echo "run_id=$RUN_ID"
  date --iso-8601=seconds
  echo "mode=$MODE"
  echo "gpu_power_cap_w=$CAP"
  nvidia-smi --query-gpu=name,memory.total,power.limit,driver_version --format=csv
  "$PYTHON" --version
  echo "comfyui_source=0.45.0"
  printf 'server_args='; printf '%q ' --listen 127.0.0.1 "${EXTRA[@]}"; echo
} | tee "$SERVER_LOG"
nvidia-smi --query-gpu=timestamp,power.draw,memory.used,temperature.gpu,utilization.gpu --format=csv -l 1 > "$GPU_LOG" &
GPU_MONITOR_PID=$!
cleanup() { kill "$GPU_MONITOR_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM
cd "$COMFY"
"$PYTHON" main.py --listen 127.0.0.1 "${EXTRA[@]}" 2>&1 | tee -a "$SERVER_LOG"
