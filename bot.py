import requests
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# ========== CONFIG ==========
BOT_TOKEN = "8661261432:AAEvxdh7IWtt3j6z765_OphNtZZTsFsyiCw"

ADMIN_ID = 8351165824

CHANNEL_LINK = "https://t.me/inffo_01"
CHANNEL_USERNAME = "@inffo_01"

GROUP_ID = -1001234567890
GROUP_LINK = "https://t.me/+fEszI3aXSV4wYzE9"

DB_CHANNEL_ID = -1003525179083

NUMBER_API = "https://yash-code-with-ai.alphamovies.workers.dev/"
API_KEY = "7189814021"

DB_FILE = "database.json"

# ========== LOAD DB ==========
def load_db():
    if not os.path.exists(DB_FILE):
        return {"verified_users": {}}
    return json.load(open(DB_FILE))

def save_db():
    json.dump(db, open(DB_FILE, "w"))

db = load_db()

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
last_update_id = 0

# ========== SEND ==========
def send_message(chat_id, text):
    res = requests.post(BASE_URL + "sendMessage", data={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }).json()

    if res.get("result"):
        msg_id = res["result"]["message_id"]
        threading.Timer(60, delete_message, args=(chat_id, msg_id)).start()

def delete_message(chat_id, msg_id):
    requests.post(BASE_URL + "deleteMessage", data={
        "chat_id": chat_id,
        "message_id": msg_id
    })

# ========== JOIN CHECK ==========
def check_member(chat_id, user_id):
    try:
        res = requests.get(BASE_URL + "getChatMember", params={
            "chat_id": chat_id,
            "user_id": user_id
        }).json()
        return res["result"]["status"] in ["member","administrator","creator"]
    except:
        return False

def is_joined(user_id):
    return check_member(CHANNEL_USERNAME, user_id) and check_member(GROUP_ID, user_id)

# ========== RESULT FORMAT (EXACT STYLE 🔥) ==========
def format_result(data, number):
    records = data.get("data", [])
    if not records:
        return "❌ No data found"

    text = f"✅ Found {len(records)} record(s) for {number}:\n\n"

    for i, r in enumerate(records, 1):
        text += f"📍 RESULT #{i}\n"
        text += f"🆔 ID: {r.get('id','N/A')}\n"
        text += f"👤 Name: {r.get('name','N/A')}\n"
        text += f"👨‍💼 Father: {r.get('father_name','N/A')}\n"
        text += f"📞 Mobile: {r.get('mobile','N/A')}\n"
        text += f"📱 Alt: {r.get('alt_mobile','N/A')}\n"
        text += f"🌐 Circle: {r.get('circle','N/A')}\n"
        text += f"🏠 Address: {r.get('address','N/A')}\n"
        text += "━━━━━━━━━━━━━━━━━━━━\n\n"

    # 👇 DEV / OWNER → CHANNEL
    text += f"🛠 Dev: <a href='{CHANNEL_LINK}'>@inffo_01</a>\n"
    text += f"👑 Owner: <a href='{CHANNEL_LINK}'>@inffo_01</a>\n\n"

    text += "🗑 Deleting in 60s..."

    return text

# ========== API ==========
def get_info(number):
    try:
        return requests.get(f"{NUMBER_API}?num={number}&key={API_KEY}").json()
    except:
        return None

# ========== LOG ==========
def log_to_channel(user_id, username, number, result):
    text = f"""📊 <b>NEW LOOKUP</b>

👤 User: {user_id}
📛 Username: @{username if username else 'N/A'}

📞 Number: {number}

{result}
"""
    requests.post(BASE_URL + "sendMessage", data={
        "chat_id": DB_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    })

# ========== MAIN ==========
def main():
    global last_update_id

    while True:
        try:
            updates = requests.get(BASE_URL + "getUpdates", params={"offset": last_update_id+1}).json()

            if "result" in updates:
                for update in updates["result"]:

                    last_update_id = update["update_id"]

                    if "message" not in update:
                        continue

                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    chat_type = msg["chat"]["type"]
                    user_id = msg["from"]["id"]
                    username = msg["from"].get("username", "")
                    text = msg.get("text", "")

                    # START
                    if text.startswith("/start"):
                        send_message(chat_id, "👋 Welcome 😊\nUse /num 9876543210")
                        continue

                    # NUM
                    if text.startswith("/num"):
                        parts = text.split()

                        if len(parts) != 2:
                            send_message(chat_id, "❌ Use: /num 9876543210")
                            continue

                        number = parts[1]

                        if not number.isdigit() or len(number) != 10:
                            send_message(chat_id, "❌ Invalid number")
                            continue

                        # 🔥 GROUP FIX
                        if chat_type in ["group","supergroup"]:
                            if not is_joined(user_id):
                                send_message(chat_id, f"❌ Join first: {CHANNEL_LINK}")
                                continue

                        data = get_info(number)

                        if data:
                            result = format_result(data, number)
                            send_message(chat_id, result)

                            # SAVE
                            log_to_channel(user_id, username, number, result)

                        else:
                            send_message(chat_id, "❌ No data")

            time.sleep(1.2)

        except Exception as e:
            print(e)
            time.sleep(3)

# ========== WEB ==========
def run_server():
    HTTPServer(("0.0.0.0", 8080), BaseHTTPRequestHandler).serve_forever()

# ========== RUN ==========
if __name
