# app_webhook.py
import os
import asyncio
import secrets
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
PUBLIC_URL    = os.getenv("PUBLIC_URL")   # e.g. https://your-service.onrender.com
WEBHOOK_PATH  = os.getenv("WEBHOOK_PATH") # if empty, we generate one and print it
PORT          = int(os.getenv("PORT", "8080"))

if not TG_BOT_TOKEN:
    raise RuntimeError("Missing TG_BOT_TOKEN (set as env var)")

# 如果沒有設定 WEBHOOK_PATH，程式啟動時會生成一個安全隨機路徑
if not WEBHOOK_PATH:
    WEBHOOK_PATH = "/hook-" + secrets.token_hex(12)

# handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot 已部署並以 Webhook 運行 ✅")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong")

# 建 Application
application = Application.builder().token(TG_BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("ping", ping))

# health check for platform
async def health(request):
    return web.Response(text="ok")

# register health route on aiohttp internal web app if available
try:
    application.web_app.add_routes([web.get("/", health)])
except Exception:
    pass

async def main():
    print("Starting bot (webhook mode)...")
    await application.initialize()
    await application.start()

    # 如果 PUBLIC_URL 沒設定，print 提示並不設 webhook（你可以在平台設定後重啟）
    if not PUBLIC_URL:
        print("WARNING: PUBLIC_URL not set. Set PUBLIC_URL to your service URL (https://...) and restart to enable webhook.")
    else:
        webhook_url = PUBLIC_URL.rstrip("/") + WEBHOOK_PATH
        await application.bot.set_webhook(url=webhook_url)
        print("Webhook set to:", webhook_url)

    # 啟動 aiohttp server 以監聽 webhook（python-telegram-bot 的內部 webhook 支援）
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH.lstrip("/"),
        webhook_url=(PUBLIC_URL.rstrip("/") + WEBHOOK_PATH),
        drop_pending_updates=True,
    )
    print(f"Listening on 0.0.0.0:{PORT}  (path: {WEBHOOK_PATH})")
    # 永久等待
    await asyncio.Event().wait()

if __name
