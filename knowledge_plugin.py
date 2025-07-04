# knowledge_plugin.py
# 功能：載入外掛知識庫，根據使用者輸入自動提供相關補腦文字（通用知識 + 對話語氣）

import os
import json

# === 預設知識庫路徑（你需放在 /knowledge 目錄）===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UNIVERSAL_PATH = os.path.join(BASE_DIR, "knowledge", "universal_knowledge.json")
CHITCHAT_PATH = os.path.join(BASE_DIR, "knowledge", "chitchat_knowledge.json")

# === 載入兩份知識庫 ===
def load_knowledge():
    try:
        with open(UNIVERSAL_PATH, "r", encoding="utf-8") as f:
            universal = json.load(f)
    except:
        universal = {}

    try:
        with open(CHITCHAT_PATH, "r", encoding="utf-8") as f:
            chitchat = json.load(f)
    except:
        chitchat = {}

    return universal, chitchat

# === 查詢關聯知識（補腦用）===
def get_knowledge_context(user_input):
    context = ""
    universal, chitchat = load_knowledge()

    # 通用知識：查關鍵字
    for keyword, info in universal.items():
        if keyword in user_input:
            context += f"{info}\n"

    # 對話語氣：完全符合的問句（親切補腦）
    for question, answer in chitchat.items():
        if question in user_input:
            context += f"（提示回答風格）{answer}\n"

    return context.strip()
