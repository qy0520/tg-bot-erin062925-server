#2025 0704 1440
from flask import Flask, request, jsonify  # 建立 API 伺服器與處理 POST/GET 請求
from transformers import AutoTokenizer, AutoModelForCausalLM  # 載入 Hugging Face 的 tokenizer 和模型
from knowledge_plugin import get_knowledge_context  # 補腦插件
import torch  # 深度學習運算
import requests  # 發送訊息給 Telegram
import os  # 取得系統環境變數
import time  # ✅ 加在最上方（與其他 import 並列）

# ✅ 顯示「輸入中...」提示，讓使用者知道機器人有收到訊息
requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction", json={
    "chat_id": chat_id,
    "action": "typing"  # 顯示「輸入中...」
})

time.sleep(1.5)  # ✅ 延遲 1.5 秒，讓「輸入中...」能顯示一段時間


# === 初始化 Flask 伺服器 ===
app = Flask(__name__)

# === Telegram Bot 設定 ===
TELEGRAM_TOKEN = "7967078631:AAH9viY8zWZ6mi7krxw1RSz5eycrI9Lce8Q"
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# === 載入模型與分詞器 ===
model_name = "souljoy/gpt2-small-chinese-cluecorpussmall"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# === 回覆文字生成函數（加入補腦 context）===
def generate_reply(user_text):
    # 🔍 取得補腦 context（外掛知識）
    context = get_knowledge_context(user_text)

    # 建立完整 prompt
    prompt = f"""
你是一個中文 AI 助理，請根據以下背景知識回答問題：

{context}

使用者：{user_text}
機器人：
"""

    # 模型輸入處理
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)

    # 產生回應
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
    reply = reply.strip().split("使用者：")[0]  # ✅ 去掉亂補的下一句

    # 檢查亂碼或過短回答
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

    # ⛔ 避免機器人回自己
    if message.get("from", {}).get("is_bot", False):
        return jsonify({"status": "bot message ignored"}), 200

    chat_id = message["chat"]["id"]
    user_text = message.get("text", "")

    if not user_text:
        return jsonify({"status": "no text"}), 200

    try:
        # ✅ 顯示「輸入中...」
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction", json={
            "chat_id": chat_id,
            "action": "typing"
        })

    try:
    # ✅ 顯示輸入中 + 延遲
        requests.post(...)  ←這段
        time.sleep(1.5)

        reply = generate_reply(user_text)

    except Exception:
        reply = "⚠️ 抱歉，我現在有點狀況，請稍後再試。"

    # 回覆訊息
    requests.post(TELEGRAM_URL, json={
        "chat_id": chat_id,
        "text": reply
    })

    return jsonify({"status": "ok"}), 200

# === 啟動伺服器（Render、Heroku 用）===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

