# 後續下載預測（2026-11-14）

不自行下載大型模型；先提供使用者學校網路下載清單。全部大小以十進位 GB 計。用途與優先順序依 Gate 0–18，不能因檔案已下載就跳過前面 Gate。

1. 必要：ISTA-DASLab Qwen3.8-Flash-Next GSQ-RCO IQ2_XS，供 Strata 主測試；兩個分片合計 68.026 GB。固定版本、直接連結與 SHA256 見 `3080-guides.md`。
2. 建議預備：Unsloth Qwen3.8-27B UD-Q4_K_M，16.6 GB，供 Gate 9 的 llama.cpp Dense 實驗；現有目錄沒有 27B。它比 ggml-org Q4_K_M（19.4 GB）小，但仍必須以 4K smoke 確認實際 VRAM/KV，無法保證全 GPU 或長上下文成功。
   https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/4af51b3542f775b0a8e4b310bfb3f17e01c306c9/Qwen3.8-27B-UD-Q4_K_M.gguf
   SHA256: 1bce504dfecd84153666928a41d8a66706f0158d3a317bc5196b72819d7dc529
3. 選擇性：ggml-org Qwen3.8-27B Q4_K_M，19.4 GB，便於另一套官方 GGUF 比較，並非完成 Dense 測試的第二個必需檔。
   https://huggingface.co/ggml-org/Qwen3.8-27B-GGUF/resolve/c1869413dece09109e55b7dcc2c77ef382b0d0bd/Qwen3.8-27B-Q4_K_M.gguf
   SHA256: d15d4b6de55f662ac40e867702d31afe738d032fa06b829b2b1a21a49d4a48ee
4. Windows A/B 需同一模型檔，但不用再下載另一份；需兩 OS 可讀取的儲存位置。Windows llama.cpp CUDA 12 的 b12375 主程式及 DLL（對應現有 Linux b12375；兩平台 CUDA minor 有差異）可從官方 release 取得：
   https://github.com/ggml-org/llama.cpp/releases/download/b12375/llama-b12375-bin-win-cuda-12.4-x64.zip
   https://github.com/ggml-org/llama.cpp/releases/download/b12375/cudart-llama-bin-win-cuda-12.4-x64.zip
   套件大小及 Windows driver 相容性尚未在 Windows 核驗。
5. Windows Strata 需同一 release 的 Windows 版本及引擎；下載前先在 Windows 檢查既有安裝，並查官方 v0.2.13 release： https://github.com/Niko1221/Strata/releases/tag/v0.2.13 。Windows Terminal 與 Linux 在此 release 可能不同步，應核實後決定 App/Terminal；不能宣稱現已達成相同配置。
6. Codex profiles 不必額外下載模型；使用已啟動的 Flash-Next。DFlash/MTP、vision projector、其他量化為後續選項，不屬目前基準必需。

來源： https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/blob/main/Qwen3.8-27B-UD-Q4_K_M.gguf 、 https://huggingface.co/ggml-org/Qwen3.8-27B-GGUF/blob/main/Qwen3.8-27B-Q4_K_M.gguf 、 https://github.com/ggml-org/llama.cpp/releases/tag/b12375
