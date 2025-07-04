# app.py（Render 專用，只做 TG webhook 轉發）

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 你的 Hugging Face Space API URL
HF_API_URL = "https://你的-hf-space-url/ask"

# 你的 Telegram Bot Token
TELEGRAM_TOKEN = "7967078631:AAH9viY8zWZ6mi7krxw1RSz5eycrI9Lce8Q"
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

@app.route("/", methods=["GET"])
def index():
    return "✅ Webhook 正常啟動"

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"status": "ignored"}), 200

    message = data["message"]
    chat_id = message["chat"]["id"]
    user_text = message.get("text", "")

    # 呼叫 Hugging Face 模型 API
    try:
        response = requests.post(HF_API_URL, json={"text": user_text})
        result = response.json()
        reply = result.get("reply", "⚠️ 模型沒有回應")
    except:
        reply = "⚠️ 模型服務異常，請稍後再試"

    # 回傳給 Telegram 使用者
    requests.post(TELEGRAM_URL, json={
        "chat_id": chat_id,
        "text": reply
    })

    return jsonify({"status": "ok"}), 200

# Render 上會自動處理啟動，無需加 if __name__ == "__main__"
