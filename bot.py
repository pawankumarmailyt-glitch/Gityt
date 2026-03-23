import requests
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# ========== CONFIG ==========
BOT_TOKEN = "8661261432:AAEvxdh7IWtt3j6z765_OphNtZZTsFsyiCw"

CHANNEL_USERNAME = "@inffo_01"
CHANNEL_LINK = "https://t.me/inffo_01"

GROUP_USERNAME = "@cineinfo1"
GROUP_LINK = "https://t.me/cineinfo1"

DB_CHANNEL_ID = -1003525179083  # ✅ LOG CHANNEL

DB_FILE = "database.json"

NUMBER_API = "https://nv2.ek4nsh.in/api?key=3012&mobile="
API_KEY = "7189814021"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
last_update_id = 0

# ========== DATABASE ==========
def load_db():
    if not os.path.exists(DB_FILE):
        return {"verified_users": []}
    return json.load(open(DB_FILE))

def save_db():
    json.dump(db, open(DB_FILE, "w"))

db = load_db()

# ========== SEND ==========
def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)

    requests.post(BASE_URL + "sendMessage", data=data)

# ========== LOG TO CHANNEL ==========
def log_to_channel(user_id, username, number, result):
    log = f"""📊 <b>NEW LOOKUP</b>

👤 User ID: {user_id}
📛 Username: @{username if username else 'N/A'}

📞 Number: {number}

📄 Result:
{result}
"""
    requests.post(BASE_URL + "sendMessage", data={
        "chat_id": DB_CHANNEL_ID,
        "text": log,
        "parse_mode": "HTML"
    })

# ========== JOIN CHECK ==========
def check_join(chat_id, user_id):
    try:
        res = requests.get(BASE_URL + "getChatMember", params={
            "chat_id": chat_id,
            "user_id": user_id
        }).json()
        return res["result"]["status"] in ["member","administrator","creator"]
    except:
        return False

def is_joined(user_id):
    return (
        check_join(CHANNEL_USERNAME, user_id) and
        check_join(GROUP_USERNAME, user_id)
    )

# ========== FORCE JOIN UI ==========
def send_force_join(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "📢 Join Channel", "url": CHANNEL_LINK}],
            [{"text": "👥 Join Group", "url": GROUP_LINK}],
            [{"text": "✅ Verify", "callback_data": "verify"}]
        ]
    }

    send_message(chat_id, """🔐 <b>Access Required 😊</b>

💙 Bot use karne ke liye channel aur group join karna zaroori hai

👇 Join karo aur Verify button dabao""", keyboard)

# ========== RESULT ==========
def format_result(data, number):
    records = data.get("data", [])
    if not records:
        return "❌ No data found"

    text = f"✅ <b>Found {len(records)} record(s) for {number}</b>\n\n"

    for i, r in enumerate(records, 1):
        text += f"📍 <b>RESULT #{i}</b>\n"
        text += f"🆔 ID: {r.get('id','N/A')}\n"
        text += f"👤 Name: {r.get('name','N/A')}\n"
        text += f"👨‍💼 Father: {r.get('father_name','N/A')}\n"
        text += f"📞 Mobile: {r.get('mobile','N/A')}\n"
        text += f"📱 Alt: {r.get('alt_mobile','N/A')}\n"
        text += f"🌐 Circle: {r.get('circle','N/A')}\n"
        text += f"🏠 Address: {r.get('address','N/A')}\n"
        text += "━━━━━━━━━━━━━━━━━━━━\n\n"

    text += f"📢 <a href='{CHANNEL_LINK}'>Join Channel</a>"

    return text

# ========== API ==========
def get_info(number):
    try:
        return requests.get(f"{NUMBER_API}?num={number}&key={API_KEY}").json()
    except:
        return None

# ========== MAIN ==========
def main():
    global last_update_id

    while True:
        try:
            updates = requests.get(BASE_URL + "getUpdates", params={"offset": last_update_id + 1}).json()

            if "result" in updates:
                for update in updates["result"]:

                    last_update_id = update["update_id"]

                    # VERIFY BUTTON
                    if "callback_query" in update:
                        query = update["callback_query"]
                        user_id = query["from"]["id"]
                        chat_id = query["message"]["chat"]["id"]

                        if is_joined(user_id):
                            if user_id not in db["verified_users"]:
                                db["verified_users"].append(user_id)
                                save_db()

                            send_message(chat_id, "✅ Verified Successfully 🎉")
                        else:
                            send_message(chat_id, "❌ Please join channel & group first")

                        continue

                    if "message" not in update:
                        continue

                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    user_id = msg["from"]["id"]
                    username = msg["from"].get("username", "")
                    text = msg.get("text", "")

                    # START
                    if text.startswith("/start"):
                        send_message(chat_id, """👋 <b>Welcome 😊</b>

💎 Premium Number Lookup Bot

🔍 Use:
/num 9876543210
""")
                        continue

                    # NUM
                    if text.startswith("/num"):
                        parts = text.split()

                        if len(parts) != 2:
                            send_message(chat_id, "❌ Use: /num 9876543210")
                            continue

                        number = parts[1]

                        if not number.isdigit():
                            send_message(chat_id, "❌ Invalid number")
                            continue

                        if user_id not in db["verified_users"]:
                            send_force_join(chat_id)
                            continue

                        data = get_info(number)

                        if data:
                            result = format_result(data, number)
                            send_message(chat_id, result)

                            # ✅ LOG SAVE
                            log_to_channel(user_id, username, number, result)

                        else:
                            send_message(chat_id, "❌ No data found")

            time.sleep(1.2)

        except Exception as e:
            print("Error:", e)
            time.sleep(3)

# ========== WEB ==========
def run_server():
    HTTPServer(("0.0.0.0", 8080), BaseHTTPRequestHandler).serve_forever()

# ========== RUN ==========
if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    main()
