#!/usr/bin/env bash
# Give the local Strata Qwen3.8-Flash-Next server its picture reader (VLM).
#
#   scripts/enable_vision.sh status   read-only: what is present, what is missing
#   scripts/enable_vision.sh fetch    only download the 0.9 GB picture reader (no restart)
#   scripts/enable_vision.sh apply    download if needed, relaunch the server with --vision cpu
#   scripts/enable_vision.sh check    send one red picture and print the answer
#   scripts/enable_vision.sh pi       let pi declare image input (local/pi-agent-home/models.json)
#
# `apply` unloads the running model and loads it again (about 20 minutes, engine_ready_s
# 1230 measured on this machine).  Anything talking to the API - including the agent
# session you may be reading this from - is interrupted, so run it when nothing is working.
set -euo pipefail

root=/home/swchen/git/install_3080_llm
cd "$root"

export STRATA_HOME=$root/local/state
export STRATA_COMPONENTS_DIR=$root/local/components
export XDG_STATE_HOME=$root/local/xdg-state
export PATH=$root/local/strata-control/bin:$PATH

run_config=$root/local/xdg-state/strata/launch/ud-q4_k_xl-128k.json
key_file=$root/local/hermes-private/api-key
models_json=$root/local/pi-agent-home/models.json

status() {
  echo "run config   $run_config"
  python3 - "$run_config" <<'PY'
import json, sys
cfg = json.load(open(sys.argv[1]))
v = cfg.get("vision")
print("vision       " + (json.dumps(v, ensure_ascii=False) if v else "ABSENT (the server answers text only)"))
PY
  if compgen -G "$root/local/unsloth-data/models/mmproj-*.gguf" > /dev/null \
     || compgen -G "$root/local/models/mmproj-*.gguf" > /dev/null; then
    echo "mmproj       present ($(du -h "$root"/local/*/models/mmproj-*.gguf 2>/dev/null | head -1 | cut -f1))"
  else
    echo "mmproj       missing (0.9 GB; apply fetches it)"
  fi
  grep -q '"image"' "$models_json" \
    && echo "pi           declares image input" \
    || echo "pi           text only (run: scripts/enable_vision.sh pi)"
  echo "power limit  $(nvidia-smi --query-gpu=power.limit --format=csv,noheader)"
}

apply() {
  echo "Reloading the model with the picture reader.  This interrupts every API client."
  # the key goes in through the environment, never the command line (it would show in ps)
  export STRATA_LAN_KEY="$(cat "$key_file")"
  strata launch --family unsloth --model ud-q4_k_xl --context 128k \
    --vision cpu --drafting off --tune skip --access lan --port 8080 \
    --api-key-env STRATA_LAN_KEY \
    --set STRATA_ROUTE_TAIL_SKIP=0 --set STRATA_PREFILL_CPU_SHARE=0 \
    --restart --no-tui
  unset STRATA_LAN_KEY
}

check() {
  python3 "$root/scripts/vision_check.py"
}

pi() {
  python3 - "$models_json" <<'PY'
import json, shutil, sys
p = sys.argv[1]
shutil.copy(p, p + ".bak")
d = json.load(open(p))
n = 0
for prov in d.get("providers", {}).values():
    for m in prov.get("models", []):
        inp = m.get("input", ["text"])
        if "image" not in inp:
            m["input"] = inp + ["image"]
            n += 1
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
open(p, "a").write("\n")
print(f"updated {n} model(s); previous file kept as {p}.bak")
PY
  echo "restart pi to pick it up"
}

fetch() {
  # setup's own picture step: writes the mmproj and its finish mark, changes no run config
  STRATA_COMPONENTS_DIR=$root/local/components \
  STRATA_HOME=$root/local/state \
  XDG_STATE_HOME=$root/local/xdg-state \
  XDG_DATA_HOME=$root/local \
  PYTHONPATH=$root/local/strata-control \
    "$root/local/strata-control/python/bin/python3.12" -m strata_control.pictures fetch \
      --config "$run_config" \
      --engine-dir "$root/local/components/engine/0.1.59-linux-x86_64-cuda-cuda12" \
      --vision cpu
}

case "${1:-status}" in
  status) status ;;
  fetch)  fetch ;;
  apply)  apply ;;
  check)  check ;;
  pi)     pi ;;
  *)      sed -n '2,12p' "$0"; exit 2 ;;
esac
