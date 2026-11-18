# Qwen Flash 與 Hermes 內網部署（2026-11-18）

## 配置與來源

使用本機已有 Unsloth Qwen3.8-Flash-Next UD-Q4_K_XL、Strata Terminal 0.2.13 / Engine 0.1.59 CUDA12；context 131072、parallel 1、vision off、drafting off、quality baseline（route tail skip 0、prefill CPU share 0）、GPU 上限 250W。原先 GPU 空閒，上限為 320W；依先前授權設回 250W。2026-11-18 在本機與 LAN 的 `/v1/models` 均使用 API key 返回 200，模型顯示 loaded。LAN API `http://192.168.10.99:8080/v1`；金鑰存放於被忽略、權限 600 的 `local/hermes-private/api-key`，不得放入 Git 或日誌。

Hermes Agent 官方 v0.23.2 commit `ae2a81ccc00e` 安裝在 `local/hermes-agent`，隔離 Python 3.14.10 在 `local/hermes-venv`，狀態、設定在 `local/hermes-home`；未改系統 Python。官方 release 使用 uv override 以允許 browser-harness 對 Pillow 的版本衝突，`uv pip install -e` 需明確傳入由原始 `pyproject.toml` 的 `tool.uv.override-dependencies` 產生的 `local/hermes-private/uv-overrides.txt`。Python 套件安裝後以自訂 provider 指向 `127.0.0.1:8080/v1`，上下文 131072。Hermes oneshot 繁體中文回答成功。Strata `connect hermes --check` 的 prompt 與 tool call 均成功；注意其 JSON 可能輸出 API key，不能公開記錄。

官方 [Hermes dashboard](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) 使用 Node 和 pnpm 編譯；獨立安裝 Node 26.12.1 / pnpm 12.15.0 到 `local/hermes-js`，採用官方 pnpm lockfile。Dashboard 預定綁定 LAN IP `192.168.10.99:9119`，帳號 `admin`；密碼及 API key 均為獨立隨機值存放在 `local/hermes-private/`（600），dashboard 配置保存密碼 hash。Dashboard 是可呼叫命令及讀寫檔案的 agent 管理介面，只適合可信內網或 VPN；密碼驗證不提供 HTTP 傳輸加密。不要將其公開到網際網路。Python/Node、程式和前端依賴有下載，未下載新模型。

## 啟動狀態

Strata `--access lan --api-key-env STRATA_LAN_KEY --port 8080`，使用專案的 STRATA_HOME、STRATA_COMPONENTS_DIR、XDG_STATE_HOME。該次 launch log 經 CLI 顯示模型 loaded；API key 自 `local/hermes-private/api-key` 讀入環境，不記錄於命令列或此文件。模型需要較多載入時間，且目前啟動程序並非自動開機服務。

Hermes Web 的 Node 依賴以 `pnpm install --frozen-lockfile --filter web...` 安裝並 `pnpm --dir web run build` 編譯；聊天 TUI 另以 `pnpm install --frozen-lockfile --filter hermes-tui...` 和 `pnpm --dir ui-tui run build` 編譯。安裝期間固定 lockfile 的套件來源檢查耗時約 82 秒；前端編譯完成。以 systemd user transient unit `hermes-dashboard-3080` 啟動，監聽 `192.168.10.99:9119`：

```sh
systemd-run --user --unit=hermes-dashboard-3080 \
  --property=WorkingDirectory=/home/swchen/git/install_3080_llm/local/hermes-agent \
  --setenv=HERMES_HOME=/home/swchen/git/install_3080_llm/local/hermes-home \
  --setenv=PATH=/home/swchen/git/install_3080_llm/local/hermes-js/node_modules/.bin:/home/swchen/git/install_3080_llm/local/hermes-venv/bin:/usr/local/bin:/usr/bin:/bin \
  /home/swchen/git/install_3080_llm/local/hermes-venv/bin/hermes dashboard \
  --skip-build --host 192.168.10.99 --port 9119 --no-open
```

驗收：LAN 的 `/api/status` 回報 `auth_required=true`、`auth_providers=[basic]`；以密碼登入 `/auth/password-login` 回 200，`/api/auth/me` 和前端頁面皆回 200。未登入存取 Strata `/v1/models` 回 401；帶 key 的本機與 LAN models request 皆回 200。Hermes CLI 實際呼叫本機模型回覆繁體中文成功，另以 tool 執行 `pwd` 並回報預期路徑成功。Strata Hermes 接口檢查的 prompt 和 tool-call 均通過；尚未用 iPad 實際操作瀏覽器聊天，WebSocket 聊天端到端仍待使用者實機確認。

## Codex Responses API 驗證（2026-11-18）

後續針對 Codex 要求的 Responses API 再做端到端檢查：

- Strata 綁定 `0.0.0.0:8080`；主機區域網路 IP 為 `192.168.10.99`，本機 UFW 顯示 inactive、nftables input/filter 規則為空。從服務主機分別連 `127.0.0.1` 和 `192.168.10.99`，帶 key 的 `/v1/responses` 都回 HTTP 200；未帶 key 的 `/v1/models` 回 HTTP 401。此結果證明主機服務及本機 LAN 位址可用，不等於已從另一台 LAN 裝置驗證路由器/Wi-Fi 用戶端隔離設定。
- `/v1/responses` 非串流請求回 HTTP 200、`status=completed`。串流回 HTTP 200，完整收到 `response.created`、增量事件及終止事件 `response.completed`。故意限制輸出 token 過低的短請求可能以 `response.incomplete` 結尾，這是 token 上限結果，不是連線錯誤。
- Responses API 的函式工具請求返回 `function_call`。Codex CLI 實際執行工具後，再把工具結果交回模型並完成最終回答，驗證了 Responses + 工具呼叫的完整回合。
- 本機 Codex CLI 實際版本是 **0.169.0**（`codex --version`），並非 0.170.0。使用臨時 `CODEX_HOME` 指向 Strata 的 `wire_api="responses"` provider；唯讀 sandbox 首次因主機不允許 `bwrap` 建立 user namespace 而無法啟動工具。改以 Codex `danger-full-access` sandbox 跑無修改的 `pwd`，工具成功並回覆 `CODEX_TOOL_OK`。此驗證確認 0.169.0 的 Responses/工具流程；0.170.0 尚未在此主機安裝或測試。
- Vision 保持關閉，沒有進行圖片輸入測試。API key 留在權限 600、Git 忽略的本機狀態檔中，沒有寫入本報告。

若另一個遠端執行環境無法連線 `192.168.10.99:8080`，此主機端的 listener、防火牆狀態及本機 LAN-IP 測試都正常，問題更可能在該執行環境到此私有網段的網路路徑（例如不在同一 LAN、VPN/容器網路隔離或 Wi-Fi client isolation）。要確認 iPad/其他用戶端，需在同一可信 LAN 上直接測試網址；服務端本身目前已提供 LAN listener。不要將 API 或 dashboard 直接暴露到公網。

Dashboard 使用 transient user service，和 Strata 一樣不是開機自動啟動；重開機或該使用者的 systemd session 結束後需再啟動。當 LAN IP 改變時，dashboard 綁定及網址要一起調整。此次不把密碼與 key 提交到 Git。
