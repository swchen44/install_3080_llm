#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/swchen/Downloads/ai/tools/comfyui-linux"
COMFY="$ROOT/ComfyUI-102350eb949bca599e450a904f0562ad3f551279"
PYTHON="$ROOT/.venv/bin/python"
RESEARCH="/home/swchen/git/install_3080_llm/docs/research"
LOG_DIR="$RESEARCH/logs"
mkdir -p "$LOG_DIR"

CAP="$(nvidia-smi --query-gpu=power.limit --format=csv,noheader,nounits | head -n 1 | xargs)"
case "$CAP" in
  250|250.0|250.00) ;;
  *) echo "Refusing to start: GPU power cap is $CAP W, expected 250 W." >&2; exit 2 ;;
esac

RUN_ID="$(date '+%Y%m%d-%H%M%S')"
SERVER_LOG="$LOG_DIR/13-comfyui-server-$RUN_ID.log"
GPU_LOG="$LOG_DIR/14-gpu-telemetry-$RUN_ID.csv"
MEMORY_LOG="$LOG_DIR/15-memory-telemetry-$RUN_ID.csv"

{
  echo "run_id=$RUN_ID"
  date --iso-8601=seconds
  echo "gpu_power_cap_w=$CAP"
  nvidia-smi --query-gpu=name,memory.total,power.limit,driver_version --format=csv
  free -h
  "$PYTHON" --version
  ffmpeg -version | head -n 1
  echo "comfyui_source=0.45.0"
  printf 'comfyui_args='; printf '%q ' "$@"; echo
  echo "gpu_telemetry=$GPU_LOG"
  echo "memory_telemetry=$MEMORY_LOG"
} | tee "$SERVER_LOG"

nvidia-smi --query-gpu=timestamp,name,power.draw,memory.used,temperature.gpu --format=csv -l 1 > "$GPU_LOG" &
GPU_MONITOR_PID=$!
(
  echo 'timestamp,MemTotal_kB,MemAvailable_kB,SwapTotal_kB,SwapFree_kB'
  while :; do
    NOW="$(date --iso-8601=seconds)"
    awk -v now="$NOW" '
      /^MemTotal:/ { mem_total=$2 }
      /^MemAvailable:/ { mem_available=$2 }
      /^SwapTotal:/ { swap_total=$2 }
      /^SwapFree:/ { swap_free=$2 }
      END { print now "," mem_total "," mem_available "," swap_total "," swap_free }
    ' /proc/meminfo
    sleep 1
  done
) > "$MEMORY_LOG" &
MEMORY_MONITOR_PID=$!
cleanup() {
  kill "$GPU_MONITOR_PID" "$MEMORY_MONITOR_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cd "$COMFY"
"$PYTHON" main.py --listen 127.0.0.1 "$@" 2>&1 | tee -a "$SERVER_LOG"
