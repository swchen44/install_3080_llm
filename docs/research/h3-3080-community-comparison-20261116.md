# MiniMax H3 RTX 3080 社群時間比較（2026-11-16）

最接近本機題目的公開紀錄是 lcz.me 使用者 xbinb0：RTX 3080 20GB、六參考圖、1344×768、294 幀、20 步、不用 Turbo LoRA。其 3D ComfyUI 時間 2:09:10、2D 1:51:59，採樣分別 7,630 / 6,602 秒。來源：https://lcz.me/topic/3073/2 。

本機 3D 相同輸出尺寸、294 幀、六圖與 20 步，PyTorch attention 1:31:14，Kitchen attention 42:42；採樣分別 5,319 / 2,389 秒。與該篇 3D 的 ComfyUI 時間比較分別快約 29% / 67%，但不是嚴格 A/B：對方 320W、W6A8 DiT、NVFP4 文字編碼器、Euler/beta、sigma 12/3、將參考圖預先放大並使用 token 分片；本機 250W、INT8 ConvRot、res_multistep/simple、原參考圖與 Kitchen INT8 attention。對方自述分片使其速度降低並限制顯存。無法歸因各差異或直接認定畫質相同。

其他 3080 經驗：

- https://lcz.me/topic/1306/4 3080 20GB、FL2VA 768p 5s I2V：10 步 541–604 秒；4 步 Turbo + Sage 279.7 秒。10s 4 步 Turbo + Sage 757.8 秒。模式與步數不同，不可直接換算。
- https://www.reddit.com/r/comfyui/comments/1wjcz72/comfyui_just_made_minimax_ai_video_5x_faster_fast/ 一位 3080 / 64GB 用戶報告 10s、0.5MP、Turbo 8 步原 500 秒，改工作流後 350 秒；不是同解析度及步數。
- https://note.com/j2_games/n/n789c04da0a77?hl=en 3080 10GB / 64GB，作者報告 15s 約 7 分鐘，使用 4 步 Turbo、多階段、稀疏注意力及升頻；自述有品質取捨。

以上都是使用者或作者自述，沒有獨立重現。全尺寸 3D 結果僅一組 seed；參考圖處理、音訊及動作品質仍須另行比較。未下載模型或變更設定。
