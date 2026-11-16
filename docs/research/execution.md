# 實機執行日誌

## 2026-11-14：Gate 0–3

工作目錄 `/home/swchen/git/install_3080_llm`。實際離線資料位於 `/home/swchen/Downloads/ai`；原指示的 `~/Download/ai` 不存在。清單 `~/Downloads/ai/FILE_LIST.md` 記載來源與歷史雜湊。系統可用 122 GiB RAM、8 GiB swap、184 GiB 磁碟；GPU 桌面占 185 MiB，driver 595.99.02，沒有看到 NVIDIA Xid（詳見原始 kernel log）。

Strata 原先未在 PATH 中，亦未見其現有服務。使用離線 Terminal 封存 `strata-control-0.1.59-linux-x86_64.tar.gz`，SHA256 `14a9fde3dbde5a16cd1a0d34fe04b3dca38c462114a534f8813a00fcabfc4f5d`，解至 `local/strata-control/`，顯示 Strata 0.2.13 build 0.1.59。CUDA 12 Engine 封存 SHA256 `4bf321cb0c2d7ff15fe221f22a29aeb8371f24fa77a4425c920eb01a520babbc`。以上均與既有清單相符。使用官方離線安裝指令，隔離在專案目錄：

```sh
mkdir -p local/strata-control
tar -xzf "$HOME/Downloads/ai/tools/linux-x86_64/strata-control-0.1.59-linux-x86_64.tar.gz" -C local/strata-control
export STRATA_HOME="$PWD/local/state" STRATA_COMPONENTS_DIR="$PWD/local/components"
STRATA_NO_ACQUIRE=1 local/strata-control/bin/strata components install-file \
  "$HOME/Downloads/ai/tools/linux-x86_64/strata-engine-0.1.59-linux-x86_64-cuda-cuda12.tar.gz" \
  --components-dir "$STRATA_COMPONENTS_DIR" --output jsonl
```

工具驗證簽章與所有檔案、執行 `--version` 測試後成功安裝；該測試尚未載入模型。`components plan` 的一般 manifest 格式不接受此 Engine 的 schema 2；改由正式 `install-file` 檢驗。`STRATA_ENGINE` 環境變數不能讓 `launch` 的元件預檢辨識獨立解出的二進位；使用上述離線安裝。

本地模型 `bartowski/Qwen3.8-Flash-Next-IQ2_XS` 兩分片共 77,737,182,784 bytes，來源及歷史雜湊見 FILE_LIST；與計畫估算的 ISTA-DASLab 格式不同。4K 與 128K 的 `--plan` 報告本地模型下載 0 GB，但那不表示模型可用。為避免下載 drafter，明確 `--drafting off`；設定與計畫預設不同，基準測試必須保留此差異。

```sh
MODEL="$HOME/Downloads/ai/models/llm/bartowski/Qwen3.8-Flash-Next-GGUF/Qwen3.8-Flash-Next-IQ2_XS"
STRATA_NO_ACQUIRE=1 local/strata-control/bin/strata launch --plan --family qwen --model iq2_xs \
  --model-path "$MODEL" --context 128k --vision off --parallel 1 --access local --port 8080 \
  --tune skip --drafting off --output json
STRATA_NO_ACQUIRE=1 local/strata-control/bin/strata launch --family qwen --model iq2_xs \
  --model-path "$MODEL" --data-dir "$PWD/local/model-data" --context 4k --vision off \
  --parallel 1 --access local --port 8080 --tune skip --drafting off --yes --no-tui
```

注意：這版 launch 子程序會移除 `STRATA_NO_ACQUIRE`；必須先檢查 Engine 已安裝、`--plan` 的下載預估和實際檔案，不可單靠此變數保證不下載。測試進行中，詳見 `logs/03-launch-4k.txt`。

### 4K 第一次嘗試：失敗與相容性實驗

離線 Engine 安裝後啟動，setup 顯示 3080 compute capability 8.6、PCIe 3.0 x16、AVX2；準備階段 exit 1，尚未啟動服務。`logs/03-setup-4k.txt` 記錄 `hc_attn` / `hc_ffn` 權重為 Q4_K 或 Q5_0，但 Engine 需要 BF16。`--plan` 沒預告：setup 自動下載約 0.04 GB llama.cpp 原始碼，即使 `~/Downloads/ai/tools/source/` 已有封存；這是意外下載，並非大型模型。之後應在啟動前核對 setup 固定的 `LLAMA_CPP_COMMIT` 並將匹配的來源預放至安裝根目錄的 `third_party/llama.cpp`。

本版官方 `tools/iq_pack.py --help` 和檔頭記載 `--compat-bf16` 可將一般 Qwen4Exp 的非原生小型 projection 反量化後以 BF16 四捨五入，專家和 PLE 權重保留原樣；此轉換不會還原原始精度。以專案內獨立 pack 進行一次可回滾的相容性實驗，不改 GGUF：

```sh
STRATA_GGUF_PY="$PWD/local/install/third_party/llama.cpp/gguf-py" \
  local/strata-control/python/bin/python3.12 local/strata-control/tools/iq_pack.py \
  --gguf "$MODEL/Qwen3.8-Flash-Next-IQ2_XS-00001-of-00002.gguf" \
  --out "$PWD/local/model-data/packs/iq2_xs" --compat-bf16
```

此乃試驗，不表示該第三方量化已受官方支援；結果、轉換清單和啟動驗證均必須保留。

相容性實驗結果：pack 成功，362 tensors 轉換（168 exact、194 rounded，最大絕對誤差 0.0312），轉換細目見 `compat-bf16.json`。第二次啟動仍失敗，Engine 顯示 `native embedding: token_embd.weight is absent, of another shape, or of a type without a GPU dequantizer`，見 `logs/03-engine-4k-compat.log`。無 API、無 benchmark。RTX 3080 先例及正式模型檔資訊見 `3080-guides.md`。依使用者要求先查先例，不再試驗此第三方量化。

## 2026-11-15：接收學校下載的檔案

`~/Downloads/ai/models/llm/others` 中找到 ISTA IQ2_XS 兩分片、IQ3_S 第一分片及 27B UD-Q4_K_M，檔案大小符合清單；正在逐一執行 SHA256，結果寫入 `docs/research/logs/04-downloaded-models.sha256`。SSD 餘量約 49 GiB，128GB RAM 可用約 122 GiB。4K `--plan` 已選指定模型與獨立資料目錄，模型下載量 0；見 `logs/04-ista-plan-4k.json`。先前 bartowski 實驗與 ISTA 同名 pack 有混用風險；必須確認產生的新 pack 對應已校驗的 ISTA 分片，不能直接重用。

IQ2_XS 兩個檔案 SHA256 已比對官方值成功；以專案內 symbolic links 使用原始檔案，避免修改下載檔。IQ3_S 第一分片亦已校驗，第二分片以專案內 symbolic link 指向通過 hash 的共用 IQ2_XS 第二分片，尚未啟動 IQ3_S。

以官方 `iq_pack.py`（不使用 `--compat-bf16`）在 `local/ista-data/packs/iq2_xs` 先準備獨立 pack，避免 `setup` 從先前 bartowski 實驗資料夾自動找到同名 pack；actual launch config 確認 pack、native、ple 路徑均指向 ISTA 新資料。

2026-11-15 08:12，4K Strata 0.2.13 / Engine 0.1.59 CUDA 12 啟動成功，localhost:8080，vision off、parallel 1、int8 KV、drafting off，載入時間約 90 秒。GPU 顯存約 19,413 MiB（全卡含桌面），系統 swap 未增加。PLE 26.8 GiB 沒被鎖住（process memlock 限制），Engine 說可運作；hugepages 不可用，沒有變更系統。`/v1/models` 的 n_ctx 為 4096；API streaming smoke 回覆「系統運作正常，隨時為您服務。」finish_reason stop；prompt 25、completion 9、cached 0、engine timings 已保存。此短測不是 benchmark。見 `logs/04-ista-launch-4k.txt`、`04-ista-engine-4k.log`、`04-models.json`、`04-metrics.txt`、`04-smoke-sse.txt`。

全部四個下載檔的實際 SHA256 均與 `3080-guides.md` / `download-forecast.md` 的上游值相符，完整結果 `logs/04-downloaded-models.sha256`。128K plan 為本地檔案、額外下載 0，見 `logs/04-ista-plan-128k.json`；它沒有提供具體 RAM/VRAM/KV 預估，不能因此聲稱 128K 可行。

設定差異：雖然傳入 `--kv int8`，4K 時 `/metrics` 顯示 `kv=fp16`，檢查本版 `setup.py:10768`，context <= 8192 時程式固定為 fp16。不可把這次當 int8；128K 的實際格式將另行驗證。`/v1/messages/count_tokens` 為 Anthropic 協議，同一使用者訊息回報 65 tokens；Chat Completions smoke 回報 25 tokens（reasoning_effort=none），兩個模板／設定並不等價，不能把前者直接當 Chat benchmark 的 prompt 數。正式依 Chat `usage.prompt_tokens` 校準並驗收。見 `logs/04-token-count-anthropic.json`。

## 2026-11-15：Linux benchmark

以專案隔離 XDG state 啟動的 4K server 處於 idle，且僅有我們的 Strata compute process。停止該服務後以 `scripts/measure_strata_load.py` 啟動相同模型的 128K / int8 / vision off / parallel 1 / drafting off server；啟動到 ready 50.71 秒、49 個遙測樣本，可能受熱 page cache 影響，不可標作冷碟載入。結果與每秒 GPU/RAM/CPU 頻率及功耗在 `results/ubuntu/strata/flash-next/20261115/load-128k/`。GPU 整卡使用量含桌面，不是模型專屬值。128K `/metrics` 確認 KV int8、kv_resident 32768、expert cache 14404 MiB。

`python3 -m unittest discover -s tests -v` 的 4 個基本測試通過。4K server 上的 1K 試跑與正式 128K server 測試分開。128K server 上 1K：預熱一次、三次正式；每次 752 prompt tokens、128 output、0 cached；prefill 中位數 747.2 tokens/s、decode 100.34 tokens/s、TTFT 1.022s。輸入級別 1K，實際輸入約 752 tokens，並非 1024。詳細請求、Engine timings、每秒遙測見 `results/ubuntu/strata/flash-next/20261115/baseline-128k-1k/`。校準請求不列入正式樣本。64K 正在校準，首個校準約 105K tokens，屬校準而非 64K 樣本；後續依 usage 調整。`scripts/strata_longctx_bench.py` 在 1K 與 64K 之間新增校準期間遙測與 Xid 檢查，生成 prompt 的函式未變。

64K 首次校準實際 104732 tokens；第二次校準 62276 tokens。暖身輸入 62276、輸出 256、cached 0，prefill 2281.9 t/s、decode 87.0 t/s，但期間 swap 從近零增加到約 2.23 GiB；第二個校準期間已增加至 1.15 GiB。依計畫保護條件於第一個正式請求執行期間中止，Engine log 記錄該請求在讀入 55296/62277 token 後 cancelled，未列入正式成績。停止後 swap 約 2.4 GiB，其中 engine VmSwap 約 2.06 GiB；系統 MemAvailable 約 81 GiB，無 Xid／OOM，原因尚未確定。`pswpout` 已停止增加，不應將此現象直接斷言為持續 swap thrash；下一次需監測增量並保存暖身資料。

使用者後續明確要求將 GPU power limit 固定為 250 W 再實驗，取代計畫原本不調功耗的約束；先前所有結果皆在上限 320 W，不能與固定 250 W 結果混合。`nvidia-smi --query-gpu=power.limit,power.min_limit,power.max_limit` 回報 320 / 100 / 320 W；以一般帳號執行 `nvidia-smi -i 0 -pl 250` 回報 Insufficient Permissions（exit 4），設定仍是 320 W。計畫仍禁止 sudo，因此等待使用者以管理員權限自行設定，完成後查核實際 power.limit 再執行新一輪測試。

2026-11-15：使用者明確授權使用 sudo，並要求今後實驗固定 250W；計畫已更新至 2.1。`sudo -n nvidia-smi -i 0 -pl 250` 成功，`nvidia-smi` 確認 250.00W。此前「禁止 sudo」及「等待使用者設定」是歷史狀態，已由新指示取代。各次實驗須重新檢查 250W；320W 紀錄不與新結果混合。

使用者補充：目標是品質不變或不劣化前提下選擇中等速度、能供 Codex 使用的模型，以 Strata 為優先，另測一個 Dense。這必須透過一致的 coding、工具使用、長文檢索及參考配置 A/B 評估；量化無法事先保證和未量化原模型完全相同。`RTX3080_20GB_Strata_Qwen_Codex_PLAN_v2.md` 已加入此選模目標。
使用者補充：最後推薦的方案以 decode 至少 30 tokens/s 為目標，並須完成 Codex 相關品質與工具呼叫測試；不同 context 分別記錄，不能用短輸入成績保證所有情境。
使用者要求額外測試 256K tokens context；已納入計畫，須先驗證 128K 和資源狀態，再另開 256K server、記錄載入及實際輸入 token。256K 是 window 等級，非宣稱已測滿或 256KB bytes。

使用者最新約束：不再使用 Q2／IQ2，至少 Q3，Q3 與 Q4 都要測；IQ2 數據僅為歷史紀錄。計畫新增高優先選模指示：本機 ISTA IQ3_S 作主要 Strata 模型，本機 Unsloth UD-Q4_K_XL 亦須測，Dense 選既有 UD-Q4_K_M。256K 請求改由 Q3／Q4 視資源條件執行；均需固定 250W。

2026-11-15 IQ3_S 品質優先配置完成 1K / 64K / 128K / 256K（每級 warmup 1 次、正式有效 3 次）；`scripts/strata_longctx_bench.py` 的 `LEVELS` 增加 262,144-token 級距。正式中位數：

| context 設定 | 實際 prompt tokens | prefill tok/s | decode tok/s | TTFT | 總時間 |
|---:|---:|---:|---:|---:|---:|
| 1,024 | 753–755 | 355.86 | 71.43 | 2.14 s | 3.94 s |
| 65,536 | 62,878 左右 | 2,078.70 | 64.27 | 30.33 s | 34.24 s |
| 131,072 | 125,677–125,679 | 2,246.00 | 61.86 | 56.09 s | 60.22 s |
| 262,144 | 251,299–251,303 | 2,144.83 | 55.31 | 117.41 s | 121.88 s |

全部正式請求輸出 256 tokens、cache 0、無 flags / request error / Xid。128K 該級最高 GPU VRAM 19,586 MiB、溫度 61°C、GPU power draw 讀值最高 251.39W（`power.limit` 設定始終 250W；讀值短暫略高於設定），RAM 使用峰值 62.72 GiB、swap 約 0.33 GiB。256K 載入約 102.58 s；ready 時 `/metrics` max_context/context=262144、idle、VRAM 19,432 MiB、engine RSS 79.63 GiB、RAM available 69.28 GiB、swap 約 0.318 GiB。256K 該級最高 VRAM 19,588 MiB、溫度 61°C、讀值最高 250.31W、engine RSS 約 84.71 GiB、RAM 使用約 61.48 GiB、swap 約 0.318 GiB。128K → 256K decode 中位數降低約 10.6%，TTFT 增加約 2.09 倍；此合成長輸入僅量測容量及性能，不能證明 256K 檢索或 coding 品質。

完整請求／回應與逐秒遙測：`results/ubuntu/strata/flash-next/20261115/iq3-quality-250w-128k-{1k,64k,128k}/level-*/` 及 `results/ubuntu/strata/flash-next/20261115/iq3-quality-250w-256k-256k/level-256k/`；256K 啟動 log `logs/07-iq3-250w-load-256k.txt`，benchmark stdout `logs/07-iq3-250w-256k.txt`。每級有 `summary.json`、`raw.csv`、`requests.jsonl`、`telemetry.jsonl` 與 prompt hash；generator SHA256 見各級 `run.json`/log header。

2026-11-15 量化網路調查與本機權重清點見 `docs/research/quantization-web-research.md`：本機沒有 Q5/Q6 GGUF；本次不下載 Q5/Q6，Flash 只測 IQ3_S / UD-Q4_K_XL，Dense 只測既有 27B UD-Q4_K_M。Strata 官方 Q6 文件說明支援測試，但未提供 Q6 對 llama.cpp 的品質測量；個人回報不足以證明 Q5/Q6「品質差不多」。Q5/Q6 權重／PLE 記憶體需求亦顯著高於本次既有 Q4，網路參考不能替代本機 A/B。

Flash UD-Q4_K_XL 本機四個 GGUF 分片 SHA256 均吻合已下載清單，hash 輸出 `logs/08-unsloth-q4-sha256.txt`；`strata launch --plan` 證明本機使用、下載 0，plan 在 `logs/08-unsloth-q4-plan-4k.json`。首次 4K/int8 setup+load 共 564.29s，包含模型檔案完整性掃描、一次 pack 建立及啟動，並非冷碟 benchmark。setup 中可用 RAM 最低 48.07 GiB、系統 swap 最終 1.237 GiB（起始 0.317 GiB，增量約 0.92 GiB），engine RSS 73.36 GiB / swap 0.423 GiB；ready VRAM 19,446 MiB、GPU power cap 250W。1K 短 prompt 級 warmup 1 + formal 3 均有效，實際 prompt 751–755、completion 128、cache 0；decode 中位數 48.945 tok/s、prefill 209.414 tok/s、TTFT 3.631s、總計 6.209s，結果見 `results/ubuntu/strata/flash-next/20261115/unsloth-q4-quality-250w-4k-1k/level-1k/`。Strata `connect codex --check` prompt 與 tool-call 均成功（`logs/08-unsloth-q4-strata-connect-codex-check.json`）；該 helper 顯示 vendor-tested Codex CLI 0.163.0，與系統安裝的 `codex-cli 0.169.0` 不同，故後續仍需用版本 0.169.0 的隔離 `CODEX_HOME` 在 fixture 上驗證實際 T1–T3，不能把 helper check 當作完成 Codex 測試。

Q4 128K/int8 context 啟動 224.89s，ready 時 engine RSS 102.59 GiB、RAM available 45.45 GiB、swap 0.575 GiB、VRAM 19,448 MiB。64K/128K throughput 正式各 3 次，輸入約 62.9K/125.7K、completion 256、cache 0；decode median 45.179/44.711 tok/s，prefill 1,972.085/2,177.044 tok/s，TTFT 31.980/57.870s。結果在 `results/ubuntu/strata/flash-next/20261115/unsloth-q4-quality-250w-128k-64k-128k/level-{64k,128k}/`。一個首版品質 probe 因估算錯誤傳入 136,599 tokens 而遭 131,072 window 拒絕，沒有進入計分；錯誤見 `logs/08-unsloth-q4-quality-probe-128k-retry.txt`。修正初始估算後，品質 probe 用 124,727-token prompt、不同 nonce 避免 KV reuse，六個散佈的 ledger 欄位全部精確答對（6/6），回應 83 tokens、59.00s、cache_n=0；原始 prompt 與結果 `results/ubuntu/strata/flash-next/20261115/q4-long-context-quality-128k-retry2/{prompt.txt,result.json}`，probe JSON stdout `logs/08-unsloth-q4-quality-probe-128k-retry2.txt`。這個人工合成 needle-recall 集合是檢索指標，不能代替多樣化 coding / Codex 工具品質。

Q4 256K context setup/load 139.70s；ready 時 engine RSS 104.77 GiB、RAM available 43.83 GiB、swap 0.566 GiB、VRAM 19,449 MiB。256K throughput 正式 3 次，實際 prompt 251,300–251,302、completion 256、cache 0；decode median 43.141 tok/s、prefill 2,025.737 tok/s、TTFT 124.290s、總時間 130.203s。正式樣本最高 GPU 溫度 61°C、power draw 249.04W。結果在 `results/ubuntu/strata/flash-next/20261115/unsloth-q4-quality-250w-256k/level-256k/`。相同 6-key needle-recall 256K probe 得 6/6；實際 prompt 248,697、83 output tokens、125.371s、cache_n=0；原始資料在 `results/ubuntu/strata/flash-next/20261115/q4-long-context-quality-256k/{prompt.txt,result.json}`，log `logs/08-unsloth-q4-quality-probe-256k.txt`。與 128K probe 都是同一組答案，但 prompt filler 長度及 nonce 不同，兩次滿分只代表這個小型合成精確回憶測試，不能宣稱全部長 context coding 能力相等。

Codex CLI 0.169.0 在 Q4 上逐項完成相同 fixture 任務：T1 讀出 version=1.0.0 / architecture；T2 正確解釋 0/5/10 kg，並發現測試期待與 `<5` 目前實作不符。T2 雖要求不改檔，模型自發執行測試，確認原始錯誤（12 != 8），但沒有檔案修改。T3 在獨立副本將 `<5` 改為 `<=5`，`python3 -m unittest discover -s tests` 兩項 PASS，diff 只有一行。原始 fixture 雜湊保持不變。首次一般 `--sandbox read-only` 執行遇 bwrap network namespace `RTM_NEWADDR: Operation not permitted`，沒有讀檔；使用者提示的 Strata `connect codex --check` 文件亦明確指示無 bubblewrap 時只能在 throwaway folder bypass，因此後續 T1/T2/T3 使用工作目錄隔離副本及獨立 `CODEX_HOME`，設 `--dangerously-bypass-approvals-and-sandbox`，且 prompt 禁止網路。所有 Codex stdout/stderr 在 `logs/08-q4-codex-t1-bypass*`, `08-q4-codex-t2*`, `08-q4-codex-t3*`。Codex 說沒有 model metadata，fallback metadata 可能影響表現；不能因此推論所有 Codex 工作都穩定無誤。

使用者要求後續只使用至少 Q3；已停止 IQ2（歷史結果不參與選型）。ISTA IQ3_S 的主分片與共享第 2 分片各通過 SHA256，`--plan` 顯示無下載。2026-11-15 在 250W 上限啟動 IQ3_S 4K，首次從命令到 ready 110.60 秒（包含 pack 第一次建立，且快取狀態非冷碟），文本 API 以繁體中文回覆、usage 與 timings 正常；`/v1/models` 為 `qwen3.8-flash-next-iq3_s`，4K 實際 KV 為 fp16。載入遙測 `results/ubuntu/strata/flash-next/20261115/iq3-250w-load-4k/`，smoke `logs/07-iq3-smoke-sse.txt`。128K plan 無模型下載，接著在相同 250W 下切換到 128K / int8 以做 1K、64K、128K；之後才試 256K。

2026-11-15：新增自架 LLM agent harness 調查 `local-agent-harnesses.md`。官方資料確認 Hermes 可接本機相容 API 並要求 agent 使用至少 64K context；Codex CLI 有本機 OSS provider 流程，Codex + Strata 已有舊版 0.163 prompt/tool smoke，但尚未以安裝的 0.169 完成 coding 工作驗收。社群貼文反覆提及本機日常／雲端難題、Hermes 通用助理搭配 coding harness、以及 Responses API／tool-call 相容性差異。此回合僅研究與寫文件，未安裝 Hermes 或更動模型／設定。

2026-11-16：依使用者新題目調查中國象棋機器學習。新增 `xiangqi-ml-training-3080.md`，並加入研究索引。查閱 Xiangqi SL+RL 論文、AlphaZero 論文、Pikafish 官方資料、Px0 和 CC-Lite repo。結論：3080 可以訓練象棋網路 prototype；目前沒有可信的 RTX 3080 20GB「達世界前十」工時資料。2024 Xiangqi 論文報告特定真人線上天梯 top 0.1%，但硬體與訓練成本資訊不足以複現或換算；AlphaZero 的 9h 使用 5,000 TPU self-play actors、64 TPU trainer、44M 遊戲，不能外推為單卡 3080 幾小時。建議先明確定義 human ladder 或 engine ranking，檢查 CC-Lite 研究 baseline，再做 debug、棋譜監督 baseline、teacher distillation／self-play pilot 和成對對局評估。此回合僅研究與寫文件，未下載象棋模型／棋譜、安裝軟體或執行訓練。

2026-11-16：使用者追問他人使用 GPU 的象棋訓練方法與經驗。補充查閱 icyChessZero 作者的 2018 實作回顧與 repo、CC-Lite、AlphaBing、Px0、PyTorch SL+PPO 專案及一份近期設計提案。可核實的舊案例稱使用 4–5 台 GPU server，作者當時僅估計需半年至一年達中上人類水平；單張 1080 Ti 多 worker 實作同時提醒 CPU 核心會限制作業數。單卡研究工作台的例子支援小模型、batch/MCTS 調整，但沒有 RTX 3080 對應的棋力和速度證據。近期提案的 3060 / 4 GPU 時間表只是規劃估值。新增比較表、證據限制與單卡 throughput pilot 建議；未安裝或下載任何程式／資料。

品質優先調查：IQ3_S 預設 Engine 啟動日誌顯示 route tail skip 實際跳過 experts。Strata 官方 [DETAILS](https://github.com/Niko1221/Strata/blob/main/docs/DETAILS.md) 指出 `STRATA_ROUTE_TAIL_SKIP=7` 可能令回答不同，並將 `STRATA_PREFILL_CPU_SHARE=0` 列為可關閉會造成末位數值差異的短 prompt CPU sharing。為建立品質優先測試配置，IQ3 正式 benchmark 先關閉兩者：`--set STRATA_ROUTE_TAIL_SKIP=0 --set STRATA_PREFILL_CPU_SHARE=0`；這不保證量化模型等同 BF16，也不能排除其他浮點精度差異，須以 coding、工具與檢索任務測試。此前 default 啟動僅作 smoke，不能視為此配置的基準。

2026-11-15 IQ3_S 對照品質與 Codex：128K/int8 setup/load 134.67s、256K/int8 103.30s；256K ready RSS 仍約 78 GiB、RAM available 69.38 GiB、swap 0.563 GiB、VRAM 19,432 MiB。前述兩 context 的六欄位固定 needle-recall probe 都是 6/6：128K prompt 124,727 tokens/58.67s；256K prompt 248,697 tokens/119.81s、cache 0、83 output、`predicted_per_second=37.4`。完整 input/answer/hardware 在 `results/ubuntu/strata/flash-next/20261115/iq3-long-context-quality-{128k,256k}/`，probe logs `logs/09-iq3-quality-probe-{128k,256k}.txt`。Q3 與 Q4 在這個合成小樣本都 128K/256K 全對，因此無法以此排量化或 context 品質高下。

Codex CLI 0.169.0、Strata IQ3_S、medium reasoning 用隔離 `CODEX_HOME`/fixture copy 重跑 T1/T2/T3：讀 README 正確；解釋 0kg=$8、5kg=$12、10kg=$20，指出測試期待 5kg=$8；T2 自行跑既有測試得到預期邊界失敗但未修改檔案；T3 單行 `<5`→`<=5`，兩個 unittest PASS。Q4/IQ3_S 這三項 fixture outcomes 一致，這不是完整 Codex benchmark。log `logs/09-iq3-codex-t{1,2,3}.{jsonl,stderr}`，source fixture hash `55b657324d255294dda4ffda452b9c48d885b9b2c7ba740c1c6cd11b77bf8f7b`，修正後 copy hash `8228a6f91b667684773e7f213b8dba1dc45a99f73f4127646c2eecb703fa0328`。

## 2026-11-15：Qwen3.8-27B Dense UD-Q4_K_M 初測

模型 SHA256 已核對：`1bce504dfecd84153666928a41d8a66706f0158d3a317bc5196b72819d7dc529`。使用本機 llama.cpp b12375 CUDA12.8，服務綁定 `127.0.0.1:8081`；GPU power limit 250W，GPU layers 99、threads 10、parallel 1、K/V cache Q8_0、flash attention on、reasoning effort none。4K context 的 1K prompt benchmark（warmup 1 + formal 3）decode 中位數 36.276 tok/s、prefill 1,014.519 tok/s、TTFT 約 0.82s；formal summary：`results/ubuntu/llama-cpp/qwen27b/20261115/q4km-quality-250w-4k-1k/level-1k/summary.json`，log `logs/10-qwen27b-q4km-250w-4k-1k.txt`。服務 `/v1/models` 回報 `n_ctx=4096`、訓練 context `262144`、約 27.32B parameters、Q4_K medium。首個未設 `reasoning_effort=none` 的 API smoke 把短回答放進 `reasoning_content`，所以正式 benchmark 固定 none；兩份 smoke JSON 均保留於 `results/ubuntu/llama-cpp/qwen27b/20261115/`。

為檢查 Dense 長 context，在停止 4K 服務後以 131072 context 重啟同一模型，加入 `--no-kv-offload` 讓長 context KV 留在主機 RAM，其他設定不變。啟動 7.72 秒、power limit 驗證 250W、RAM available 122.88→117.93 GiB、swap 約 0.559 GiB、VRAM 16,190 MiB；page cache 可能已暖，不能稱為 cold load。64K 級完成一次校準和一次完整 warmup pilot，實際 prompt 62,874 tokens、completion 256、cache 0：prefill 638.22 tok/s、decode 2.994 tok/s、TTFT 99.83s、總時間 185.35s；GPU VRAM peak 16,323 MiB、util peak 94%、temp peak 58°C、功耗讀值 peak 233.39W、power limit peak/avg 均 250W，RAM peak 10.61 GiB、swap peak 0.559 GiB、無 Xid/error/benchmark flags。證據：`results/ubuntu/llama-cpp/qwen27b/20261115/q4km-load-128k/startup.json`、`.../q4km-load-128k/server.log`、`results/ubuntu/llama-cpp/qwen27b/20261115/q4km-quality-250w-128k-64k-128k/environment.json` 與 `level-64k/{level_start.json,calibration.jsonl,requests.jsonl}`。正式三次重複尚未執行；因完整 warmup 已顯示約 3 tok/s，低於選型目標 30 tok/s 一個數量級，終止該 benchmark 並關閉服務以免浪費長時間重複確認。這個單樣本只足以淘汰目前 CPU KV 長 context 執行路徑，不證明 Dense 模型所有 context 或不同 KV/硬體設定都同速；未做 Dense 128K/256K throughput 或檢索測試。

實驗安排：在獨立 `CODEX_HOME` 與 throwaway fixture copy，以 Codex CLI 0.169.0 驗收 Dense 短 context（讀取、debug、最小修正與測試），結果與限制記於下文。Dense 尚不能視為 64K+ 達標方案。

Dense Codex 驗收結果（更新）：用 Codex CLI 0.169.0、`local/codex-home-dense/config.toml`、本機 llama.cpp Responses API 及隔離副本 `local/codex-fixture-dense` 執行。初始 4K context T1 失敗：Codex 送出 6,095-token 請求，server 的 n_ctx=4,096 而回 400；未修改檔案。改成 n_ctx=8,192、`--no-kv-offload` 後，T1 正確讀出版本 1.0.0 與 Python shipping-price library 架構；T2 正確解釋負數例外、5kg 實際落在 $12 而測試要求 $8、10kg 落在 $20。T3 只修改 throwaway copy 中一個條件 `< 5`→`<= 5`，Codex 自己執行 `python3 -m unittest discover -s tests`，2 tests PASS；之後 Codex 重複讀檔並重跑測試，未結束 turn，故人工停止此冗餘循環。原始 fixture SHA256 `55b657324d255294dda4ffda452b9c48d885b9b2c7ba740c1c6cd11b77bf8f7b` 未變；隔離副本修改後 SHA256 `8228a6f91b667684773e7f213b8dba1dc45a99f73f4127646c2eecb703fa0328`。T1/T2/T3 JSONL 與 stderr 分別在 `docs/research/logs/10-dense-codex-t{1,2,3}-8k.*`；4K 超 context 記錄 `logs/10-dense-codex-t1.*`。8K 設定的 server log 顯示 T3 一個長回覆約 9 tok/s；這是實際 Codex 工具 session，不與 direct API 的 4K 1K prompt decode 36.28 tok/s 混用。llama.cpp 記錄 `namespace`、`web_search` tool types 不支援並跳過；本 fixture 不需要網路搜尋。所有服務結束後 GPU power limit 仍為 250W。

選型判斷（就目前測到的機器與配置）：Strata Flash-Next IQ3_S / UD-Q4_K_XL 是符合「中等速度且 >=30 tok/s」的主要候選，因 1K–256K direct benchmark 都超過門檻，且 Codex T1/T2/T3 fixture session 完成。Dense UD-Q4_K_M 的 4K direct API 數據達標，但 64K CPU-KV decode 只有 2.99 tok/s，Codex 需要至少 8K 才能承載實際請求，T3 session 約 9 tok/s 且完成回報循環異常；因此 Dense 不符合本次「可用 Codex 且至少 30 tok/s」的整體選型目標。所有品質判斷仍是小型 fixture 和六點合成 needle retrieval，沒有大規模 benchmark，不能宣稱 Strata/Q3/Q4 與高精度模型品質等同。

## 2026-11-15: Q2 model cleanup

User requested removal of Q2. Removed all usable IQ2_XS weights: both bartowski shards and the ISTA IQ2_XS first shard. Removed the two Q2-only Strata pack caches. The ISTA IQ2_XS second shard is byte-identical to the IQ3_S second lookup-table shard, so it was moved to a neutral `shared/` filename and the IQ3_S symlink was updated. Its SHA-256 before/after move is `316b46f3a2dbd68c900f43136ab9449f9dcc3725dfd8c794847c204bc161e113`; IQ3_S link resolves successfully. Historical Q2 logs/results remain. Root free space increased from 43 GiB to 155 GiB. Exact paths and byte counts: `docs/research/logs/11-q2-cleanup.txt`.
