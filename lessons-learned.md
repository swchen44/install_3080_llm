# 執行紀錄與注意事項

- 實際下載目錄為 `~/Downloads/ai/`，不是 `~/Download/ai/`。檔案清單為 `~/Downloads/ai/FILE_LIST.md`。
- 本地官方 Terminal 包含 Python runtime；不需要執行網路安裝腳本或修改 PATH。Control、Engine、Strata 原始碼封存 SHA256 符合清單。
- `strata launch --plan` 確認使用指定模型路徑不代表模型分片已驗證或可供引擎載入；必須實測。`STRATA_ENGINE` 單獨設置未令 launch 的 engine 預檢視為已安裝，改用官方 `components install-file` 至獨立專案目錄。
- kernel log 中網卡訊息包含 `XID 541`，不是 NVIDIA GPU Xid；NVRM 僅見驅動載入訊息。
- `--plan` 沒有計入準備模型需要的約 40 MB llama.cpp 原始碼；setup 實際下載了固定 commit 3cf03257f219afbe7334045ff7c6a06ac68c627d。現有來源 commit 不同，不能假設可替代。事後詳見 `docs/research/execution.md`。
- bartowski IQ2_XS 非計畫所指 ISTA-DASLab GSQ-RCO。相容 BF16 轉換後仍因 native embedding 檢查失敗，不應將 `--plan` 成功誤認為相容。實驗 pack 與模型檔可分離回滾，未更動原模型內容。
- 2026-11-15：新 ISTA 模型已通過 4K API smoke；先手動於獨立資料目錄建立與模型匹配的官方 pack，防止 setup 因搜尋其他既有資料目錄而錯用先前 bartowski pack。專案內 symbolic links 避免修改下載的 GGUF。
- Engine 回報 PLE 沒有 memory lock、hugepages unavailable，但已成功推論；不變更 ulimit、kernel 或其他系統設定。真實比較要記錄這些條件。
- Strata 0.2.13 的 setup 對 <=8192 context 固定 fp16 KV，即便指定 `--kv int8`；信任 `/metrics` 實際值。Anthropic token count 與本次 Chat smoke 對相同訊息回傳 65 vs 25，模板／設定不等價，不能直接作 Chat token 準據。
- 2026-11-15：64K 長輸入校準與 warmup 後，雖 MemAvailable 約 81GiB，Strata engine 的 VmSwap 升至約 2.06GiB；已停後續長測並保留取消紀錄。應量測 swap 使用及 pswpin/pswpout 增量，不能只以 MemAvailable 排除換頁。
- 250W 由使用者明確指定；一般帳號 `nvidia-smi -i 0 -pl 250` 因權限不足失敗，實際仍 320W。計畫禁止 sudo，需使用者自行設好再驗證，所有舊結果標 320W。
- 使用者其後已明確授權 sudo，並將全部後續實驗功耗上限設為 250W；2026-11-15 已設定並核對。上方有關禁止 sudo / 等待使用者的敘述為當時狀態，現已失效。
