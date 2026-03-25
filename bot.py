import requests
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# ========== CONFIG ==========
BOT_TOKEN = "8661261432:AAEvxdh7IWtt3j6z765_OphNtZZTsFsyiCw"

ADMIN_ID = 8351165824

CHANNEL_USERNAME = "@inffo_01"
CHANNEL_LINK = "https://t.me/inffo_01"

GROUP_USERNAME = "@cineinfo1"
GROUP_LINK = "https://t.me/cineinfo1"

DB_CHANNEL_ID = -1003525179083

NUMBER_API_1 = "https://yash-code-with-ai.alphamovies.workers.dev/"
NUMBER_API_2 = "https://nv2.ek4nsh.in/api?key=3012&mobile="

DB_FILE = "database.json"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
last_update_id = 0

# ========== DATABASE ==========
def load_db():
    if not os.path.exists(DB_FILE):
        return {
            "verified_users": {},
            "pending": {},
            "all_users": []
        }
    return json.load(open(DB_FILE))

def save_db():
    json.dump(db, open(DB_FILE, "w"))

db = load_db()

# ========== TYPING ==========
def send_typing(chat_id):
    try:
        requests.post(BASE_URL + "sendChatAction", data={
            "chat_id": chat_id,
            "action": "typing"
        })
    except:
        pass

# ========== SEND ==========
def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)

    return requests.post(BASE_URL + "sendMessage", data=data)

def edit_message(chat_id, msg_id, text):
    requests.post(BASE_URL + "editMessageText", data={
        "chat_id": chat_id,
        "message_id": msg_id,
        "text": text,
        "parse_mode": "HTML"
    })

# ========== USER ==========
def add_user(user_id):
    uid = str(user_id)
    if uid not in db["all_users"]:
        db["all_users"].append(uid)
        save_db()

# ========== JOIN ==========
def check_join(chat, user_id):
    try:
        res = requests.get(BASE_URL + "getChatMember", params={
            "chat_id": chat,
            "user_id": user_id
        }).json()
        return res["result"]["status"] in ["member","administrator","creator"]
    except:
        return False

def is_joined(user_id):
    return check_join(CHANNEL_USERNAME, user_id) and check_join(GROUP_USERNAME, user_id)

# ========== VERIFY ==========
def is_verified(user_id):
    return str(user_id) in db["verified_users"]

def verify_user(user_id):
    db["verified_users"][str(user_id)] = True
    save_db()

# ========== VERIFY UI ==========
def send_verify_ui(chat_id, user_id, number):
    keyboard = {
        "inline_keyboard": [
            [{"text": "📢 Join Channel", "url": https://t.me/inffo_01}],
            [{"text": "👥 Join Group", "url": https://t.me/cineinfo1}],
            [{"text": "✅ Verify", "callback_data": f"verify_{user_id}"}]
        ]
    }

    db["pending"][str(user_id)] = number
    save_db()

    send_message(chat_id, "🔐 Join channel & group then click verify 👇", keyboard)

# ========== DEV BUTTON ==========
def dev_button():
    return {
        "inline_keyboard": [
            [{"text": "👨‍💻 Contact Developer", "url": "https://t.me/inffo_01"}],
            [{"text": "📢 Join Channel", "url": https://t.me/inffo_01}]
        ]
    }

# ========== API ==========
def get_info(number):
    try:
        res = requests.get(NUMBER_API_1 + "?num=" + number).json()
        if not res.get("data"):
            res = requests.get(NUMBER_API_2 + number).json()
        return res
    except:
        return None

# ========== RESULT ==========
def format_result(data, number):
    records = data.get("data", [])

    if not records:
        return f"❌ No data found for {number}"

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

    return text

# ========== LOG ==========
def log_to_channel(user_id, number, result):
    requests.post(BASE_URL + "sendMessage", data={
        "chat_id": DB_CHANNEL_ID,
        "text": f"User: {user_id}\nNumber: {number}\n\n{result}"
    })

# ========== MAIN ==========
def main():
    global last_update_id

    while True:
        try:
            updates = requests.get(BASE_URL + "getUpdates", params={"offset": last_update_id+1}).json()

            for upd in updates.get("result", []):
                last_update_id = upd["update_id"]

                # VERIFY BUTTON
                if "callback_query" in upd:
                    q = upd["callback_query"]
                    user_id = q["from"]["id"]
                    chat_id = q["message"]["chat"]["id"]
                    msg_id = q["message"]["message_id"]

                    send_typing(chat_id)

                    if is_joined(user_id):
                        verify_user(user_id)
                        edit_message(chat_id, msg_id, "✅ Verified!")

                        number = db["pending"].get(str(user_id))
                        if number:
                            result = format_result(get_info(number), number)
                            send_message(chat_id, result, dev_button())
                            log_to_channel(user_id, number, result)
                    else:
                        send_message(chat_id, "❌ Join first")

                    continue

                if "message" not in upd:
                    continue

                msg = upd["message"]
                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                text = msg.get("text", "")

                add_user(user_id)

                # AUTO VERIFY
                if is_joined(user_id) and not is_verified(user_id):
                    verify_user(user_id)

                if text.startswith("/start"):
                    send_typing(chat_id)
                    send_message(chat_id, "👋 Welcome bro 😊\n\n💎 Premium Number Lookup Bot\n\nUse:\n<code>/num 9876543210</code>")
                    continue

                if text.startswith("/num"):
                    parts = text.split()

                    if len(parts) != 2:
                        send_message(chat_id, "❌ Use: /num 9876543210")
                        continue

                    number = parts[1]
                    send_typing(chat_id)

                    if not is_verified(user_id):
                        if is_joined(user_id):
                            verify_user(user_id)
                        else:
                            send_verify_ui(chat_id, user_id, number)
                            continue

                    result = format_result(get_info(number), number)
                    send_message(chat_id, result, dev_button())
                    log_to_channel(user_id, number, result)

            time.sleep(1)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(3)

# ========== WEB ==========
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Running")

def run_server():
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()

# ========== RUN ==========
if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    main()
