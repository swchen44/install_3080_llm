# 執行進度

2026-11-15；完整證據見 `docs/research/execution.md`。使用者最新要求只測 Q3 或以上，Strata 的 IQ3_S 和 Q4 都要測；Dense 另測一個，固定 GPU power limit 250W，目標 decode >=30 tokens/s 且須通過 Codex 品質／工具測試。

- 已停止 IQ2_XS；320W 與 250W 的 IQ2 結果保留歷史用途，不納入後續選模。
- IQ3_S：已驗證主分片與共享 PLE 分片 SHA256，4K plan 下載 0；250W 4K 載入與 smoke 進行中。之後評估 1K / 64K / 128K / 256K。
- Q4：現有 Unsloth UD-Q4_K_XL 尚未驗證模型完整性、啟動與 benchmark。
- Dense：已驗證的 27B UD-Q4_K_M 尚未測。
- Codex 與品質：NOT_STARTED，吞吐成績不代表 coding 成功或品質無損。
- Windows A/B：WAITING_FOR_WINDOWS_BOOT。
