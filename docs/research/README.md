# RTX 3080 / Strata 實機研究與重現紀錄

主機：Ubuntu 24.04.5、RTX 3080 20 GiB、Xeon E5-2666 v3、125 GiB RAM；時間以 Asia/Taipei 為準。原始計畫見專案根目錄 `RTX3080_20GB_Strata_Qwen_Codex_PLAN_v2.md`。本目錄記錄實際操作，不將尚未通過的計畫視為結果。

- [執行日誌](execution.md)：命令、版本、檔案位置、結果與待辦。
- [自架 LLM 的 Agent Harness](local-agent-harnesses.md)：Codex、Hermes 及社群工作流的研究與本機建議。
- [中國象棋機器學習與 RTX 3080](xiangqi-ml-training-3080.md)：訓練方法、棋力基準、算力限制及可重現的研究階段。
- [Pikafish UCI 與架構](pikafish-uci-architecture.md)：指令、狀態管理、搜尋、模型與象棋教練整合。
- [Pikafish 現有應用](pikafish-applications.md)：iPad、網頁、教學、複盤與開源整合案例。
- [Hermes 與 Strata 內網部署](hermes-strata-20261118.md)：Qwen Flash、Hermes 與內網連線設定。
- [Pi Coding Agent 連接 Strata](pi-agent-strata-20261118.md)：Pi 安裝、Responses API 設定及工具呼叫實測。
- [MiniMax H3 lcz.me 3045 實驗報告](minimax-h3-3080-lcz3045.html)：RTX 3080 20 GiB 的 H3 雙風格影片挑戰、工作流與實測紀錄。
- [MiniMax H3 加速測試](minimax-h3-speed-canary-20261115.html)：論壇經驗及 RTX 3080 20 GiB 從短 canary 到 1344×768 全尺寸 Comfy Kitchen 對照。
- [H3 加速測試原始紀錄](minimax-h3-speed-canary-20261115.md)：測試設定、速度、SSIM、影片雜湊及重現方法。
- [LTX-2.5 RTX 3080 實測](ltx25-3080-experiment-20261116.md)：兩階段短片及 5 秒影片的冷啟動、快取時間和輸出。
- [H3 工作流與重現腳本](workflows/README.md)：官方 R2V 範本、3D／2D JSON、模型驗證及執行輔助腳本。
- 原始輸出位於 `logs/`；進度及故障紀錄分別為 `progress.md`、`lessons-learned.md`，在每次更新後同步至此目錄。

使用者已授權本次安裝使用 sudo；不得變更 GPU 驅動或中斷既有服務。所有 GPU 實驗固定 250 W。其他模型檔超過 10 GB 前先告知使用者，由使用者決定是否於學校下載。模型檔的相容性與雜湊必須自行檢查，不能只依檔名。
