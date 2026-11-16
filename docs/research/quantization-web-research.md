# Strata Qwen Flash 量化選擇：網路經驗與本機範圍

查閱日期：2026-11-15。網路經驗只作為背景，硬體、量化、KV、推理引擎、context、prompt 與評分方式不一致，不能直接當成本機品質或速度結果。

## 本機這次要測的模型

| 用途 | 模型 | 量化 | 檔案狀態 |
|---|---|---|---|
| Flash / Strata | Qwen3.8-Flash-Next ISTA-DASLab | IQ3_S | 已在本機；已核 SHA256 |
| Flash / Strata | Qwen3.8-Flash-Next Unsloth | UD-Q4_K_XL | 已在下載目錄；待實測前核 SHA256 |
| Dense / llama.cpp | Qwen3.8-27B | UD-Q4_K_M | 已在本機；已核 SHA256 |

核對 `local/`、`~/Downloads/ai/models/llm/others`、`~/Downloads/ai/models/llm/unsloth` 及 `~/Downloads/ai/FILE_LIST.md`，沒有找到 Flash 或 27B 的 Q5/Q6 模型檔案；計畫內也沒有 Q5/Q6 下載。此次實機上限維持 Q4，沒有為 Q5/Q6 下載任何東西。

## 已查到的 Q5/Q6 使用經驗

- Strata 專案有 [UD-Q6_K_XL 支援與核心測試說明](https://github.com/Niko1221/Strata/blob/main/docs/UNSLOTH_Q6.md)，也明確註記該頁**沒有** Q6 相對 llama.cpp 的品質測量。因此，該文件證明格式／kernel 支援，不等於 Q6 品質與 Q4 相同。
- [Unsloth 公開的 Qwen3.8-Flash-Next GGUF benchmark 表](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/blob/main/README.md)提供模型級任務成績：Flash-Next 對 27B 在 DeepSWE 1.1 為 58.7 對 42.2、SWE-bench Pro 為 62.5 對 61.7、LiveCodeBench v6 為 91.9 對 90.3。這些是模型報告的 benchmark，不是 Q5/Q6 vs Q4 量化對照，也不是此機 GGUF/Strata 跑分。
- [Strata 使用者的 Q6 日常回報](https://www.reddit.com/r/LocalLLaMA/comments/1x92rdf/what_quant_do_you_actually_use_day_to_day_anyone/)稱其 coding benchmark 沒看到能力損失；這是個人測試與自述，沒有足夠資料證明普遍「品質相同」。同一討論也有使用者覺得 2/3-bit 品質不滿意，顯示任務與偏好會影響結論。
- [27B 與 Flash-Next 的 coding agent 對照自述](https://www.reddit.com/r/Qwen_AI/comments/1wd7q2q/qwen38-27b-vs-flash-next-for-agentic-coding-same/)是在 128GB Strix Halo、llama.cpp、Pi 上測，作者報告自己的 5 個 coding tasks 皆 5/5，Flash-Next 用 token 較少。硬體、量化、agent harness 和樣本數都不同，不能預測本機哪個更適合 Codex。
- Strata 相關 [Q5/Q6 GGUF 檔案與 Expert/Ple 結構彙整](https://github.com/ByronScottJones/Moe-llama.cpp/blob/main/docs/Qwen3.8-Flash-Next.md)列 UD-Q4_K_XL 約 103.7 GB、UD-Q5_K_XL 約 147.4 GB、UD-Q6_K_XL 約 157.5 GB。其資料顯示 Q5/Q6 的 Expert 與 PLE 記憶體總量大幅提高；作者的硬體和快取架構不同，這只能說明容量成本上升，不能推斷本機速度。下載前還須依實際發行版本與 Strata 文件核對檔案大小與 hash。

## 對本次實驗的決定

使用者確認：本次不下載 Q5/Q6；Flash 實機只到 IQ3_S 和既有 UD-Q4_K_XL，另以既有 Qwen3.8-27B UD-Q4_K_M 測一個 Dense。`128GB` 是主機 RAM，不會令 Q5/Q6 在 20GB VRAM 上自動加速；更大權重須在 RAM／SSD／GPU 之間分配，並可能增加載入、換頁或專家讀取延遲。沒有本機 Q5/Q6 模型檔案，也不以網路個人心得宣稱它們品質「差不多」。

## 來源

- [Strata 官方 Q6 文件](https://github.com/Niko1221/Strata/blob/main/docs/UNSLOTH_Q6.md)
- [Unsloth Qwen3.8-Flash-Next GGUF README 與模型級 benchmark](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/blob/main/README.md)
- [使用者日常量化經驗討論](https://www.reddit.com/r/LocalLLaMA/comments/1x92rdf/what_quant_do_you_actually_use_day_to_day_anyone/)
- [27B vs Flash-Next 個人 coding agent 測試](https://www.reddit.com/r/Qwen_AI/comments/1wd7q2q/qwen38-27b-vs-flash-next-for-agentic-coding-same/)
- [UD-Q4/Q5/Q6 GGUF 檔案與 Expert/PLE 大小彙整](https://github.com/ByronScottJones/Moe-llama.cpp/blob/main/docs/Qwen3.8-Flash-Next.md)
