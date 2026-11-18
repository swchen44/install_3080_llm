---
title: 重啟與還原 Runbook（Strata 視覺 / LLM service / pi 對話）
subtitle: 2026-11-19，本機 RTX 3080 20 GB · Strata Terminal 0.2.13 · Engine 0.1.59 CUDA12
file: vision-restart-runbook-20261119
---

# 重啟與還原 Runbook

適用情況：要替本機 Strata 的 Qwen3.8-Flash-Next 啟用讀圖（vision），或任何需要重新載入模型的動作。
重點只有一句話：**載入模型要約 20 分鐘，而且正在跟 API 對話的 agent（包含 pi 這個對話）會被中斷**；中斷後用 `pi --continue` 就能回到同一份 context。

## 0. 現況快照（寫入時）

| 項目 | 值 |
|---|---|
| 執行中的模型 | Unsloth Qwen3.8-Flash-Next **UD-Q4_K_XL**，128K / KV int8 |
| 執行身分（profile） | `launch-ud-q4_k_xl-128k`，port `8080`，host `0.0.0.0`（`--access lan`） |
| run config | `local/xdg-state/strata/launch/ud-q4_k_xl-128k.json` |
| engine log | `local/xdg-state/strata/launch/ud-q4_k_xl-128k.engine.log` |
| API key | `local/hermes-private/api-key`（600、Git 忽略；**不要**貼進 Git 或日誌） |
| 品質基準環境變數 | `STRATA_ROUTE_TAIL_SKIP=0`、`STRATA_PREFILL_CPU_SHARE=0` |
| GPU power limit | 250 W（每次實驗前重新確認） |
| 載入實測 | `engine_ready_s: 1230`（約 20 分鐘） |
| 視覺權重目標檔 | `local/unsloth-data/models/mmproj-Qwen3.8-Flash-Next-BF16.gguf`，907,543,008 bytes，SHA-256 `b1a82259702816a5330d7bd7607cd9676b11780e79ff7348c21103ff3ce49bd0` |
| 這份對話的 pi session id | `01a1f0c4-6296-7062-acf2-387bdc8a0f49` |

## 1a. 準備已完成（2026-11-19 06:45）

mmproj 已下載並驗證完成，**重啟前不需要再做任何下載**：

| 項目 | 實測 |
|---|---|
| 路徑 | `local/unsloth-data/models/mmproj-Qwen3.8-Flash-Next-BF16.gguf` |
| 大小 | 907,543,008 bytes（與 pin 相同） |
| SHA-256 | `b1a82259702816a5330d7bd7607cd9676b11780e79ff7348c21103ff3ce49bd0` ✔ |
| 完成記號 | 同目錄 `*.gguf.done`，之後的啟動不會重新 hash |
| 下載日誌 | `logs/12-mmproj-fetch.txt`（结尾 `{"ok": true, ... "fetched": true}`） |
| 磁碟 | 下載後 `/` 仍剩約 57 GB |

`fetch` 回來的 vision 區段（重啟時由 launch 寫進 run config，現在尚未寫入）：

```json
{"exe": "local/components/engine/0.1.59-linux-x86_64-cuda-cuda12/strata-vision",
 "mmproj": "local/unsloth-data/models/mmproj-Qwen3.8-Flash-Next-BF16.gguf",
 "model": "~/Downloads/ai/models/llm/unsloth/Qwen3.8-Flash-Next-GGUF/UD-Q4_K_XL/Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf",
 "gpu": false, "max_tokens": 300, "threads": 10}
```

`gpu: false` 就是 `--vision cpu`（讀圖跑在 RAM，不佔 VRAM）。

## 1b. 相關準備的檢查（已完成，可略過）

```sh
cd /home/swchen/git/install_3080_llm
bash scripts/enable_vision.sh status     # 看缺什麼（唯讀）
bash scripts/enable_vision.sh fetch      # 只下載 0.9 GB 讀圖權重，不動伺服器
```

`fetch` 中斷可以直接再跑一次，`.part` 會續傳。驗證下載結果：

```sh
sha256sum local/unsloth-data/models/mmproj-Qwen3.8-Flash-Next-BF16.gguf
# 必須是 b1a82259702816a5330d7bd7607cd9676b11780e79ff7348c21103ff3ce49bd0，大小 907543008
```

抓不到 Hugging Face 時，自己放同名檔案到 `local/unsloth-data/models/` 或模型資料夾（`~/Downloads/ai/models/llm/unsloth/Qwen3.8-Flash-Next-GGUF/UD-Q4_K_XL/`）或其上一層，`fetch` 會驗 hash 後直接沿用。

## 2. 重啟（會中斷所有 API 客戶）

確認沒有人在工作後執行：

```sh
cd /home/swchen/git/install_3080_llm
bash scripts/enable_vision.sh apply 2>&1 | tee logs/12-vision-relaunch-$(date +%Y%m%d-%H%M).log
```

它做的是（等效手動指令，方便你改參數）：

```sh
cd /home/swchen/git/install_3080_llm
export STRATA_HOME=$PWD/local/state
export STRATA_COMPONENTS_DIR=$PWD/local/components
export XDG_STATE_HOME=$PWD/local/xdg-state
export PATH=$PWD/local/strata-control/bin:$PATH
export STRATA_LAN_KEY="$(cat local/hermes-private/api-key)"   # 用環境變數，避免 key 出現在 ps / 命令列
strata launch --family unsloth --model ud-q4_k_xl --context 128k \
  --vision cpu --drafting off --tune skip --access lan --port 8080 \
  --api-key-env STRATA_LAN_KEY \
  --set STRATA_ROUTE_TAIL_SKIP=0 --set STRATA_PREFILL_CPU_SHARE=0 \
  --restart --no-tui
```

必須保留的參數：`--access lan --port 8080` 與同一組 key（否則 Hermes、Codex、pi 全部斷線）、`--set STRATA_ROUTE_TAIL_SKIP=0 --set STRATA_PREFILL_CPU_SHARE=0`（品質基準，和既有量測一致）、`--context 128k`。
`--vision cpu` 是這張 20 GB 卡的建議值：GPU encoder 需要 23.5 GB 以上才划算，`--vision gpu` 會固定吃掉 1～1.4 GB VRAM 並拖慢 decode。

怕 terminal 被關掉導致 launch 中止的話，用 transient service 跑：

```sh
systemd-run --user --unit=strata-vision-relaunch --property=WorkingDirectory=/home/swchen/git/install_3080_llm \
  bash -lc 'bash scripts/enable_vision.sh apply > logs/12-vision-relaunch.log 2>&1'
```

## 3. 等待載入完成（約 20 分鐘）

```sh
cd /home/swchen/git/install_3080_llm
tail -f local/xdg-state/strata/launch/ud-q4_k_xl-128k.engine.log      # 看載入進度
watch -n 30 'curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $(cat local/hermes-private/api-key)" http://127.0.0.1:8080/v1/models'
```

出現 HTTP 200 且 `data[0].id` 是 `qwen3.8-flash-next-unsloth-ud-q4_k_xl` 才算就緒。此時 `bash scripts/enable_vision.sh status` 應該顯示 `vision {...}` 而不再是 `ABSENT`。

## 4. 驗收 LLM service 與讀圖

```sh
cd /home/swchen/git/install_3080_llm
KEY=$(cat local/hermes-private/api-key)
curl -s -H "Authorization: Bearer $KEY" http://127.0.0.1:8080/v1/models | head -c 400   # 文字 API 活的
python3 scripts/vision_check.py            # 送一張純紅圖，答案要出現「紅」
python3 scripts/vision_check.py --base http://192.168.10.99:8080   # LAN 那張网卡也要能收圖
```

`vision_check.py` 只用標準函式庫在記憶體裡產生紅圖，唯讀、不寫檔。它印 `VISION_OK` 代表 vision 段真的生效；印 `VISION_UNCLEAR` 就回去看 `status` 的 vision 區段與 engine log。

## 5. 通過驗收後，才讓 pi 送圖

```sh
cd /home/swchen/git/install_3080_llm
bash scripts/enable_vision.sh pi      # 把 models.json 的 input 改成 ["text","image"]，舊檔存成 .bak
pi --list-models                      # 該模型該顯示 images enabled
```

順序很重要：**伺服器還沒有 vision 之前不要改這行**，否則 pi 會送圖片給只会回文字的 server 而報錯。
Codex 端不用改：`wire_api = "responses"` 送的 `input_image` 由 Strata 的 `serve/responses.py` 直接接收。

## 6. 回到這份對話的 context

你重啟後，在同一個目錄執行 `pi --continue` 就能接回本文件第 0 節那個 session。

重啟後（或在另一個 terminal 現在就能開）：

```sh
cd /home/swchen/git/install_3080_llm          # session 是以工作目錄分檔，一定要在同一個目錄
pi --continue                    # 續這個目錄最近的一次 session（最常用）
pi --resume                      # 列出 sessions 讓你挑
pi --session 01a1f0c4            # 直接開這份：01a1f0c4-6296-7062-acf2-387bdc8a0f49
```

補充：

- session 檔在 `local/pi-agent-home/sessions/--home-swchen-git-install_3080_llm--/`，`/local/` 被 Git 忽略，不會進 repo。
- `pi` 是 `/home/swchen/.local/bin/pi` 那個 wrapper，會自己帶 `PI_CODING_AGENT_DIR=local/pi-agent-home`，不要直接叫 `local/pi-agent/bin/pi`。
- 模型 id 重啟前後都是 `qwen3.8-flash-next-unsloth-ud-q4_k_xl`，所以舊 session 可以無痛接回去；只需重送被中斷的最後一句。
- 想保留「重啟前」的狀態當對照，用 `pi --fork 01a1f0c4` 分叉，不要在原 session 上反覆試。

## 7. 其他不是開機自動啟動的服務

Strata 的模型伺服器與 Hermes dashboard 都是手動／transient 啟動，重開機後要自己拉起來。

```sh
# Strata：已經有 vision 的 run config，重啟最省事的是
strata runtime restart --profile ud-q4_k_xl-128k --no-tui   # 或重跑 scripts/enable_vision.sh apply

# Hermes dashboard（LAN 192.168.10.99:9119）
systemd-run --user --unit=hermes-dashboard-3080 \
  --property=WorkingDirectory=/home/swchen/git/install_3080_llm/local/hermes-agent \
  --setenv=HERMES_HOME=/home/swchen/git/install_3080_llm/local/hermes-home \
  --setenv=PATH=/home/swchen/git/install_3080_llm/local/hermes-js/node_modules/.bin:/home/swchen/git/install_3080_llm/local/hermes-venv/bin:/usr/local/bin:/usr/bin:/bin \
  /home/swchen/git/install_3080_llm/local/hermes-venv/bin/hermes dashboard \
  --skip-build --host 192.168.10.99 --port 9119 --no-open
```

實驗用的功耗上限每次重新確認：

```sh
sudo -n nvidia-smi -i 0 -pl 250 && nvidia-smi --query-gpu=power.limit --format=csv,noheader
```

## 8. 回退方式

讀圖造成問題（VRAM 吃緊、decode 變慢、回覆異常）時，把 vision 關掉重載，其他參數不變：

```sh
cd /home/swchen/git/install_3080_llm
export STRATA_HOME=$PWD/local/state STRATA_COMPONENTS_DIR=$PWD/local/components XDG_STATE_HOME=$PWD/local/xdg-state
export PATH=$PWD/local/strata-control/bin:$PATH STRATA_LAN_KEY="$(cat local/hermes-private/api-key)"
strata launch --family unsloth --model ud-q4_k_xl --context 128k \
  --vision off --drafting off --tune skip --access lan --port 8080 --api-key-env STRATA_LAN_KEY \
  --set STRATA_ROUTE_TAIL_SKIP=0 --set STRATA_PREFILL_CPU_SHARE=0 --restart --no-tui
bash scripts/enable_vision.sh pi   # 把 pi 的 input 改回 text（或還原 models.json.bak）
```

mmproj 檔案本身留著不影響純文字執行，之後要再開 vision 不用重新下載。

## 9. 疑難排解

| 狀況 | 處理 |
|---|---|
| `/v1/models` 回 401 `missing or wrong API key` | 沒帶 key 或 key 不同於 `local/hermes-private/api-key`；`--api-key-env` 重帶 |
| 重啟中 request 失敗／掛住 | 模型還沒 ready（real time 約 20 分鐘），看 engine log 與 `/v1/models` 直到 200 |
| `fetch` 說 disk 不足 | `df -h /`；目前剩約 57 GB。清 `local/unsloth-data/packs/` 內不再用的 pack 前先確認對應模型不再使用 |
| Hugging Face 連不上 | 手動放 mmproj 檔（見第 1 節），`fetch` 只驗 hash 不重複下載 |
| 改完 `models.json` 沒効果 | pi 啟動時才讀設定，重開 pi（`pi --continue`） |
| vision 開了但回 `VISION_UNCLEAR` | 確認 `enable_vision.sh status` 有 vision 區段、engine log 有起 `strata-vision` 行程，且 mmproj hash 正確 |
| decode 變慢 | 檢查是否被改成 `--vision gpu`（多佔 1～1.4 GB VRAM），以及 `nvidia-smi` power limit 是否仍是 250 W |

相關文件：`docs/research/hermes-strata-20261118.md`、`docs/research/pi-agent-strata-20261118.md`、`docs/research/execution.md`、進度見根目錄 `progress.md`。
