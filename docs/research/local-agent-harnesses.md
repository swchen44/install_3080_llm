# 自架 LLM 的 Agent Harness 與實際工作流

研究日期：2026-11-15。網路貼文屬個別使用者經驗，不是受控比較。這份整理用來選擇本機模型外面的工具層（harness），不代表已在本機完成端到端 coding 評測。

## 名詞與架構

自架模型通常不是直接「裝進 Codex/Hermes」；常見架構是模型由推論伺服器載入並提供本機 API，agent harness 再把使用者任務、工具定義和檔案操作送給該 API。模型做決策與生成，harness 負責讀寫檔案、執行命令、批准權限、管理多步驟循環和保存對話。

本機現況已具備這種拆分：Strata 載入 Qwen GGUF，Codex CLI 可透過 Strata 的 Responses API 與工具呼叫介面連線。`logs/08-unsloth-q4-strata-connect-codex-check.json` 的 prompt 和工具呼叫檢查通過，但使用的是 Codex CLI 0.163.0，而主機安裝版本記錄為 0.169.0；這不是完整程式修改品質驗收。Strata CLI 也列有 `hermes` connector，但本機尚無 Hermes 對 Strata 的相容性／任務測試。

## 社群常見工作模式

1. **本機模型做日常，較強的雲端模型做難題。** r/hermesagent 一位使用者以本機 Qwen2.5 14B 4-bit 處理一般任務，把較複雜推理留給 Codex；他回報本機日常可用，但細膩度、一致性和 persona 保持仍落後於 Codex。此例是 Mac 上的個人經驗，不可直接推論 3080/Qwen3.8 結果。[貼文](https://www.reddit.com/r/hermesagent/comments/1tz4rsg/tried_a_hybrid_local_cloud_hermes_setup_curious/)
2. **Hermes 做通用助理，coding 交給 coding 專用 harness。** LocalLLaMA 使用者描述 Hermes 用於一般對話、工具操作和小型設定修正；較正式或複雜的程式工作則另外啟動 Codex 或 Pi。另有使用者以本機模型做小型前端調整，複雜工作再切 API 模型。[討論串](https://www.reddit.com/r/LocalLLaMA/comments/1uvypn9/hermes_agent_with_local_llms/)
3. **比較 harness 前先排除 API／工具格式問題。** Codex 使用者回報中，有人遇到本機 llama.cpp 的 Responses API 相容問題，也有人認為 Codex agent loop 很完整但對本機端點較挑；Pi/OpenCode 對多種開源後端較容易調整。這些經驗會隨版本和 server 改變。討論者建議固定小型任務集，分開看工具呼叫成功率、失敗恢復、diff 品質、延遲與 token 消耗，避免把 adapter 問題誤判成模型能力。[Codex harness 討論](https://www.reddit.com/r/LocalLLaMA/comments/1uuib36/how_is_codex_as_a_harness_for_local_models/)
4. **工具呼叫與 context 設定是實際瓶頸。** Hermes 官方指出本機 agent 需要至少 64K context，Ollama 預設 context 可能太小；server 也必須正確輸出結構化 tool calls。Hermes system prompt 和工具 schema 每次都要 prefill，啟用大量工具會增加首 token 等待與 context 壓力。[Hermes 本機 Ollama 指南](https://hermes-agent.nousresearch.com/docs/guides/local-ollama-setup) [Hermes providers](https://hermes-agent.nousresearch.com/docs/integrations/providers)

## Codex 和 Hermes 各適合什麼

### Codex CLI

- 優點：使用者已熟悉；直接在 repository 內工作；Codex CLI 可接本機模型，Codex 專案另有原生 `--oss` 流程。OpenAI 公開原始碼目前列出 `ollama` 和 `lmstudio` 為原生 OSS provider；自訂相容 endpoint 則需設定 provider，且要對上 Codex 使用的 Responses API。Strata 的 Codex connector 已提供這種設定方向。[Codex CLI OSS provider 選項](https://github.com/openai/codex/blob/main/codex-rs/utils/cli/src/shared_options.rs) [Codex provider 實作](https://github.com/openai/codex/blob/main/codex-rs/model-provider-info/src/lib.rs)
- 限制：Responses API 和 tool schema 相容性很重要；社群回報 llama.cpp/Ollama 的端點可能能聊天但工具循環或啟動不一定正常。某些只在雲端提供的能力也不會因為改成本機模型而自動存在。逐項檢查，不預設全部功能都可用。
- 適合你：先沿用 Codex CLI + Strata + 現有 Q3/Q4 模型，因為這符合習慣且已有基本連線／tool-call smoke。再用你實際 repository 任務驗收檔案閱讀、patch、測試修復、工具呼叫和長 context。

### Hermes Agent

- 優點：更像通用、可持續使用的助理／自動化 agent，支援本機 OpenAI-compatible endpoint、profiles、memory、skills 和 messaging gateway；可以把聊天、定時／訊息入口與一般工具任務放在一個環境。[Hermes providers 文件](https://hermes-agent.nousresearch.com/docs/integrations/providers) [Hermes FAQ](https://hermes-agent.nousresearch.com/docs/reference/faq/)
- 限制：Hermes 文件要求本機 agent 至少 64K context；系統 prompt、記憶、工具 schema 會佔掉 prompt，且先 prefill 再開始生成。對本機推論而言，開很多不常用工具會增加等待和 context 消耗。工具呼叫是否被模型和 server 正確支援仍須實測。
- 適合你：若你想要「一般助理 + skills/memory + 手機訊息入口」，可另建 Hermes profile 接相同本機模型伺服器試用；不要因此取代 Codex 的程式工作流，除非實際任務比較後更喜歡 Hermes。

## 對本機 3080 的建議工作流

1. **主要 coding：Codex CLI + Strata + 已有 Qwen3.8 Flash Q3/Q4。** Codex 用熟悉的交互方式；Strata 繼續作為模型 server。先選 64K 作 agent 驗收起點，確認模型 server 實際 context；若希望更大任務再試 128K。現有 128K/256K 是吞吐和資源測量，不代表 agent 在這些 context 下已通過檢索或 coding 品質測試。
2. **驗收後才選日常模型。** 固定相同 repo 和任務，比較 Q3 IQ3_S 與 Q4 UD-Q4_K_XL 的 patch 正確度、漏改／誤改、工具呼叫、測試修復、context 保持、首 token 時間與 decode 速度。模型大不等於 agent 自動更可靠；量化 benchmark 也不能代替工具循環測試。
3. **較長或複雜工作用可中斷的小步驟。** 先讓 agent 說明將改哪些檔案，再讓它做一個有界變更、檢視 diff、執行專案既有測試，最後人工 review。把「工具回覆成功」和「工作成果正確」當成兩個獨立驗收項目。
4. **Hermes 作為第二條工作流，視需求再裝。** 如果有持續記憶、skills 或手機／訊息入口的需求，再試 Hermes；先精簡工具集合並核對它傳給 Strata 的協定與 64K context。單卡同一時間仍由一個模型 server 佔用 GPU，切換 harness 不代表可同時跑兩份大型推論。
5. **雲端不是必要條件。** 社群常見混合方案是難題切雲端，但你品質優先也可先全本機驗收；如日後要混合，使用者明確手動切 provider，避免不知情的自動 fallback 把私有程式碼送出本機。

## 待實測項目與現況界線

- 已有 Strata connector 的 Codex prompt/tool-call smoke，版本 0.163.0；未完成主機 Codex CLI 0.169.0 的同版本整合確認及真實 repository 任務驗收。
- Hermes 對 Strata 的 API 相容、64K 設定和 tool-call 成功率尚未測試。
- Q3 與 Q4 的 context 容量／速度紀錄已在其他研究章節，但尚不能代表 harness 下的程式修改品質。
- 此研究沒有安裝 Hermes、改寫使用者設定、下載模型或啟用雲端 fallback。

## 參考連結

- OpenAI Codex CLI local provider options: https://github.com/openai/codex/blob/main/codex-rs/utils/cli/src/shared_options.rs
- OpenAI Codex provider implementation: https://github.com/openai/codex/blob/main/codex-rs/model-provider-info/src/lib.rs
- Hermes Agent providers: https://hermes-agent.nousresearch.com/docs/integrations/providers
- Hermes local Ollama guide: https://hermes-agent.nousresearch.com/docs/guides/local-ollama-setup
- Hermes FAQ: https://hermes-agent.nousresearch.com/docs/reference/faq/
- Local + cloud Hermes user report: https://www.reddit.com/r/hermesagent/comments/1tz4rsg/tried_a_hybrid_local_cloud_hermes_setup_curious/
- Hermes + local models discussion: https://www.reddit.com/r/LocalLLaMA/comments/1uvypn9/hermes_agent_with_local_llms/
- Codex as a local-model harness discussion: https://www.reddit.com/r/LocalLLaMA/comments/1uuib36/how_is_codex_as_a_harness_for_local_models/
