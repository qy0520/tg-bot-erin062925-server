import os, time
import os, sys
from typing import Any, Dict
from fastapi import FastAPI, Request, Header, HTTPException
from dotenv import load_dotenv
import httpx
from openai import OpenAI

def need(key):
    v = os.environ.get(key)
    if not v:
        print(f"[FATAL] Missing env: {key}", file=sys.stderr)
        sys.exit(1)
    return v

TELEGRAM_BOT_TOKEN = need("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY     = need("OPENAI_API_KEY")
WEBHOOK_SECRET     = os.environ.get("WEBHOOK_SECRET", "")
ONLY_18_PLUS       = os.environ.get("ONLY_18_PLUS", "true").lower() == "true"
RATE_LIMIT_PER_MIN = int(os.environ.get("RATE_LIMIT_PER_MIN", "20"))
SYSTEM_PROMPT      = os.environ.get("SYSTEM_PROMPT", "你是僅供成年人使用的AI助理...")


load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
ONLY_18_PLUS = os.environ.get("ONLY_18_PLUS", "true").lower() == "true"
RATE_LIMIT_PER_MIN = int(os.environ.get("RATE_LIMIT_PER_MIN", "20"))
SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", "你是僅供成年人使用的AI助理...")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
client = OpenAI(api_key=OPENAI_API_KEY)
http = httpx.AsyncClient(timeout=20.0)

# 極簡節流：記憶近 60 秒計數（正式可換 Redis）
from collections import defaultdict, deque
hitlog: Dict[int, deque] = defaultdict(deque)

app = FastAPI()

def rate_limited(chat_id: int) -> bool:
    now = time.time()
    q = hitlog[chat_id]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= RATE_LIMIT_PER_MIN:
        return True
    q.append(now)
    return False

async def tg_send_text(chat_id: int, text: str):
    await http.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def violates_age_policy(text: str) -> bool:
    if not ONLY_18_PLUS:
        return False
    keywords = ["未成年","小孩","國小","國中","高中","未滿18","未滿十八","未成年人成","兒童"]
    t = text or ""
    return any(k in t for k in keywords)

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.post("/webhook")
async def webhook(req: Request, x_telegram_bot_api_secret_token: str = Header(None)):
    # 1) 驗證 TG Webhook Secret
    if WEBHOOK_SECRET and x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid secret token")

    body = await req.json()
    message = body.get("message") or body.get("edited_message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    user_text = message.get("text") or ""

    # 2) 節流
    if rate_limited(chat_id):
        await tg_send_text(chat_id, "⚠️ 太頻繁了，稍後再試。")
        return {"ok": True}

    # 3) 18+ 限制：偵測關鍵字或年齡語境直接拒答（再保守也可）
    if violates_age_policy(user_text):
        await tg_send_text(chat_id, "本 Bot 僅供 18 歲以上使用者，未成年相關話題恕不回覆。")
        return {"ok": True}

    # 4) （可選）先做 Moderation，降低違規風險
    try:
        mod = client.moderations.create(model="omni-moderation-latest", input=user_text)
        if mod.results[0].flagged:
            await tg_send_text(chat_id, "⚠️ 該內容不符合安全政策，請換個問法。")
            return {"ok": True}
    except Exception:
        pass  # 容錯：若審查失敗，不影響主流程

    # 5) 呼叫 OpenAI Responses API（核心：模型算力在 OpenAI）
    try:
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
        )
        out = ""
        for item in resp.output or []:
            if item.type == "message":
                for c in item.content:
                    if c.type == "output_text":
                        out += c.text
        if not out.strip():
            out = "（沒有文字輸出）"
        await tg_send_text(chat_id, out.strip())
    except Exception as e:
        await tg_send_text(chat_id, "伺服器暫時忙碌，請稍後再試。")

    return {"ok": True}
