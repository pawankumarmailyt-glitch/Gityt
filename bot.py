import requests
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# ================= CONFIG =================
BOT_TOKEN = os.getenv("8661261432:AAEvxdh7IWtt3j6z765_OphNtZZTsFsyiCw")  # yaha token set karo

CHANNEL_USERNAME = "@cineinfo1"
CHANNEL_LINK = "https://t.me/cineinfo1"

GROUP_USERNAME = "@cineinfo1"  # agar private group hai to -100 id use karo
GROUP_LINK = "https://t.me/cineinfo1"

DB_CHANNEL_ID = -1003525179083

API1 = "https://yash-code-with-ai.alphamovies.workers.dev/?num="
API2 = "https://nv2.ek4nsh.in/api?key=3012&mobile="

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

last_update_id = 0
verified_users = {}
pending = {}

# ================= SAFE REQUEST =================
def safe_get(url, params=None):
    try:
        return requests.get(url, params=params, timeout=10).json()
    except:
        return {}

def safe_post(method, data=None):
    try:
        requests.post(BASE_URL + method, data=data, timeout=10)
    except:
        pass

# ================= TELEGRAM =================
def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)

    safe_post("sendMessage", data)

def send_typing(chat_id):
    safe_post("sendChatAction", {
        "chat_id": chat_id,
        "action": "typing"
    })

# ================= BUTTON =================
def dev_button():
    return {
        "inline_keyboard": [
            [{"text": "👨‍💻 Developer", "url": "https://t.me/cineinfo1"}],
            [{"text": "📢 Channel", "url": CHANNEL_LINK}]
        ]
    }

# ================= JOIN CHECK =================
def check_join(chat, user):
    try:
        res = safe_get(BASE_URL + "getChatMember", {
            "chat_id": chat,
            "user_id": user
        })
        return res["result"]["status"] in ["member", "administrator", "creator"]
    except:
        return False

def is_joined(user):
    return check_join(CHANNEL_USERNAME, user) and check_join(GROUP_USERNAME, user)

# ================= VERIFY UI =================
def verify_ui(chat_id, user_id, number):
    pending[user_id] = number

    keyboard = {
        "inline_keyboard": [
            [{"text": "📢 Join Channel", "url": CHANNEL_LINK}],
            [{"text": "👥 Join Group", "url": GROUP_LINK}],
            [{"text": "✅ Verify", "callback_data": f"verify_{user_id}"}]
        ]
    }

    send_message(chat_id, "🔐 Please join channel & group then click verify 👇", keyboard)

# ================= DATA PARSER =================
def parse_data(res):
    if isinstance(res, list):
        return res

    if "data" in res:
        if isinstance(res["data"], list):
            return res["data"]
        elif isinstance(res["data"], dict):
            return [res["data"]]

    if "name" in res:
        return [res]

    return []

# ================= FETCH =================
def fetch_data(number):
    res1 = parse_data(safe_get(API1 + number))
    if res1:
        return res1

    res2 = parse_data(safe_get(API2 + number))
    return res2

# ================= RESULT =================
def format_result(data, number):
    if not data:
        return f"❌ No data found for {number}"

    text = f"✅ Found {len(data)} record(s) for {number}\n\n"

    for i, r in enumerate(data, 1):
        text += f"📍 RESULT #{i}\n"
        text += f"🆔 ID: {r.get('id','N/A')}\n"
        text += f"👤 Name: {r.get('name','N/A')}\n"
        text += f"👨‍💼 Father: {r.get('father_name','N/A')}\n"
        text += f"📞 Mobile: {r.get('mobile', number)}\n"
        text += f"📱 Alt: {r.get('alt_mobile','N/A')}\n"
        text += f"🌐 Circle: {r.get('circle','N/A')}\n"
        text += f"🏠 Address: {r.get('address','N/A')}\n"
        text += "━━━━━━━━━━━━━━\n\n"

    return text

# ================= DB SAVE =================
def save_to_db(user_id, number, result):
    try:
        text = f"📥 New Search\n\n👤 User: {user_id}\n📞 Number: {number}\n\n{result}"
        send_message(DB_CHANNEL_ID, text)
    except:
        pass

# ================= MAIN =================
def main():
    global last_update_id

    while True:
        updates = safe_get(BASE_URL + "getUpdates", {
            "offset": last_update_id,
            "timeout": 20
        })

        for upd in updates.get("result", []):
            last_update_id = upd["update_id"] + 1

            # ===== CALLBACK =====
            if "callback_query" in upd:
                q = upd["callback_query"]
                user_id = q["from"]["id"]
                chat_id = q["message"]["chat"]["id"]

                if is_joined(user_id):
                    verified_users[user_id] = True
                    number = pending.get(user_id)

                    if number:
                        send_typing(chat_id)
                        result = format_result(fetch_data(number), number)
                        send_message(chat_id, result, dev_button())
                        save_to_db(user_id, number, result)
                else:
                    send_message(chat_id, "❌ Please join first")
                continue

            # ===== MESSAGE =====
            if "message" not in upd:
                continue

            msg = upd["message"]
            chat_id = msg["chat"]["id"]
            user_id = msg["from"]["id"]
            text = msg.get("text", "")

            if text.startswith("/start"):
                send_message(chat_id, "👋 Welcome 😊\n\nUse:\n/num 9876543210")
                continue

            if text.startswith("/num"):
                parts = text.split()

                if len(parts) != 2:
                    send_message(chat_id, "❌ Use: /num 9876543210")
                    continue

                number = parts[1]

                # ===== VERIFY SYSTEM =====
                if user_id not in verified_users:
                    if is_joined(user_id):
                        verified_users[user_id] = True
                    else:
                        verify_ui(chat_id, user_id, number)
                        continue

                send_typing(chat_id)
                result = format_result(fetch_data(number), number)
                send_message(chat_id, result, dev_button())
                save_to_db(user_id, number, result)

        time.sleep(1)

# ================= WEB SERVER =================
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Running")

def run_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

# ================= RUN =================
if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    main()
