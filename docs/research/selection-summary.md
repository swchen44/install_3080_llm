# RTX 3080 20GB 本機 Qwen 選型摘要

日期：2026-11-15。測試主機 RTX 3080 20GB、主機 RAM 128 GiB；所有本輪 GPU 測試都將 power limit 固定為 250W。只使用已下載模型：Strata Qwen3.8-Flash-Next IQ3_S 與 Unsloth UD-Q4_K_XL、Dense Qwen3.8-27B UD-Q4_K_M。沒有下載 Q5/Q6。完整步驟、命令、異常和原始資料見 [`execution.md`](execution.md)、[`progress.md`](progress.md) 和 [`quantization-web-research.md`](quantization-web-research.md)。

## 建議

**優先建議：Strata + Qwen3.8-Flash-Next UD-Q4_K_XL，平時 context 設為 128K；只有提示確實超過 128K 時才提高到 256K。** 在這張 3080 上，Q4 在 128K 的 decode 中位數 44.71 tok/s，prefill 2,177 tok/s，TTFT 57.87s；256K decode 43.14 tok/s，prefill 2,026 tok/s，TTFT 124.29s。兩種 context 都超過 30 tok/s，並完成 Codex CLI 0.169.0 的小型讀取／除錯／修正 fixture。

若更重視速度、磁碟與 RAM 用量，可選 **Strata IQ3_S**：128K decode 61.86 tok/s、256K 55.31 tok/s；在本次固定 coding fixture 與六點合成 retrieval 上，未觀察到 IQ3_S 和 Q4 的差異。這不是廣泛品質等價證明。兩種 Strata 量化都達到既定速度門檻。

**不建議把 Qwen3.8-27B Dense UD-Q4_K_M 當作這次的主 Codex 模型。** 它的 4K 直接 API 短 prompt decode 為 36.28 tok/s、prefill 1,014.52 tok/s，但 Codex 的首個 4K 請求已達 6,095 tokens，遭 4,096 context 拒絕。8K CPU-KV 的 Codex fixture 能完成讀取、分析與修改，測試 2/2 PASS，但實際 session 約 9 tok/s，且最終反覆驗證未正常收束。64K CPU-KV pilot 的 decode 只有 2.99 tok/s；因此 Dense 未達「Codex 實用速度至少 30 tok/s」的整體要求。Dense 在不同推理引擎或 KV 放置配置下可能不同，但本次沒有證據支持它達標。

## 實測數字

下表是 direct API benchmark 中位數，輸入 tokens 約為該級 context 的 95%，每級 warmup 1 次、正式 3 次；Dense 64K 是單次完整 warmup pilot，非正式三次基準。

| 模型／量化 | 設定 context | 實際輸入 tokens | Prefill tok/s | Decode tok/s | TTFT |
|---|---:|---:|---:|---:|---:|
| Flash-Next IQ3_S | 1K | 753–755 | 355.86 | 71.43 | 2.14s |
| Flash-Next IQ3_S | 64K | 約 62.9K | 2,078.70 | 64.27 | 30.33s |
| Flash-Next IQ3_S | 128K | 約 125.7K | 2,246.00 | 61.86 | 56.09s |
| Flash-Next IQ3_S | 256K | 約 251.3K | 2,144.83 | 55.31 | 117.41s |
| Flash-Next UD-Q4_K_XL | 1K | 751–755 | 209.41 | 48.95 | 3.63s |
| Flash-Next UD-Q4_K_XL | 64K | 約 62.9K | 1,972.09 | 45.18 | 31.98s |
| Flash-Next UD-Q4_K_XL | 128K | 約 125.7K | 2,177.04 | 44.71 | 57.87s |
| Flash-Next UD-Q4_K_XL | 256K | 約 251.3K | 2,025.74 | 43.14 | 124.29s |
| Qwen3.8-27B Dense UD-Q4_K_M | 4K | 約 0.75K | 1,014.52 | 36.28 | 約 0.82s |
| Qwen3.8-27B Dense UD-Q4_K_M | 128K server / 64K prompt | 62,874 | 638.22 | 2.99 | 99.83s |

Dense 長文的 64K 數字使用 `--no-kv-offload`，即 KV 留在主機 RAM；Dense 4K 和其他 Dense configuration 不可直接套用該長文速度。長文 pilot 完整輸出 256 tokens，無 cache hit、無 benchmark flags。`prefill` 表示讀取輸入速度；`decode` 表示生成速度。TTFT 為首 token 延遲。

## 品質證據與限制

- IQ3_S 與 Q4 在 128K、256K 的六個固定合成 needle facts 均答對 6/6。這只測一種精確回憶，不代表真實程式碼庫理解或一般長文品質。
- IQ3_S 與 Q4 各自在同一個小型 Codex fixture 完成 T1 讀 README、T2 定位邊界問題、T3 一行修正並令兩個 unittest 通過；兩者結果相同。這不足以衡量大型程式庫或多輪長任務的品質。
- Dense 在小型 fixture 能找出 5kg 邊界錯誤並完成修正，Codex 在重複驗證階段沒有正常結束。Dense 與 Strata 用不同 inference server，數據是端到端配置的比較，不是純模型權重 A/B。
- 256K 雖能運作並保有超過 30 tok/s decode，但 TTFT 約 2 分鐘。日常預設 128K 更平衡；超長任務才切到 256K。
- 128 GiB RAM 能容納主機側 KV 和大型模型資料，但不能替代 GPU 記憶體頻寬；Dense 64K pilot 的約 3 tok/s 清楚顯示這點。
- 本地沒有 Q5/Q6 權重，本次沒有下載或測試 Q5/Q6；線上個人經驗無法證明它們相對 Q4 的品質差異。

## 複現入口

- IQ3_S 原始 benchmark：`results/ubuntu/strata/flash-next/20261115/iq3-quality-250w-128k-{1k,64k,128k}/` 與 `.../iq3-quality-250w-256k-256k/`。
- Q4 原始 benchmark：`results/ubuntu/strata/flash-next/20261115/unsloth-q4-quality-250w-128k-64k-128k/`、`.../unsloth-q4-quality-250w-256k/`。
- Dense 4K：`results/ubuntu/llama-cpp/qwen27b/20261115/q4km-quality-250w-4k-1k/`。
- Dense 64K pilot：`results/ubuntu/llama-cpp/qwen27b/20261115/q4km-quality-250w-128k-64k-128k/level-64k/requests.jsonl`。
- Codex 與 Dense server log：`docs/research/logs/08-q4-codex-*`、`09-iq3-codex-*`、`10-dense-codex-*`。
- 研究結論與參考連結：[`quantization-web-research.md`](quantization-web-research.md)。
