# 無審查模型調查：Qwen3.8-Flash-Next（Strata/Q4）與 MiniMax H3

日期：2026-11-19（HF API 實搜 + 討論區證據；**尚未下載**）
目的：為 Windows 上的 Strata（LLM）與 ComfyUI（MiniMax H3 影片）尋找社群驗證的無審查版本。
術語：LLM 圈稱 `abliterated / uncensored / refusal-removed`；影片圈多標 `uncensored / NSFW / 微調合併`。

## 現況（500G USB `E:\downloads\ai\`）

- LLM：Qwen3.8-Flash-Next **UD-Q4_K_XL（有審查，104G，4 分片）**、GSQ-RCO IQ2_XS / IQ3_S、Qwen3.8-27B Q4_K_M
- 影片：Comfy-Org MiniMax H3（`minimax_h3_ref2va_pruned_int8_convrot` + `qwen3vl_32b_minimax_h3_int8_convrot` text encoder）
- USB 剩餘空間約 **92G**（抓無審查 Q4_K_XL 104G 會放不下 → 先刪 IQ2_XS 63G，或改選 IQ4_XS）

## 1. Qwen3.8-Flash-Next 無審查 Q4（Strata 用）

| 排名 | Repo | 人氣 / 實測證據 | Q4 檔案 |
|---|---|---|---|
| 🥇 | [huihui-ai/Huihui-Qwen3.8-Flash-Next-abliterated-v2-GGUF](https://huggingface.co/huihui-ai/Huihui-Qwen3.8-Flash-Next-abliterated-v2-GGUF) | 1.0M dl、274👍、2026-11-09 更新、tags 含 `Strata`、8 串討論（含 Unsloth v3.1 量化實測） | `unsloth-UD-Q4_K_XL-V2/`（4 分片）、`unsloth-UD-IQ4_XS/`（3 分片） |
| 🥈 | [orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF](https://huggingface.co/orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF) | 699K dl、**1539👍**、20 串討論；[網友實測文：IQ4_XS speed on 12GB+96GB + Strata 使用者備註](https://huggingface.co/orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF/discussions/20)（與本機「小顯卡+大 RAM」同規格） | `Q4_K_M`、`IQ4_XS`（各 3 分片）、MTP 版 |
| 🥉 | [SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF](https://huggingface.co/SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF) | 4.28M dl、1171👍；與本機 IQ2/IQ3（ISTA GSQ-RCO）同血統，144 tensors transplanted、per-tensor blake2b 驗證 | ⚠️ Q4 僅 `mtp-Q4_0` 單檔，主力 IQ2/IQ3/Q2 |
| ⚠️ 避開 | [alesha-pro/…-abliterated-GSQ-RCO-Strata-GGUF](https://huggingface.co/alesha-pro/Qwen3.8-Flash-Next-abliterated-GSQ-RCO-Strata-GGUF) | 10/30 負評串〈Not really abliterated〉 | IQ3/Q2 為主 |

**結論**：首選 **huihui-ai `unsloth-UD-Q4_K_XL-V2`** — 與現任 UD-Q4_K_XL 同分片結構，等於無審查直替版，Strata 載入方式與記憶體占用不變。省空間方案為 orcarouter `IQ4_XS`（有同規格 Strata 實測文）。

## 2. MiniMax H3 無審查（ComfyUI 影片）

| 排名 | Repo | 人氣 / 實測證據 | 備註 |
|---|---|---|---|
| 🥇 | [WarmBloodAban/Minimax-h3_Singularity](https://huggingface.co/WarmBloodAban/Minimax-h3_Singularity) | **1.27M dl、1001👍、46 串討論**、附範例影片＋提示詞規格書 | `ref2va_pruned_int8`（v1.3/v2）與現有空檔**同名直替**；text encoder/VAE 沿用現有 |
| 🥈 | [OliviaRossi/Minimax-h3_Singularity-x-10Eros-Max_PRISM](https://huggingface.co/OliviaRossi/Minimax-h3_Singularity-x-10Eros-Max_PRISM) | 545K dl、359👍（更激進的二次合併） | 無討論區，風險自負 |
| 🔄 省空間路線 | [linjian257/qwen3vl_32b_minimax_h3_int8_convrot_uncensored](https://huggingface.co/linjian257/qwen3vl_32b_minimax_h3_int8_convrot_uncensored-by-linjian257) | 62👍；1 串报错討論（2026-08） | **只換 text encoder**（26G），底模不動；審查多卡在 text encoder |

### 討論區情報摘要（Singularity 46 串）
- v1.3 int8 較穩；**v2 有「動作太快、畫面偏暗」回報**（2026-10/11）。
- v2 建議搭配 latent upscaler：[LBH-123-AI/Minimax_h3_latent_Upscaler](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler)（505👍）。
- Civitai 需登入才能搜 H3 相關資源，本調查未納入。

## 下載計畫（待執行）

1. LLM：`huihui-ai` UD-Q4_K_XL-V2（~104G，**需先清 500G 空間**：刪 GSQ-RCO IQ2_XS 63G 或改抓 IQ4_XS ~60G）→ 放 `Qwen3.8-Flash-Next/huihui-abliterated-Q4_K_XL/`
2. 影片：`WarmBloodAban` **v1.3 pruned int8**（先不用 v2）→ 覆寫/並存於 `ComfyUI/models/diffusion_models/`（保留原版檔名以便回退）
3. 可選：linjian257 無審查 text encoder 路線（26G，最省）
4. 落地後照例逐檔 byte 核對；社群版無官方 SHA256，以 ComfyUI / Strata 實際 load 驗證

## 通用注意事項
- 社群量化版無官方校驗碼，先查討論區有無 load 失敗回報再下載。
- abliterated 版常附改過的 chat template；輸出異常時換回官方 template。
- 分片 GGUF（`-of-`）要整組同目錄，載入選 `00001` 那檔。
