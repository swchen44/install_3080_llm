# 中國象棋機器學習與 RTX 3080 訓練可行性

研究日期：2026-11-16。目標硬體：RTX 3080 改裝 20GB、128GB RAM、Xeon E5-2666 v3（依本專案既有盤點）。本文件是文獻與工程可行性研究；沒有在主機安裝象棋程式、下載棋譜或執行訓練。

## 先講結論

### Pikafish 提供的模型和程式（2026-11-16）

Pikafish 的程式介面是 UCI 協定：客戶端啟動引擎，經 stdin/stdout 送 `position`、`go` 等文字指令，讀取 `info` 和 `bestmove`。目前查閱的官方文件描述本機 UCI，未找到官方提供的公共 HTTP API；若需要 HTTP，需使用現有封裝或自行建立 API wrapper。保留完整走棋歷史，單一 FEN 不能恢復長將、長捉與重複局面的歷史。來源：[引擎運行和通訊](https://www.pikafish.com/wiki/en/reference/engine-runtime.html)。本次沒有架設服務。

Pikafish 公開引擎原始碼，以及 NNUE 局面評估網路權重 `pikafish.nnue`；引擎結合 CPU 搜尋與網路評估來選步。官方 [Networks](https://github.com/official-pikafish/Networks) 存放網路，[引擎 releases](https://github.com/official-pikafish/Pikafish/releases) 提供版本套件，[UCI 設定](https://www.pikafish.com/wiki/en/reference/uci-options.html)解釋運行選項。權重與引擎架構需要匹配；官方維護者說 master-net 會更新，舊引擎應使用其配套網路：[issue 130](https://github.com/official-pikafish/Pikafish/issues/130)。這些權重不是可直接放進 Qwen 的 GGUF。可作為現成引擎、訓練資料 teacher 或研究起點；不保證可直接接一般 PyTorch 訓練流程。引擎源碼 GPL，官方 NNUE 權重有獨立限制：非經許可不得商用，衍生權重也在其約束內，詳見 [NNUE license](https://github.com/official-pikafish/Networks/blob/master/README.md)。本次僅查資料，未下載或訓練。

### 2026-11-16 使用者澄清：個人象棋教練

實際目標是學會打贏自己 iPad 上的象棋程式，並獲得可理解的走法解說；也希望親自用 3080 訓練模型。尚不知道 iPad App 名稱及難度，所以無法估算要達到的棋力。兩週是可以安排的實驗預算，並非保證能打贏該 App 的時間。

建議兩條並行研究：先用已訓練的 [Pikafish](https://github.com/official-pikafish/Pikafish) 計算候選走法、變化和局面，搭配現有本機語言模型解說；逐步用合法走法檢查及引擎變化驗證解說，避免憑空捏造。每一步可先手動把 iPad 的棋局記錄或局面輸入，對局結束後複盤，先確認 App 的棋力與介面。象棋教練研究本身也指出辨識錯著、產生原因需要資料和專家評估：[JAIST 研究](https://dspace.jaist.ac.jp/dspace/bitstream/10119/19417/4/paper.pdf)。

有意親手訓練時，先比較 [CC-Lite](https://github.com/hskl18/cc-lite) 的監督學習 + MCTS/self-play、[PPO self-play 象棋專案](https://github.com/Chow-JIN/xiangqi_project) 及 Pikafish teacher 蒸餾。先用可合法使用的棋譜或引擎產生標籤，訓練小型 policy/value，加入搜尋，再以固定開局、紅黑交換與 iPad 指定難度或引擎 baseline 對弈。記錄 GPU 時數、成功續跑、勝和負與解說事實正確性；一兩週能否達標要以 pilot 和對戰結果決定。Pikafish 可用作不需自行訓練的棋力對照；其 CPU 搜尋與 3080 的神經網路訓練是不同工作。

另有 [Xiangqi-R1](https://github.com/MINE-USTC/Xiangqi-R1)，研究以棋局、專家標註及引擎評估訓練 7B 語言模型；[論文](https://arxiv.org/abs/2507.12215)記載約五百萬局面與走法配對，但目前未核實在本機 20GB VRAM 的訓練資源與權重下載規模，不能聲稱可在兩週內重現或直接下載。

用這張 3080 訓練一個會下中國象棋的神經網路，完全可行。監督式學習可以從棋譜開始；再加入強化學習、自我對弈和搜尋，讓模型反覆改進。模型不是單獨的「棋手」：實用引擎還要有合法走法、局面表示、搜尋、局面評估和對局測試。

「世界前十」目前無法給可信的訓練時間。必須先釐清是人類選手排名、某個線上平台，還是象棋引擎排名；三種排名的對手池和評分都不同。若指世界頂尖引擎，已存在非常強的 Pikafish；其官方網站稱之為最強象棋 AI，並公開版本間配對測試。新模型需要在同規則、同時間控制及足夠多配對棋局中擊敗它，才有可比較的證據。[Pikafish 官方網站](https://www.pikafish.com/) [引擎測試資料與方法說明](https://www.pikafish.com/wiki/en/faq/)

文獻確實顯示象棋的深度學習可以很強。2024 年研究報告使用「棋譜監督學習 + 強化學習」，並稱其 RL-ViT 在該研究的人類線上天梯達前 0.1%。但這不是「世界前十」的證據；論文摘要與可檢索方法內容未給足 GPU 型號、完整訓練時數、天梯母體和可獨立重現的資料，不能直接推算到本機 3080。[研究論文](https://arxiv.org/abs/2410.04865)

## 訓練方法

| 方法 | 做法 | 適合的第一階段目標 | 主要限制 |
|---|---|---|---|
| 監督式學習（SL） | 用人類棋譜訓練模型預測下一步或局面勝率 | 快速得到可走棋、會模仿棋譜的 baseline | 模仿棋譜不等於棋力；資料來源、規則與強度會影響模型 |
| 引擎蒸餾 | 用 Pikafish 等引擎為大量局面提供建議步、評分或搜尋分佈，再訓練小網路 | 借用強引擎知識，做出適合 GPU 推論的神經網路 | 學生模型不會自然超越 teacher；製作標籤要跑大量引擎搜尋 |
| 自我對弈強化學習（RL） | 網路搭配 MCTS 搜尋產生對局和訓練目標，週期性用新舊模型互相驗證 | 研究自我改進、建立自己的策略 | 對局產生、搜尋、資料品質和評估比單純反向傳播更耗時，易出現策略循環或遺忘 |
| 混合流程 | 先用棋譜／引擎標籤 warm start，再和多種舊模型或引擎對弈，持續評估新 checkpoint | 本機最值得試的研究路線 | 工程複雜度較高；需保存資料來源、版本、seed 和配對結果 |

2024 象棋研究報告指出，加入雙方合法走法作特徵可加快早期學習；作者的 opponent pool 比純粹只和最新模型自我對弈有更好的實驗結果。這些結果值得當設計參考，但缺少本機可直接複製的完整硬體成本與訓練量。[論文方法與消融結果](https://arxiv.org/abs/2410.04865)

## 3080 時間估算能說到哪裡

目前沒有找到同一個 Xiangqi 訓練方案在 RTX 3080 20GB 上、以可查驗資料報告從零到指定棋力的訓練時數。因此不把下列內容偽裝成 benchmark：

- **程式與小型 smoke run：** 幾分鐘到數小時可用來檢查規則、網路前向、一次自我對弈、訓練和評分流程；只證明管線可執行，棋力沒有保證。
- **棋譜監督 baseline：** 在取得可合法使用且已解析的棋譜後，初次小型訓練通常應以數小時級 GPU 試跑作預算起點；完整資料、多組模型和調參會拉長到數天。這是工程預算範圍，不是論文保證或 3080 實測，應先用固定資料切分測 tokens／positions per second 再重算。
- **自我對弈 RL：** 先做至少 24–72 小時的受控 pilot，記錄每小時完整對局數、有效位置數、GPU 占用、每步搜尋量和 checkpoint 對手成績。pilot 之後才能按明確資料量估算數週或更久的運行量。增加 RAM 不會消除搜尋和大量推論的運算成本。
- **世界前十級：** 無法由目前證據推估時數或承諾可達。AlphaZero 在西洋棋的著名數小時結果，使用 5,000 顆第一代 TPU 產生自我對弈資料、64 顆第二代 TPU 訓練網路；總計 700,000 個訓練 batch、4,096 筆一批及 4,400 萬局棋，約 9 小時。這是另一種遊戲、專用大規模硬體，不能用來線性換算成單張 3080；但足以說明「幾小時達超強」隱藏了巨量並行運算。[AlphaZero 論文與補充資料](https://arxiv.org/abs/1712.01815)

本機 128GB RAM 主要幫助保存 replay buffer、較大的資料集及 CPU/GPU offload；不會把單張 GPU 的訓練量變成多張 GPU。現有 Xeon E5-2666 v3 在 CPU 自我對弈、棋規執行和 Pikafish 搜尋時也可能成為瓶頸。Pikafish 使用 CPU NNUE；其官方知識頁特別說明顯卡不會加速 Pikafish 本身。[Pikafish：GPU 對象棋引擎是否有用](https://www.pikafish.com/wiki/en/faq/)

## 別人的 GPU 實作經驗

| 案例 | GPU / 方法 | 公開經驗 | 證據界線 |
|---|---|---|---|
| [icyChessZero 作者實作日誌](https://fast.v2ex.com/t/479672) + [repo 說明](https://github.com/bupticybee/icyChessZero) | AlphaZero 式 policy/value + MCTS；使用 4–5 台 GPU server 做分散式 self-play | 作者曾報告約 700 的早期 Elo、自評 4–5 台機器仍算力緊張，目標是中上人類水平，對所需工期估過半年到一年。repo 記載單張 1080 Ti 可開多個 GPU worker，但警告 worker 數也受 CPU 核心限制。作者還測試 policy 網路加 MCTS 對純 policy 網路，29 局中 MCTS 沒輸、5 局因步數上限和棋。 | 2018 年個人開發紀錄，不是當代 3080 benchmark；Elo 和對局樣本很有限，半年到一年是當時多機集群的個人預估，不是已達成的成績。repo 使用 TensorFlow 1.4 時代的老依賴。 |
| [CC-Lite](https://github.com/hskl18/cc-lite) | PyTorch 小型殘差網路；GPU preset 是 200 simulations、batch 64，內含 self-play、訓練與配對評估 | 專案明確以單台消費級電腦／單張 RTX 級 GPU 為目標，作者說網路和 replay memory 用量不大，建議先從小設定跑穩。 | 這是可複現的研究 baseline，不是經驗上已達某個 Elo 的強引擎；repo 沒有 3080 的吞吐或棋力成績。 |
| [AlphaBing](https://github.com/Simuschlatz/AlphaBing) | 精簡 AlphaZero 概念，結合傳統 alpha-beta search 和 RL/MCTS | 作者的目標是讓象棋學習能在較有限的單機硬體上運行，並提供 pipeline 和評估入口。混合傳統搜尋是值得比較的省算力方向。 | README 沒公布可對照的 GPU 型號、self-play 速度或可靠 Elo。 |
| [Px0 / PikaXiangqiZero](https://github.com/official-pikafish/px0) | GPU 神經網路引擎、GPU/CPU backend、自我對弈 | 官方 repo 感謝 Google TPU Research Cloud 資源支援訓練與開發。這是成熟的分散訓練路線參考。 | 不代表普通一張 GPU 可取得相同訓練量；官方並未提供單張 RTX 3080 達標時間。 |
| [PyTorch SL + PPO Xiangqi 專案](https://github.com/Chow-JIN/xiangqi_project) | 棋譜轉 shard、監督 policy/value，再 PPO self-play，最後模型互打 | 可參考其完整管線和資料分片方式。repo 的示例模型對打只有 10 局。 | 10 局示例不足以支持高棋力或 Elo 主張；未見硬體和訓練時長基準。 |
| [象棋 AI 設計提案](https://github.com/oashasu/chinese-chess/blob/main/docs/2026-08-21-xiangqi-alphazero-upgrade-design.md) | 設計先 Pikafish 蒸餾，再 AlphaZero self-play；提案估單張 3060 監督訓練 2–4 小時，4 GPU self-play 1–2 週 | 這種拆段方式適合作規劃參考。 | 這是設計文件的估時，不是已完成 benchmark 或實驗結果；不能用作 3080 實測。 |

### 從 GPU 經驗得出的實用技巧

1. **分開走棋工作和訓練工作。** GPU 適合批次跑網路前向與梯度更新；合法走法、MCTS 樹管理、Pikafish teacher 搜尋常會吃 CPU。IcyChessZero 作者將 GPU worker 開太多視為問題，建議也不能超過實體 CPU 核心可支援的範圍。這對本機 E5-2666 v3 尤其 relevant。
2. **讓多盤棋的神經網路前向合併成 batch。** MCTS 每個搜尋節點都要請 policy/value 網路評估局面。若每次只有一個位置，GPU 可能吃不飽；多個 self-play actor 把局面湊成 batch 後再推論，常比單一 actor 不斷送小 batch 更能利用 GPU。這是作者實作建議，不保證本機最佳 actor 數；應逐級量測。
3. **採用緊湊網路和小搜尋先驗證。** CC-Lite 的 small preset 使用數個 ResNet blocks、64–96 channels，測試設定從 batch 64 和 200 simulations 起；這足以先驗證 pipeline，不代表接近 Pikafish。
4. **先用棋譜或 teacher warm start。** 純 policy 模型的著法看似像樣，實戰中局可能送子；IcyChessZero 作者觀察到 MCTS 能補強單純 policy 網路的局面前瞻。可用 Pikafish 評分或搜尋策略協助起步，再比較純模仿、teacher distillation、RL self-play。
5. **避免把 GUI 和顯存大小當主要吞吐指標。** 20GB VRAM 足以容納許多小型棋盤網路；真正未知量通常是每秒可完成多少 CPU 搜尋節點、網路批次推論位置和完整對局。128GB RAM 可放 replay data，不會替代 GPU/CPU self-play 運算。

### 對這台 3080 的直接判斷

截至研究日，沒有找到可核實的「一張 RTX 3080 訓練 Xiangqi 到指定 Elo / 世界前十」公開實驗。最接近的真實象棋 GPU 經驗是舊版 icyChessZero 多機集群、單卡消費級研究框架 CC-Lite（但沒有公布棋力成績），以及數個沒有嚴謹 rating/算力記錄的 GitHub 實驗。因此，原先提到的 24–72 小時應定位為**我們規劃中的性能 pilot 時間**，用來量測吞吐及穩定度；不是文獻證明能在該時間提升到何種棋力。

如果要用本機開始，優先選 CC-Lite 這類單卡小型 baseline 做最小 smoke，然後測「單 actor / 多 actor、batch 大小、MCTS simulations」對完整 games/hour 和 GPU 利用率的影響。再決定是否加上監督資料、teacher 或更長 RL。只調高 MCTS 模擬次數會增加計算量；不保證棋力按比例上升。GPU 實驗遵守主計畫固定 250W 上限，每一段保存版本、設定和原始結果。

## 對照引擎與可重現評估

- **Pikafish：** 頂級實用基線。建議作分析／teacher／對戰對手；它不是以 3080 GPU 跑神經網路推論的 AlphaZero 架構。
- **Px0 / PikaXiangqiZero：** UCI 神經網路象棋引擎，基於 Leela Chess Zero，使用 GPU backend 並支援 self-play。官方 README 說明訓練和發展獲得 Google TPU Research Cloud 資源，故其成果也不應假定只靠單張消費級 GPU 得到。[官方 Px0 repo](https://github.com/official-pikafish/px0)
- **CC-Lite：** 一個消費級 GPU 取向的 PyTorch Xiangqi AlphaZero 研究工作台，有棋規、MCTS、自我對弈、監督訓練、可選 engine distillation 和 paired-match evaluation。作者明確稱它是研究 baseline，並不宣稱強引擎；適合作為第一個可重現的程式候選，仍需先查清 license、資料授權與本機依賴。[CC-Lite repo](https://github.com/hskl18/cc-lite)

比較必須固定引擎版本、硬體、搜尋時間或節點、規則、先後手與開局；每個開局互換紅黑，使用大量配對棋局並報告勝和負和不確定區間。頂級引擎大量和棋，因此少數幾盤或「看起來走得不錯」不足以宣稱 Elo 或 top-N。[Pikafish 測試方法](https://www.pikafish.com/wiki/en/faq/)

## 建議的研究階段

1. **先定義榜單：** 選擇「打敗某一版本 Pikafish 的一人一局時間控制」或某個有明確規則與母體的真人天梯 percentile；不要混用人類和引擎 Elo。
2. **只讀盤點與來源檢查：** 查看本機是否已有象棋程式、資料、依賴和磁碟空間。所有新棋譜先檢查來源、授權、格式、去重及評估集污染；不要先下載模型或大檔。棋譜比通用 LLM 權重小得多，但一樣應記錄授權與雜湊。
3. **選一個可重現 baseline：** 先評估 CC-Lite 的安裝依賴和 license；以小型 debug preset 驗證棋規、棋局 replay、訓練和配對評估。或先使用已存在的 engine 做 teacher/baseline，不必先重造棋規引擎。
4. **建立監督 baseline：** 棋譜訓練 policy/value 網路，保留 train/validation/test 的棋局分隔，先測政策準確度與對隨機／簡單引擎成績。
5. **再做蒸餾或 RL：** 先試小批引擎標籤和受限 self-play，混合舊 checkpoint/opponent pool，只有在配對賽確實改善時才升級模型。
6. **逐段量吞吐：** 記錄資料解析 positions/s、GPU train positions/s、self-play games/hour、engine nodes/s 和兩側瓶頸。用這些本機量測估算擴大訓練成本。
7. **設定務實里程碑：** 先超過隨機、材料型 baseline，再挑戰指定引擎版本或真人天梯 percentile。世界前十列為長期探索題目，不列為單卡工期承諾。

## 來源

- [Mastering Chinese Chess AI (Xiangqi) Without Search, arXiv 2410.04865](https://arxiv.org/abs/2410.04865)
- [Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm, arXiv 1712.01815](https://arxiv.org/abs/1712.01815)
- [Pikafish official site](https://www.pikafish.com/)
- [Pikafish FAQ: testing, NNUE, GPU and engine strength](https://www.pikafish.com/wiki/en/faq/)
- [Px0 official repository](https://github.com/official-pikafish/px0)
- [CC-Lite Xiangqi research workbench](https://github.com/hskl18/cc-lite)
