# Windows / Linux：本機 AI 影片與剪輯研究

查閱日期：2026-11-15。此為建議與來源整理，非此主機的 Windows/Linux A/B 實測。

## 本機現況

Ubuntu 24.04、RTX 3080 20GB、128GB DDR3，平時 SSH 遠端操作。`~/Downloads/ai/` 中已有：

- `models/comfyui/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors`
- `models/comfyui/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors`
- `models/comfyui/vae/wan2.2_vae.safetensors`
- `tools/source/ComfyUI-102350eb949bca599e450a904f0562ad3f551279.tar.gz`
- Windows portable ComfyUI 及 Linux LTX Desktop `.deb`。

以上 3 個模型檔名稱與 [ComfyUI 官方 Wan 2.2 5B 指南](https://docs.comfy.org/tutorials/video/wan/wan2_2)對應。清單記錄下載時的 hash；本次未重新計算，也尚未驗證 workflow、套件或生成。Linux ComfyUI/PyTorch 離線環境在既有 FILE_LIST 中明確標註不完整；不得認為已有原始碼即能離線啟動。LTX Desktop 安裝檔不是 LTX 權重，不要默認 Wan 檔可供 LTX Desktop 使用。

## 架構

Linux 主機執行 Python ComfyUI server 和 GPU；SSH client 使用 local port forwarding 把本地 8188 轉到遠端 127.0.0.1:8188，在 client 本地瀏覽器打開 http://127.0.0.1:8188。Linux 無需桌面、遠端桌面或在 client 安裝 ComfyUI。伺服器必須有執行環境、模型與本地前端資源；SSH 連線斷線時會中斷 tunnel，server 是否持續取決於啟動方式。此主機單卡：先確認 Strata 無人使用且可停止，再啟用 video，不自行終止使用中的服務。

命令示例在 client 執行，需替換 SSH 主機：

```
ssh -L 8188:127.0.0.1:8188 swchen@LINUX_HOST
```

ComfyUI 預設僅 localhost，SSH tunnel 避免直接將服務公開；[ComfyUI 安全政策](https://github.com/Comfy-Org/ComfyUI/security)指出對外開放需自行考量認證與網路保護。桌面剪輯程式若在 Linux 運行通常需 GUI，才考慮 remote desktop；亦可在 Windows client 本機剪輯並以 SSH/SFTP 取回成品。

## 來源與觀察

- 官方 [ComfyUI Linux 安裝文件](https://docs.comfy.org/installation/manual_install) 及 [Wan 2.2 5B 指南](https://docs.comfy.org/tutorials/video/wan/wan2_2)：5B 支援文字與圖片轉影片。8GB + offload 是文件所述，不能保證本機任何解析度/長度可跑。
- [Linux vs Windows 使用者經驗](https://www.reddit.com/r/comfyui/comments/1vmhr0g/comfyui_is_better_with_linux/) 有人報 Linux 桌面佔用顯存較少；另一個 [GTX 1070 個案](https://www.reddit.com/r/comfyui/comments/1ipu3ks/comfyui_running_significantly_slower_on_linux/) 發現 Linux 慢於 Windows。硬體/版本不同，皆非此機量測；不能斷言本機固定加速比例。
- [Linux 影片剪輯經驗](https://www.reddit.com/r/linuxquestions/comments/1kcaorz) 有使用者指出商用軟體和編碼相容問題。Blackmagic 的 [Resolve 19.1 codec 表](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_19_1_Supported_Codec_List.pdf?_v=1731484810000) 在 Linux 表格對 H.264/H.265 列 Studio 限制；新版本應重新核對，且不應推廣成 Linux 所有剪輯軟體均不能處理。
- [Kdenlive 官方](https://kdenlive.org/) 是跨平台非線性剪輯替代方案。常用 Windows 商業剪輯工具仍以該工具實際支援系統與 codec 為準。

## 建議

先保留雙開機：Linux 做現有 Strata 與 headless AI 生成，影片剪輯可在 Windows GUI 完成。若 Windows 是同一台雙開機主機，不能 Windows 開著時同時使用同機 Ubuntu 服務；需重啟切換，或者從另一台電腦遠端操作啟動中的 Ubuntu。先核實 Linux 依賴、磁碟空間（先前約 48GiB）、CUDA/PyTorch、現有服務，離線重用模型並以短片低解析度 smoke test 驗證。需要下載的內容、版本與大小先呈現；其他超過 10GB 模型先告知用戶。無量測前不修改或覆蓋既有 AI 環境。

## 使用者需求與決策優先順序（2026-11-15）

- 約 90% 的使用時間是大語言模型；偶爾才做文字轉影片或影片剪輯。
- 使用者可以接受少量的 Ubuntu／Windows 雙開機切換，也願意等待重開機，不需要同時執行兩個系統。
- **優先考慮大語言模型的回答與程式任務品質**，其次考慮推論速度、遠端操作便利性與偶爾使用的影片工作流程。模型品質主要受模型、量化、推論設定及任務影響，不能在尚未做同條件測試前，把作業系統本身當作品質高低的證據。
- 因切換頻率低，保留 Ubuntu 作主要的遠端 LLM 環境、必要時切到 Windows 處理偏好在 Windows 操作的剪輯工作，是目前較符合需求的初步方案；Linux 端仍可按需要評估 headless 文字轉影片。
- 目前僅有 Ubuntu 上 IQ2_XS 4K smoke 通過，沒有完成 IQ3_S 品質評測，也沒有 Windows 對照成績；未來應先以一致任務比較 IQ2_XS、IQ3_S 和可用的現有量化，再依實際品質與速度決定日常選型。
