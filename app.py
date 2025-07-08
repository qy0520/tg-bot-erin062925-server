#2025 0708 1037

```python
# 引入必要的模組
from flask import Flask, request, jsonify, Response       # Flask 用來建立網頁伺服器與處理請求
from transformers import AutoTokenizer, AutoModelForCausalLM  # Transformers 模組，用來載入模型與分詞器
import torch                                              # PyTorch，支援模型運算
import requests                                           # 用來呼叫 Telegram API 發送訊息
import os                                                # 用於獲取環境變數

# === 初始化 Flask 應用 ===
app = Flask(__name__)  # 建立 Flask 應用實例

# === Telegram 機器人設定 ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # 從環境變數獲取 Telegram bot 的 token
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"  # 發送訊息的 API 端點

# === 載入中文語言模型 ===
model_name = "ckiplab/gpt2-base-chinese"  # 使用 CKIP Lab 提供的中文 GPT-2 模型
tokenizer = AutoTokenizer.from_pretrained(model_name)      # 載入對應的分詞器（Tokenizer）
model = AutoModelForCausalLM.from_pretrained(model_name)   # 載入語言模型本體

# === 回應生成主函數 ===
def generate_reply(prompt):
    """
    根據用戶輸入的提示生成回應

    :param prompt: 使用者輸入的文字
    :return: 模型生成的回應文字
    """
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
    """
    根據 GET 請求顯示伺服器狀態
    
    :return: 伺服器運行狀態
    """
    return Response("✅ Flask server is running and ready to receive Telegram messages!", mimetype="text/plain")

# === Telegram webhook 對應路徑，處理來自 Telegram 的 POST 訊息 ===
@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    """
    處理來自 Telegram 的訊息並生成回應

    :return: 回傳狀態確認
    """
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
    response = requests.post(TELEGRAM_URL, json={
        "chat_id": chat_id,
        "text": reply
    })
    
    # 檢查發送訊息的回應狀態
    if response.status_code != 200:
        print("Failed to send message:", response.json())

    # 回傳成功狀態給 Telegram（避免它重送訊息）
    return jsonify({"status":"ok"}), 200

# === 主程式 ===
if __name__ == "__main__":
    app.run(debug=True)  # 啟動 Flask 應用（debug 模式）
```

### 說明
1. **環境變數**：在程式中使用 `os.getenv("TELEGRAM_TOKEN")` 來獲取 Telegram Bot 的 Token，建議在執行前在環境中設置這個變數。
2. **錯誤處理**：增加了對 Telegram API 回應狀態碼的檢查，以便於發送訊息失敗時的調試。
3. **詳細註解**：對每個函數和重要步驟進行了詳細的註解，讓你能夠理解程式的每個部分及其功能。
