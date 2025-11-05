# Telegram Bot (Webhook)

## Files
- `app_webhook.py` : webhook server (python-telegram-bot v20, aiohttp)
- `requirements.txt`, `Procfile`
- `.env.example` (範例 env)

## Deploy (Render / Railway / any service with HTTPS)
1. 將專案檔案 push 到 GitHub repo。
2. 在云平台 (Render/Railway) 新增 Web Service，連接 GitHub repo。
3. 在平台 Environment Variables 設定：
   - `TG_BOT_TOKEN` = 你的 bot token
   - `PUBLIC_URL` = 你的服務網址 (e.g. https://your-service.onrender.com)
   - `WEBHOOK_PATH` = (optional) 自訂 webhook 路徑，如 `/hook-abc123`；留空會由程式自動生成
4. 啟動服務後，若你一開始沒有設定 `PUBLIC_URL`，部署完成後請設定此變數並重啟服務，以便程式自動向 Telegram 註冊 webhook。
5. 測試：在 Telegram 對你的 bot 發 `/start` 或 `/ping`。

## 注意
- 實際 token 不要推上 GitHub；只放 `.env.example` 作示範。
