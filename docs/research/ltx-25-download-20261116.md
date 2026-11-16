# LTX-2.5 模型下載紀錄（2026-11-16）

使用者授權現在下載 LTX，包括超過 10 GB 的檔案。計畫採用官方 Lightricks/LTX-2.5 distilled INT8 ConvRot、Gemma4 INT8 編碼器、BF16 video/audio VAE 和 2× 空間放大器，共約 39.71 GB。官方 revision `49b093a39c19169a8a81721dcc541e07e945232f`，完整檔案大小與 SHA-256 見 `logs/21-ltx25-download-manifest.json`。

官方主模型下載於 2026-11-16 05:15 CST 回傳 HTTP 401。官方 Hugging Face 模型頁屬 gated repository，本機無 HF token。未下載任何模型。公開鏡像 comfyicu/LTX-2.5 的四個檔案雜湊與官方一致，但同名文字編碼器雜湊與大小不一致，不能當作已驗證的完整官方組合。需要有權限的 Hugging Face 登入與授權後再從固定 revision 下載並驗證。官方頁：https://huggingface.co/Lightricks/LTX-2.5 。

已重用 ComfyUI venv 中的 huggingface_hub 2.4.0 CLI，建立 `~/.local/bin/hf` 指向該 venv 的 `bin/hf`，`hf --version` 顯示 2.4.0。使用者需自行在終端執行 `hf auth login` 並在官方模型頁接受條款；勿將 token 貼進對話。登入後使用 `hf auth whoami` 確認。

使用者登入後，`hf auth whoami` 成功；README 可取得，但對固定 revision 的主模型做認證存取檢查時，Hugging Face 回覆 HTTP 403，表示該帳號尚未列入授權名單。尚未開始下載大型檔案；需先在模型頁使用同一帳號申請存取並完成條款流程。

2026-11-16 05:42 CST：使用者完成授權後，官方主模型 metadata 檢查成功，大小 21,504,034,224 bytes。開始下載；Xet 連線後未觀察到寫入，05:44 改以 `HF_HUB_DISABLE_XET=1` 重新執行 `workflows/download_ltx25.py`，HTTP 傳輸已開始。腳本會依序下載 manifest 中五個檔案，逐一核對官方大小與 SHA-256；輸出見 `logs/22-ltx25-download.log`。下載中 `.incomplete` 是暫存檔，不代表驗證完成。

2026-11-16 13:15 CST：主模型 21.50 GB 與空間放大模型 1.00 GB 已完成且 SHA-256 驗證通過。Gemma4 文字編碼器已下載 4,435,476,480 / 15,372,969,374 bytes（約 28.9%），仍在傳輸；之後還需下載 video VAE 1.47 GB 與 audio VAE 0.36 GB。下載程序仍執行，磁碟可用 73 GiB，GPU 功率上限 250 W。尚未安裝或實測 LTX 工作流。

2026-11-16 19:09 CST 查核：五個檔案均已下載，日誌顯示最後 video VAE 於 16:25 完成且全部官方 SHA-256 通過（`ALL VERIFIED`）；下載程序已結束，磁碟可用 61 GiB。這是下載完成狀態，LTX 工作流尚未安裝或實測。
