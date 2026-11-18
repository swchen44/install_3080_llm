# 執行進度

2026-11-19 更新；完整證據見 `docs/research/execution.md` 與 `docs/research/hermes-strata-20261118.md`、`docs/research/pi-agent-strata-20261118.md`。約束：只測 Q3 或以上，IQ3_S 與 UD-Q4_K_XL 都要測，Dense 另測一個；固定 GPU power limit 250W；目標 decode >=30 tokens/s 且須通過 Codex 品質／工具測試。

## 選型結論（目前機器與配置）

- 主要方案：Strata Qwen3.8-Flash-Next **UD-Q4_K_XL**，128K/int8，現為 pi、Codex 與 Hermes 的實際服務模型（`127.0.0.1:8080`、LAN `192.168.10.99:8080`）。
- 最快候選：ISTA **IQ3_S**，1K/64K/128K/256K decode 中位數 71.43 / 64.27 / 61.86 / 55.31 tok/s。
- UD-Q4_K_XL 同四級 decode 48.95（1K）/ 45.18（64K）/ 44.71（128K）/ 43.14（256K）tok/s，全部超過 30 tok/s 門檻。
- Dense Qwen3.8-27B UD-Q4_K_M：4K 直接 API 36.28 tok/s，但 64K CPU KV 只剩 2.99 tok/s，Codex 需 n_ctx 8192 且 session 約 9 tok/s，淘汰。
- 品質樣本：IQ3_S 與 Q4 在 128K/256K 的六欄位合成 needle-recall 都是 6/6；Codex CLI 0.169.0 的 T1/T2/T3 fixture 兩者結果一致。皆為小型合成樣本，不能宣稱與未量化模型品質等同。
- Q2／IQ2 已依指示移除，僅留歷史紀錄。

## 2026-11-18 部署已完成

Hermes Agent v0.23.2（隔離 venv／home）、Hermes Web dashboard（`192.168.10.99:9119`，basic auth）、pi coding agent 1.5.2（`local/pi-agent-home`，`openai-responses` 連 8080）皆安裝並驗收：文字回覆、bash 工具呼叫、Responses 串流與 `function_call` 完整回合均通過。key 放在 Git 忽略、權限 600 的 `local/hermes-private/`，不入 Git 與日誌。

## 進行中：視覺（VLM）

引擎已附 `strata-vision` 且 `vision_archs` 含 sm_86，缺 0.9 GB 的 `mmproj-Qwen3.8-Flash-Next-BF16.gguf`、run config 的 `vision` 區段、以及 pi `models.json` 的 `"input": ["text","image"]`。

- `scripts/enable_vision.sh status|apply|check|pi` 與 `scripts/vision_check.py` 為新增的開關與驗收工具。
- mmproj 下載不影響執行中的伺服器；`apply` 會重載模型（實測 `engine_ready_s` 1230，約 20 分鐘）並中斷所有 API 客戶，包括正在使用的 agent 對話，需使用者擇時執行。
- `--vision cpu` 用於這張 20 GB 卡（低於 23.5 GB 的 GPU encoder 門檻）；`--vision gpu` 固定佔 1～1.4 GB VRAM 且會拖慢 decode。

## 待辦

- 擇時執行 `scripts/enable_vision.sh apply` + `check`，完成後再開放 pi 的 image 輸入。
- Windows A/B：WAITING_FOR_WINDOWS_BOOT。
- 更大規模的長 context coding 品質集與真實 Codex 工作負載；現有結論僅基於小型 fixture 與合成 needle recall。
- Answer me with HTML 有 0.6.1 可更新（目前 0.5.11），待使用者決定。
