# Pi Coding Agent 連接本機 Strata（2026-11-18）

## 安裝

安裝官方 npm 套件 [`@earendil-works/pi-coding-agent`](https://github.com/earendil-works/pi)，固定版本 1.5.2，放在被 Git 忽略的 `local/pi-agent`；安裝時使用 `--ignore-scripts`。Pi 要求 Node.js 22.19 或以上，因此使用此前已安裝於 `local/hermes-js` 的 Node 26.12.1，沒有變更系統 Node 或 Python，也沒有下載模型。`/home/swchen/.local/bin/pi` 是啟動 wrapper，會選用隔離安裝目錄中的 Pi、Node 及設定。

## 本機模型設定

Pi 使用獨立設定目錄 `local/pi-agent-home`，不混用 Hermes 設定：

- `settings.json` 將 `strata/qwen3.8-flash-next-unsloth-ud-q4_k_xl` 設為預設 provider/model，預設 thinking level 為 medium。
- `models.json` 設定 `api: openai-responses`、`baseUrl: http://127.0.0.1:8080/v1`，context window 為 131072、最大輸出設定為 8192 tokens，並標記純文字輸入。Strata 仍維持 vision off。
- API key 由 Pi 設定中的 `!cat /home/swchen/git/install_3080_llm/local/hermes-private/api-key` 在執行時讀取；不把 key 複製進 Pi 設定、研究文件或 Git。設定目錄權限 700，設定檔 600；key 原檔權限 600。

## 驗收結果

- `pi --version`：1.5.2；`pi --list-models` 顯示 Strata Qwen 模型、131.1K context、8.2K max output、thinking enabled、images disabled。
- 以預設 medium thinking level 執行純文字提示，Pi 成功回覆 `PI_DEFAULT_OK`。
- JSON event mode 顯示 `tool_execution_start` 的工具為 `bash`、命令為 `pwd`，`tool_execution_end` 回報 exit code 0 和正確工作目錄，之後模型完成最終回答 `PI_JSON_TOOL_OK`。這確認了 Responses API、串流事件、工具呼叫及工具結果回傳的完整一輪。
- 另外以 thinking off 再次測試文字回覆與 bash 工具呼叫，均成功。

## 使用方式

在 shell 直接執行 `pi` 啟動互動式 agent；`pi --list-models` 查看已設定模型。Pi 連到本機 `127.0.0.1:8080`，所以必須先啟動 Strata/Qwen 服務。Pi 本身不會在重開機後替 Strata 啟動模型服務。
