#2025 0704 1100
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
    # 使用 tokenizer 將輸入字串轉換成模型可接受的 tensor（含 token ids）
    # truncation=True 表示若超過最大長度就截斷
    # max_length=512 為最大長度限制（模型最大可處理的 token 數量）
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)

    # 使用模型生成回覆文字
    outputs = model.generate(
        **inputs,              # 將剛剛轉換好的 inputs 傳入（包含 input_ids 和 attention_mask）
        max_new_tokens=40,     # 限制這次生成最多產出 40 個新 token（避免回應太長或太慢）
        do_sample=True,        # 啟用隨機抽樣（非 deterministic），使回答更自然多變
        top_k=50,              # 限制每一步只從最高機率前 50 個 token 中抽樣（避免品質下降）
        top_p=0.95,            # 使用 nucleus sampling，從累積機率前 95% 的 token 中選擇
        temperature=0.8,       # 控制隨機性：越低越保守，越高越發散，常見值為 0.7～1.0
        pad_token_id=tokenizer.eos_token_id  # 如果模型需要 padding，用 <eos> 作為補足標記
    )

    # 將模型輸出的 token ids 轉換回人類可讀的文字
    # skip_special_tokens=True 表示省略掉像 <pad>、<eos> 這類特殊符號
    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # 移除開頭與結尾的空格或換行後傳回
    return reply.strip()

# === "/" 路徑測試是否正常 ===
@app.route("/", methods=["GET"])
def index():
    return "✅ Flask bot is running!"

# === Telegram Webhook 接收訊息 ===
# 當 Telegram 發送訊息時，會 POST 到這個 /telegram 路徑
@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    # 將接收到的 JSON 請求轉換為 Python 字典
    data = request.get_json()

    # 檢查資料是否為空，或是否包含 "message" 欄位（若沒有就忽略）
    if not data or "message" not in data:
        return jsonify({"status": "ignored"}), 200

    message = data["message"]

    # ✅ ⛔ 若訊息是來自 bot 自己（防止回應自己），就忽略
    if message.get("from", {}).get("is_bot", False):
        return jsonify({"status": "bot message ignored"}), 200

    # 從資料中提取訊息內容與聊天 ID（用於回傳訊息）
    chat_id = message["chat"]["id"]                  # 傳送者的 Telegram ID
    user_text = message.get("text", "")              # 使用者傳來的文字（若沒傳文字，預設空字串）

    # 如果文字是空的（例如貼圖、照片），就跳過
    if not user_text:
        return jsonify({"status": "no text"}), 200

    try:
        # ✅ 顯示「打字中...」提示
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction", json={
            "chat_id": chat_id,
            "action": "typing"        #顯示「輸入中...」
        })

        # 呼叫模型產生回覆
        reply = generate_reply(user_text)

     except Exception:
        # 若模型出錯（例如沒連網、超時），則回覆預設錯誤訊息
        reply = "⚠️ 抱歉，我現在有點狀況，請稍後再試。"


    # 使用 Telegram API 發送回應訊息回給使用者
    requests.post(TELEGRAM_URL, json={
        "chat_id": chat_id,     # 指定回傳目標聊天室
        "text": reply           # 傳送文字訊息
    })

    # 回傳成功狀態給 Telegram（HTTP 200），表示 webhook 接收正常
    return jsonify({"status": "ok"}), 200

# === 啟動伺服器（適用 Render、Heroku 類平台）===
if __name__ == "__main__":
    # 取得 Render 平台注入的 PORT（預設值 10000）
    port = int(os.environ.get("PORT", 10000))
    # 0.0.0.0 允許外部連線進來
    app.run(host="0.0.0.0", port=port)
