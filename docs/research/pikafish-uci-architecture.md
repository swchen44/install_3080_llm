# Pikafish UCI 與架構研究

研究日期：2026-11-16。依官方文件所對應的 commit `1c66b9b`；實際安裝版本的指令和選項以 `uci` 輸出為準。這是文件研究，尚未在本機安裝或實測 Pikafish。

## 元件與資料流

```text
iPad 瀏覽器／棋盤 UI
  ↕ HTTP / WebSocket（如需要遠端，須另有服務）
棋局服務：保存棋譜、規則、使用者和教學紀錄
  ↕ stdin / stdout，UCI 一行一條
Pikafish process
  ├─ UCI：解析指令、輸出 info / bestmove
  ├─ Position：棋盤、合法走法、歷史和象棋規則
  ├─ Search：alpha-beta 搜尋、剪枝、排序和 hash
  └─ NNUE：根據權重評估局面
```

Pikafish 是獨立可執行程式，stdin/stdout 是 UCI 通道。棋盤介面或服務啟動它；多使用者需求、保存與 HTTP API 均由外層處理。它常駐時保留目前局面與搜尋暫存；關閉後要由外部保存棋譜。NNUE 網路負責局面評估，搜尋負責比較後續走法；兩者共同產生最佳步。[官方架構](https://www.pikafish.com/wiki/en/reference/source-guide.html) [引擎運行](https://www.pikafish.com/wiki/en/reference/engine-runtime.html)

## UCI 一次完整對話

以下是官方例子：`>` 表示外部程式送出，`<` 表示引擎回應。回應是說明性示意，實際內容和計算結果因版本而異。

```text
> uci
< id name ...
< option name ...
< uciok
> setoption name Threads value 2
> isready
< readyok
> position startpos moves b0c2 b9c7
> go movetime 1000
< info depth ... score ... nodes ... pv ...
< bestmove ...
```

`uci` 啟動握手並列出支援選項；等待 `uciok`。`isready` / `readyok` 確認引擎回應。`position` 從初始棋局重放紅黑馬步；`go movetime 1000` 搜尋約一秒（毫秒為單位），`info` 可多次輸出，最終 `bestmove` 宣告本次搜尋結束。介面應更新棋譜、下一次重新送更新後的 `position`。棋譜格式 `b0c2` 是起點到終點，不是「炮二平五」之類中文記譜；需要用棋盤狀態轉換。[官方範例](https://www.pikafish.com/wiki/en/reference/uci-protocol.html)

## 狀態與流程控制

- `position startpos moves ...` 可提供開局以來的完整走法；也可用 `position fen ... moves ...` 從特定局面開始。每次 `position` 建立局面並重放提供的走法。只傳最後一張 FEN 無法恢復先前局面歷史，可能影響重複局面、長將和長捉判斷。
- `go depth N`、`go nodes N`、`go movetime N` 是不同搜尋限制。`go infinite` 須送 `stop`，並等待最終 `bestmove`；不要把 `readyok` 當搜尋完成訊號。`isready` 可在搜尋中得到回應。
- `ucinewgame` 清理搜尋歷史和置換表，並不自行把棋盤設回初始局面；新棋仍需送 `position`。`quit` 結束程序。
- 引擎的 UCI 通道是序列化狀態機：一個 process 同時只管理一個活動搜尋／局面。服務需序列化任務或給並行棋局配置獨立 process，不可交錯多個使用者的 `position` / `go`。
- 收集 stdout 同時持續讀取 stderr，避免 pipe 堵塞；處理程序退出、錯誤輸入、等待逾時與搜尋取消。官方記載部分版本遇到無效局面或非法走法會輸出 CRITICAL ERROR 並退出。記錄版本並驗證輸入。

## 輸出如何供教練使用

`info` 可能包含 `depth`、`score`、`nodes`、`nps`、`time`、`pv` 等：深度是搜尋迭代深度；`pv` 是引擎目前預測的主要變化；`bestmove` 是最終建議。分數格式和 `ScoreType` 會影響數值解讀，分數不是絕對勝率，也不是自然語言的理由；`lowerbound` / `upperbound` 表示界限，不能當精確分數。應存原始文字、分數型別與設定、局面、PV、版本與思考限制，並依實際版本確認視角。[UCI 設定](https://www.pikafish.com/wiki/en/reference/uci-options.html)

`MultiPV` 可提供多條候選變化供比較；官方說提高它會在固定資源下降低實戰強度，適合分析。外層應先根據合法走法重放 PV 並核對棋子和吃子，再將這些事實提供語言模型解釋。語言模型生成的因果解釋需要與變化一致，不能把引擎分數直接描述成確定事實。

## 常用設定與本案選擇

| 設定 | 功用 | 注意 |
|---|---|---|
| `Threads` | 搜尋使用的 CPU 執行緒 | 與同機其他工作共享 CPU，依本機狀況量測 |
| `Hash` | 搜尋暫存記憶體 | 每個引擎 process 使用記憶體；不等於永久棋譜 |
| `EvalFile` | NNUE 權重路徑 | 引擎和網路版本須相容 |
| `MultiPV` | 同時分析多個候選走法 | 比較候選有用；固定資源下可能減少最佳線搜尋 |
| `Skill Level` / `UCI_LimitStrength` / `UCI_Elo` | 減弱對手強度 | 隨版本列出的範圍與校準為準；引擎 Elo 不可直接等同人類或 iPad 平台等級 |
| `Repetition Rule`、`Sixty Move Rule` | 控制重複局面與和棋規則 | 需與對局 App 的實際規則比較；不同規則可能導致建議不同 |

## 應用設計與重現

初版可只用單一服務、單個本機引擎 process 和 SQLite 棋譜：保存起始 FEN、完整走法、紅黑和時間、規則、引擎與網路版本及 hash、引擎限制、分析原文和教練說明。提供建立對局、送入走法、取得分析、回放棋譜等介面；先採單一請求佇列。iPad 經 SSH tunnel 或受保護的網路連線訪問 UI。以上是架構方案，不代表已實作或驗證。

## 來源

- https://www.pikafish.com/wiki/en/reference/uci-protocol.html
- https://www.pikafish.com/wiki/en/reference/uci-options.html
- https://www.pikafish.com/wiki/en/reference/engine-runtime.html
- https://www.pikafish.com/wiki/en/reference/source-guide.html
- https://github.com/official-pikafish/Pikafish/blob/master/src/uci.cpp
