from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import requests

# 初始化 Flask 應用
app = Flask(__name__)

# Telegram Bot 設定
TELEGRAM_TOKEN = "7967078631:AAH9viY8zWZ6mi7krxw1RSz5eycrI9Lce8Q"
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# 模型設定（使用輕量中文 GPT2）
model_name = "souljoy/gpt2-small-chinese-cluecorpussmall"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 回應生成函數
def generate_reply(prompt):
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
    return reply.strip()

# 根目錄回應
@app.route("/", methods=["GET"])
def index():
    return "✅ Flask bot is running!"

# Telegram webhook
@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"status": "ignored"}), 200

    message = data["message"]
    chat_id = message["chat"]["id"]
    user_text = message.get("text", "")

    if not user_text:
        return jsonify({"status": "no text"}), 200

    try:
        reply = generate_reply(user_text)
    except Exception:
        reply = "⚠️ 抱歉，我現在有點狀況，請稍後再試。"

    requests.post(TELEGRAM_URL, json={
        "chat_id": chat_id,
        "text": reply
    })

    return jsonify({"status": "ok"}), 200

    if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

