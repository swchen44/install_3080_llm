# RTX 3080 / Strata 先例與部署依據

查閱日期：2026-11-14。先例為使用者自述，並非本機跑分，也無法直接當成此 DDR3 平台的預期速度。

- [單張改裝 RTX 3080 20GB + Xeon E5-2680 v4、64GB DDR4 的使用者經驗](https://www.reddit.com/r/LocalLLM/comments/1ww2o2v/qwen38flashnext_iq2_xs/)：使用者自述 IQ2_XS、256K context、75–81 tokens/s；帖子未提供完整可重現的軟體版本、模型雜湊及測量方法。是最接近的硬體先例，不代表本機一定相同。
- [RTX 3080 筆電討論串](https://www.reddit.com/r/LocalLLaMA/comments/1wwwmy1/running_qwen38_flash_next_176b_on_a_16gb_rtx_3080/) 有其他 GPU/RAM 使用者分享 Strata 設定；其 Windows、不同模型及容量不能直接套到 Linux 單張桌面卡。
- [四張 3080 20GB 的 Strata 經驗](https://www.reddit.com/r/LocalLLM/comments/1wy2bld/4x_3080_20gb_modded_alibaba_strata_qwen_flash/) 是多卡配置，不宜作為單卡性能預測。
- [Strata 官方專案](https://github.com/Niko1221/Strata)支援 RTX 30 系列並列出 ISTA-DASLab 的 GSQ-RCO 與 Unsloth 不同量化；同名 IQ2_XS 不保證來自不同發行者的 GGUF 可互換。[模型來源](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF)。

本機 bartowski IQ2_XS 在 0.2.13 轉換後實際仍因 `token_embd.weight` 的形狀或 GPU dequantizer 不相容而停止；錯誤無法單獨判定是哪一種。停止對該模型的試驗。現有 Unsloth UD-Q4_K_XL 被本地版本列為支援，但約 111.3 GB，須先以該版本文件評估準備空間、記憶體與量化差異；尚未啟動或驗證，不能把它當作 IQ2_XS 的成績。

計畫首選的官方 ISTA-DASLab IQ2_XS 不在現有目錄。若使用者要在學校下載，本機 0.2.13 的 `setup.py` 固定 revision `ed59f92082b1e93c0e96d60a8b11aab089b52f09`，兩檔放在同一目錄：

| 檔案 | 大小 bytes | SHA256 |
|---|---:|---|
| [00001-of-00002](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/resolve/ed59f92082b1e93c0e96d60a8b11aab089b52f09/IQ2_XS/Qwen3.8-Flash-Next-GSQ-RCO-IQ2_XS-00001-of-00002.gguf) | 39225954592 | `92cee27ae5bbadcd732416a0f7a7f0acc092399dbbe8f5a5efa707c2ec0a49d7` |
| [00002-of-00002](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/resolve/ed59f92082b1e93c0e96d60a8b11aab089b52f09/IQ2_XS/Qwen3.8-Flash-Next-GSQ-RCO-IQ2_XS-00002-of-00002.gguf) | 28800138432 | `316b46f3a2dbd68c900f43136ab9449f9dcc3725dfd8c794847c204bc161e113` |

總計 68.026 GB（十進位）。這是建議下載清單，尚未下載；vision 與 drafting 關閉不需要額外模型。下載後以 `sha256sum` 逐檔核對再執行 `--plan`，先從 4K smoke 開始。

## 補充：lcz.me 與 128GB DDR3 的量化選擇（2026-11-14）

- [X99 DDR3 + 單張 3080 20GB 的三種量化實測](https://lcz.me/topic/2988/7)：雙路 E5-2696 v3、256GB DDR3、Ubuntu 24.04.5、driver 595.99.02、Strata 0.2.12 / Engine 0.1.58。作者日常用 IQ2_XS 求速度，推薦 IQ3_S 做程式和長文；也測了 UD-Q4_K_XL。這是非常相近但雙 CPU／雙倍 RAM 的個案；三組有不同控制向量、KV 與 drafter，大多每級一次，不能視為受控品質／速度比較，更不能外推本機數值。
- [單張 3080 20GB IQ2_XS](https://lcz.me/topic/1987)：E5-2690 v4、45GiB RAM、128K 設定、int8 KV、MTP4，短測 57.8 t/s；作者明確說未測接近 128K 的真實輸入。
- [單張 3080 20GB、56GB DDR4、IQ3_S](https://www.reddit.com/r/LocalLLaMA/comments/1x85hfj/strata_qwen_38_flash_next_fast_but_whats_it/) 自述 262K context 50 t/s，無完整設定與測量方法。
- [Strata 官方模型記憶體表](https://github.com/Niko1221/Strata/blob/main/docs/MODELS.md)：IQ3_S 專家約 50 GB；IQ2_XS 約 35.5 GB，還要留系統及 context 空間。現有 125GiB RAM 令 IQ3_S 值得優先測，但 DDR3 頻寬、KV、VRAM、PCIe 及實際 RAM 使用決定性能。

歷史下載安排：若要重建當時的 IQ3_S，除第 1 主分片外，還需要可共用的第 2 lookup-table 分片：
https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/resolve/ed59f92082b1e93c0e96d60a8b11aab089b52f09/IQ3_S/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf
大小 54,817,524,224 bytes；SHA256 `4c1eb2ceb4915e1192f4f386021897bde56a97f40a0bb78bb86465e0f7d2aca3`。
第二分片與同 revision IQ2_XS 第 2 片在本版 setup 的固定 SHA256 完全相同（`316b46f3a2dbd68c900f43136ab9449f9dcc3725dfd8c794847c204bc161e113`，28,800,138,432 bytes），因此可以共用一份；檔名和 IQ3_S loader 路徑須符合格式。直接下載備用：
https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/resolve/ed59f92082b1e93c0e96d60a8b11aab089b52f09/IQ3_S/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf

保守起點：4K smoke、vision off、parallel 1、tune skip、drafting off，從已驗證 4K 逐步到 128K，KV 明確記錄 int8，使用 engine auto expert-cache。先做計畫 baseline，不直接照抄別人的 fp16 KV、MTP、DFlash2、自訂 pool-workers 或 VRAM reserve；等 baseline 與 Codex 驗收後單因素測試。不得開外網、修改 driver、功耗或 kernel。

2026-11-14 再核對 Hugging Face 固定 revision 的模型 API（`?blobs=true`）：IQ2_XS 與 IQ3_S 第 2 分片的 LFS SHA256 均為 `316b46f3a2dbd68c900f43136ab9449f9dcc3725dfd8c794847c204bc161e113`，大小均 28,800,138,432 bytes，blobId 亦相同。之後實體檔案通過 SHA 驗證並供 IQ3_S 使用。2026-11-15 清理 Q2 時將該共用檔移到 `~/Downloads/ai/models/llm/others/Qwen3.8-Flash-Next/shared/Qwen3.8-Flash-Next-GSQ-RCO-common-lookup-00002-of-00002.gguf`，IQ3_S 測試連結已更新且移動後 hash 相同。清理證據：`docs/research/logs/11-q2-cleanup.txt`。
