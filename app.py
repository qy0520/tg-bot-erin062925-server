#2025 0704 1350
from flask import Flask, request, jsonify             # 建立 API 伺服器與處理 POST/GET 請求
from transformers import AutoTokenizer, AutoModelForCausalLM  # 載入 Hugging Face 的 tokenizer 和模型
import torch                                           # 深度學習運算
import requests                                        # 發送訊息給 Telegram
import os                                              # 取得系統環境變數

# === 初始化 Flask 伺服器 ===
app = Flask(__name__)

# === Telegram Bot 設定 ===
TELEGRAM_TOKEN = "7967078631:AAH9viY8zWZ6mi7krxw1RSz5eycrI9Lce8Q"
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# === 載入模型與分詞器 ===
model_name = "souljoy/gpt2-small-chinese-cluecorpussmall"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# === 回覆文字生成函數 ===
def generate_reply(prompt):
    prompt = f"使用者：{prompt}\n機器人："  # ✅ 加入對話上下文提示詞，讓模型知道要扮演回應角色
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)

    outputs = model.generate(
        **inputs,
        max_new_tokens=40,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.8,
        pad_token_id=tokenizer.eos_token_id
    )

    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)
    reply = reply.strip().split("使用者：")[0]  # ✅ 去除模型自己補的下一句

    if len(reply) < 2 or reply.count("？") > 3:
        reply = "🤖 我還在學習中，可能不太理解這個問題..."

    return reply.strip()

# === "/" 路徑測試是否正常 ===
@app.route("/", methods=["GET"])
def index():
    return "✅ Flask bot is running!"

# === Telegram Webhook 接收訊息 ===
@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"status": "ignored"}), 200

    message = data["message"]

    if message.get("from", {}).get("is_bot", False):
        return jsonify({"status": "bot message ignored"}), 200

    chat_id = message["chat"]["id"]
    user_text = message.get("text", "")

    if not user_text:
        return jsonify({"status": "no text"}), 200

    try:
        # ✅ 顯示「打字中...」提示
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction", json={
            "chat_id": chat_id,
            "action": "typing"
        })

        reply = generate_reply(user_text)

    except Exception:
        reply = "⚠️ 抱歉，我現在有點狀況，請稍後再試。"

    requests.post(TELEGRAM_URL, json={
        "chat_id": chat_id,
        "text": reply
    })

    return jsonify({"status": "ok"}), 200

# === 啟動伺服器（適用 Render、Heroku 類平台）===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
