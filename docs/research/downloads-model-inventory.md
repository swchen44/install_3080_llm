# `~/Downloads/ai` 模型盤點與用途分類

盤點日期：2026-11-15（Asia/Taipei）。依檔案清單、實驗紀錄、hash 記錄與當下 GPU/process 狀態整理。此文件區分「當下正在執行」與「目前選定/最近測試」，避免把模型已下載誤認為服務正在使用。

## 當下狀態

- `nvidia-smi`: RTX 3080 20GB，VRAM 105 MiB，power limit 250 W，實際功耗約 14.6 W。
- 沒有 Strata、llama-server 或 ComfyUI generation process 正在執行。當下沒有任何模型載入 GPU。
- 最近完成並作為 Codex 選型的 Flash 主力是 Unsloth UD-Q4_K_XL；IQ3_S 是更快的候選。這是實驗/設定上的用途，不表示現在有 server 在跑。
- 清理後 `~/Downloads/ai/models/llm` 約 211.52 GB；`models/comfyui` 約 28.17 GB。Q2 權重與 Q2 專用 pack 已刪；IQ3_S 共用分片改放到中性 `shared/` 路徑。

## LLM 模型

| 模型檔案 | 下載目錄占用 | 已做的事 | 分類與理由 |
|---|---:|---|---|
| Qwen3.8-Flash-Next Unsloth UD-Q4_K_XL，4 shards | 111.33 GB | SHA-256 四片全數核對；Strata 250W 下測 1K、64K、128K、256K；完成固定 Codex T1/T2/T3 fixture，和長文檢索 probe | **目前主力候選／建議日常使用**。128K decode 中位 44.71 tok/s，256K 43.14 tok/s；小型 Codex fixture 通過。這不是此刻正在執行的 server。 |
| Qwen3.8-Flash-Next ISTA-DASLab GSQ-RCO IQ3_S，第 1 shard | 54.82 GB；第 2 shard與 IQ2_XS 共用 | SHA-256 驗證；Strata 250W 下測 1K、64K、128K、256K；Codex T1/T2/T3 和固定檢索 probe 完成 | **保留作較快候選**。128K decode 61.86 tok/s，256K 55.31 tok/s。小樣本上與 Q4 fixture 結果相同，但不足以證明兩者整體品質相等。 |
| Qwen3.8-27B Dense UD-Q4_K_M | 16.56 GB | llama.cpp 4K benchmark；64K CPU-KV pilot；Codex T1/T2/T3 fixture | **不是目前 Codex 主力；有特定情境才留用**。4K 短 prompt 36.28 tok/s；目前 64K CPU-KV pilot 2.99 tok/s，實際 Codex 長回覆約 9 tok/s。若未來只做短上下文、低頻工作或更換 runtime，可再評估。 |
| Qwen3.8-Flash-Next ISTA-DASLab GSQ-RCO IQ2_XS | 權重已移除；僅保留共用 lookup shard | Q2 第一分片及專用 pack 已刪，歷史紀錄保留 | **已清除**。共用分片已移到 `models/llm/others/Qwen3.8-Flash-Next/shared/`，IQ3_S 仍可用。 |
| Qwen3.8-Flash-Next bartowski IQ2_XS | 已移除，原占 77.74 GB | 先前試載在 `token_embd.weight` 附近遇 compatibility/dequantizer 錯誤；錯誤不能單獨定位是模型轉換或 runtime | **已清除**。 |

### IQ3_S 分片說明

下載目錄的 IQ3_S 子目錄只有第 1 shard（54,817,524,224 bytes）。原本第 2 shard symlink 指向 IQ2_XS 的共用 lookup table。清理時將該分片移至 `models/llm/others/Qwen3.8-Flash-Next/shared/Qwen3.8-Flash-Next-GSQ-RCO-common-lookup-00002-of-00002.gguf`，並更新 IQ3_S symlink。移動後 SHA-256 仍為 `316b46f3a2dbd68c900f43136ab9449f9dcc3725dfd8c794847c204bc161e113`；IQ3_S 連結已確認解析到新位置。完整記錄在 `docs/research/logs/11-q2-cleanup.txt`。

## ComfyUI 影音模型

| 模型 | 下載位置／占用 | 狀態 | 後續用途 |
|---|---|---|---|
| Wan 2.2 TI2V 5B FP16 | `models/comfyui/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors`，10.00 GB | 未見本輪生成紀錄 | **未來可能用**作其他 T2V/I2V 工作流或和 H3 作非競賽用途比較；lcz.me 3045 指定 MiniMax H3，因此不能代替本輪參賽模型。 |
| Wan 2.2 VAE | `models/comfyui/vae/wan2.2_vae.safetensors`，1.41 GB | 未見本輪生成紀錄 | **只在使用 Wan 2.2 時配套使用**。 |
| UMT5 XXL FP8 scaled | `models/comfyui/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors`，6.74 GB | 未見本輪生成紀錄 | **只在相容的 Wan 工作流中配套使用**。 |
| ACE-Step 1.5 Turbo AIO | `models/comfyui/checkpoints/ace_step_1.5_turbo_aio.safetensors`，10.03 GB | 未見本輪生成紀錄 | **未來可能用**作音樂生成；和 H3 影片競賽無關。 |
| MiniMax H3 權重 | 目前不在 `~/Downloads/ai/models` | 尚未下載、尚未生成 | **下一個 H3 實驗需要**。已列在 `docs/research/minimax-h3-3080-lcz3045.md`，兩個 >10GB 權重需先由使用者下載。 |

## 工具檔，不是模型權重

- Strata 0.2.13、Strata Engine 0.1.59 CUDA 12、control 包：支援本輪 Flash 模型實驗，且實驗已完成。當下沒有 Strata server 執行。
- llama.cpp b12375 CUDA 12.8：支援 Dense 27B 試驗，Dense 本輪測試已停止。
- ComfyUI Windows portable：已下載，但目前主機研究環境是 Ubuntu，這不是已安裝且可直接執行的 Linux ComfyUI runtime。
- ComfyUI source archive、ACE-Step source、LTX Desktop/source、LTX Video source：保留作未來安裝或影音工作流用途；不等於模型權重，也沒有代表它們已經跑過。
- Ubuntu ISO、Python embed 分片、其他壓縮檔和 `.done` 標記不是模型。

## 使用建議

1. Codex 日常先選 Strata + Flash-Next UD-Q4_K_XL，context 通常設 128K；有明確需要時再切 256K。
2. 需要更快回覆、且可接受本次品質證據範圍有限時，可切 Strata + IQ3_S。
3. Dense 27B 暫不作長上下文 Codex 主力；可保留做短上下文任務或未來替代引擎測試。
4. IQ2_XS 模型權重已清除。保留在 `shared/` 的單一 lookup shard 不是完整模型，仍供 IQ3_S 使用。
5. H3 尚未下載。先依 H3 research report 下載大於 10GB 權重並準備足夠磁碟空間；Wan 與 ACE-Step 不能替代指定的 H3。

## 可追溯證據

- 整體選型和限制：`docs/research/selection-summary.md`
- 實驗執行紀錄：`docs/research/execution.md`、`docs/research/progress.md`
- 已下載模型 SHA-256：`docs/research/logs/04-downloaded-models.sha256`、`docs/research/logs/08-unsloth-q4-sha256.txt`、`docs/research/logs/10-qwen27b-q4-sha256.txt`
- IQ2/IQ3 共用分片解釋：`docs/research/3080-guides.md`

## 清理結果

- 已移除 bartowski IQ2_XS 兩分片（77,737,182,784 bytes）與 ISTA IQ2_XS 第 1 分片（39,225,954,592 bytes）。
- 已刪除兩份 Q2 專用 Strata packs，各 1,538,035,200 bytes；歷史 benchmark logs 和結果保留。
- ISTA 第 2 分片（28,800,138,432 bytes）移入 `shared/`，不是完整 Q2 權重。它的 SHA-256 在移動前後都與已記錄的值一致，IQ3_S symlink 可正常解析。
- 實際釋放約 120,039,207,776 bytes，即 120.04 GB / 111.82 GiB（包括兩個 Q2 專用 pack）。`df` 可用空間從 43 GiB 增至 155 GiB；檔案系統以整數 GiB 顯示。
- Dense、Wan 2.2、ACE-Step、Flash IQ3_S 和 Flash Q4 未刪除。
