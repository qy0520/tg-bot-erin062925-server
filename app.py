#2025 0706 1140

# 引入必要的模組
from flask import Flask, request, jsonify, Response       # Flask 用來建立網頁伺服器與處理請求
from transformers import AutoTokenizer, AutoModelForCausalLM  # Transformers 模組，用來載入模型與分詞器
import torch                                              # PyTorch，用來支援模型運算
import requests                                           # 用來呼叫 Telegram API 發送訊息

# === 初始化 Flask 應用 ===
app = Flask(__name__)  # 建立 Flask 應用實例

# === Telegram 機器人設定 ===
TELEGRAM_TOKEN = "7967078631:AAH9viY8zWZ6mi7krxw1RSz5eycrI9Lce8Q"  # 你的 Telegram bot 的 token
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"  # 發送訊息的 API 端點

# === 載入中文語言模型 ===
model_name = "ckiplab/gpt2-base-chinese"  # 使用 CKIP Lab 提供的中文 GPT-2 模型
tokenizer = AutoTokenizer.from_pretrained(model_name)      # 載入對應的分詞器（Tokenizer）
model = AutoModelForCausalLM.from_pretrained(model_name)   # 載入語言模型本體

# === 回應生成主函數 ===
def generate_reply(prompt):
    # 將使用者輸入文字轉成模型可接受的格式（token IDs）
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)

    # 使用模型生成回應
    outputs = model.generate(
        **inputs,               # 傳入 tokenizer 處理好的輸入資料
        max_new_tokens=40,     # 最多生成 40 個字
        do_sample=True,        # 啟用隨機取樣（比較自然）
        top_k=50,              # 每步僅從機率前 50 名中抽樣（限制選擇範圍）
        top_p=0.95,            # 限制總機率為前 95%（nucleus sampling）
        temperature=0.8,       # 控制回應多樣性（越高越有創意）
        pad_token_id=tokenizer.eos_token_id  # 用結束符號當作 padding
    )

    # 將模型輸出的 token 轉換成文字
    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return reply.strip()  # 去除前後空白後回傳

# === GET 方法，用來測試伺服器是否正常 ===
@app.route("/", methods=["GET"])
def index():
    return Response("✅ Flask server is running and ready to receive Telegram messages!", mimetype="text/plain")

# === Telegram webhook 對應路徑，處理來自 Telegram 的 POST 訊息 ===
@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    data = request.get_json()  # 從 POST 請求中取得 JSON 資料

    # 如果資料格式錯誤，回傳忽略訊息
    if not data or "message" not in data:
        return jsonify({"status": "ignored"}), 200

    message = data["message"]  # 取得使用者的訊息物件
    chat_id = message["chat"]["id"]         # 取得聊天對象的 Telegram ID
    user_text = message.get("text", "")     # 取得使用者傳來的文字內容

    if not user_text:
        return jsonify({"status": "no text"}), 200  # 若沒文字就回覆空訊息

    try:
        # 呼叫模型生成回應
        reply = generate_reply(user_text)
    except Exception as e:
        # 如果模型錯誤，回傳預設錯誤訊息
        reply = "⚠️ 系統錯誤，請稍後再試。"

    # 發送模型回應文字給使用者
    requests.post(TELEGRAM_URL, json={
        "chat_id": chat_id,
        "text": reply
    })

    # 回傳成功狀態給 Telegram（避免它重送訊息）
    return jsonify({"status": "ok"}), 200
