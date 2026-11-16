# Pikafish 現有應用調查

查閱日期：2026-11-16。以下功能、平台和費用為產品頁或開發者自述，尚未實際安裝或測試；App Store 地區、版本和費用可能不同。

| 應用 | 平台及執行方式 | 用途與限制 |
|---|---|---|
| [Pikafish 官方網頁版](https://xiangqiai.com/) | iPad Safari / 瀏覽器，首次載入下載引擎並在裝置運算 | 人機對弈、助手提示、棋局分析、照片／文字輸入、複盤及匯出。[官方使用手冊](https://www.pikafish.com/wiki/en/guide/web-version.html)稱助手模式可給建議、可悔棋，網頁版使用較小引擎。圖片辨識結果要人工核對。 |
| [Pikafish iPad App](https://apps.apple.com/us/app/pikafish-xiangqi-ai-review/id6816128870) | App Store 頁面列 iPhone/iPad，計算在裝置本機；支援繁中 | 描述列出照片識棋、候選走法、複盤、練習和保存棋譜；基本分析無須登入。官方[下載指南](https://www.pikafish.com/wiki/en/guide/download.html)仍寫 iOS 即將推出，與 App Store 頁面不一致，應以使用者所在地 App Store 可用性為準。 |
| [Xiangqi One](https://xiangqi.one/) | 網頁、iOS、Android；分析引擎在使用者裝置 | 初學課程、AI 對手、題目及 Pikafish 棋局分析；[分析頁](https://xiangqi.one/analysis)稱首次約下載 50MB，完整棋局 review 在伺服器並需要免費帳號。 |
| [Xiangqiful](https://apps.apple.com/app/id6794340136) | iPhone/iPad/Mac，App Store 描述稱離線本機運行 | 初學課程、對手、提示、錯誤轉練習題，Pikafish 做局後分析並提供簡短說明；免費下載、部分功能有內購，介面語言及地區費用實際查看商店。 |
| [Sachess](https://sachess.com/) | 網頁 PWA；[官方說明](https://sachess.com/xiangqi-help/)稱 Pikafish 分析在瀏覽器 | 圖片轉棋局、變化、棋譜輸入、全局錯誤標記、題目與分享；各功能是否上傳及登入要求依功能頁面為準。 |
| [Web Xiangqi](https://teozeng.dev/web-xiangqi/) | JavaScript 瀏覽器介面；頁面說明棋盤、Pikafish、研究資料在瀏覽器運作 | 支援 beginner、棋譜和研究庫；未確認自架代碼及繁中解說。 |
| [ChineseChess-with-deepseek](https://github.com/WildWriter/ChineseChess-with-deepseek) | GitHub 專案，README 要求 Windows x64 / Node.js | 作者列出 Pikafish 對弈、棋譜、圖片、DeepSeek 戰術分析；有程式碼但本次未審核執行、雲端費用、穩定性或 Linux headless 支援。其權重授權與程式授權分別核對。 |
| [Pikafish WASM](https://github.com/brianhliou/pikafish-wasm) | 開發用 GitHub 專案，在瀏覽器 WebAssembly 執行引擎 | 適合研究如何自製棋盤與本地分析；不是現成的中文教練，程式與網路權重授權不同。 |

建議先用官方網頁版的「With Assistant」，或在 iPad 試官方 App；想系統學基礎，可比較 Xiangqi One 與 Xiangqiful。上述功能以產品聲明為準，尚不能保證能自動讀取另一個 iPad App 畫面或提供可靠的繁體中文自然語言解說。大多數方案在 iPad 自己運算，並不會自動使用家中 Linux；若要求遠端使用家中 CPU 與本地 LLM，需再調查現成方案或整合。

## 截圖教練構想（使用者需求）

使用者希望將象棋遊戲畫面截圖後，由教練辨識棋盤並提供兩種模式：一、先問使用者想走哪一步，分析優點、風險與對手應對；二、直接推薦一步並解釋原因和可能的後續變化。教練應顯示辨識結果，讓使用者確認或修正棋子、紅黑方位及輪到誰走，再把已確認局面交給 Pikafish；圖片不能恢復歷史，長將長捉須註明缺乏棋譜。引擎建議與候選變化由程式驗證後交給語言模型解說，避免臆造走法。

現有官方 [Pikafish 網頁](https://xiangqiai.com/)支援匯入圖片並手動校正，[官方說明](https://www.pikafish.com/wiki/en/guide/xiangqi-ai.html)指出圖片只有當前局面，沒有之前走法。另有 [rakuxq](https://github.com/rakulgt/rakuxq) 自述提供本地 ONNX 圖片轉 FEN HTTP API，以及 [xiangqi-vision-assistant](https://github.com/tzq-debug/xiangqi-vision-assistant) 自述可辨識手機棋盤並調用 Pikafish；後者的手機抓屏方式針對其特定設備，不能假定支援 iPad。兩者尚未測試，也未確認權重、授權與下載量。

本次僅完成來源研究與需求整理。搜尋 `~/Downloads/ai` 檔名未發現象棋相關項目；未安裝、下載或實測。後續可先以官方網頁圖片匯入做手動體驗，之後再評估 CLI / MCP 接入和自主搭建。

2026-11-16：使用者提出以既有 Qwen 視覺模型辨識象棋截圖。Strata 官方文件記載 Qwen Flash 可選擇啟用圖像輸入，但先前本機啟動皆為 `--vision off`，未驗證圖像能力；本次 `rg --files ~/Downloads/ai` 依 mmproj 或 vision GGUF 檔名搜尋沒有結果，其他路徑或不同檔名尚未排除。官方資料描述此系列 picture-reader 約 0.9GB（以實際版本與下載前 plan 為準）：https://github.com/Niko1221/Strata/blob/main/docs/DOCKER.md 。截圖取得須由瀏覽器或使用者提供，Qwen 負責讀圖；模型輸出棋盤後仍要檢查座標、棋子、輪次並讓使用者修正。未測量棋盤識別準確度，不能視為已可靠運作。本次未下載、修改或重啟服務。

## 網頁遊戲作教練研究目標（2026-11-16）

1. [Xiangqi One 人機對弈](https://xiangqi.one/bots)：網站介紹有初學者電腦對手、瀏覽器保存訪客棋局；第一次遊戲可能下載約 50MB 引擎。另有[分析棋盤](https://xiangqi.one/analysis)支援棋譜匯入匯出。頁面功能為網站自述，尚未互動測試；網站可能更新。
2. [Pikafish 網頁版](https://xiangqiai.com/)：官方[手冊](https://www.pikafish.com/wiki/en/guide/web-version.html)列 Play vs AI、With Assistant、級別、截圖匯入、棋譜輸出，適合先體驗教練，但對手與分析採相關引擎，獨立比較可另選其他遊戲。
3. [cv.cm 象棋](https://cv.cm/en/chinese-chess/)：作者說明瀏覽器可對電腦，有 Beginner 至 Expert 四級；尚未測試棋譜輸出、圖像可辨識度或手機版。

優先用瀏覽器而非 Android 模擬器：用 iPad 上瀏覽器對電腦下棋並自行截圖，或在可視桌面執行網頁；若要 Linux headless 以瀏覽器自動化截圖，需要獨立瀏覽器進程和連接方式，iPad 上自行操作的獨立瀏覽器不會自動被主機截到。先針對自行對電腦遊戲研究；實際截圖和控制的能力需要選定網站後實測。若網站可直接匯出棋譜/FEN，可對照影像辨識結果；單張 FEN 不包含完整歷史。此回合只查資料、寫報告，沒有啟動遊戲、下載模型或安裝模擬器。
