import requests
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# ========== CONFIG ==========
BOT_TOKEN = os.getenv("8661261432:AAEvxdh7IWtt3j6z765_OphNtZZTsFsyiCw")

CHANNEL_USERNAME = "@cineinfo1"
CHANNEL_LINK = "https://t.me/cineinfo1"

GROUP_USERNAME = "@cineinfo1"  # change if needed
GROUP_LINK = "https://t.me/cineinfo1"

DB_CHANNEL_ID = -1003525179083

API1 = "https://yash-code-with-ai.alphamovies.workers.dev/?num="
API2 = "https://nv2.ek4nsh.in/api?key=3012&mobile="

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
last_update_id = None

verified_users = {}
pending = {}

# ========== SAFE ==========
def get(url):
    try:
        return requests.get(url, timeout=10).json()
    except:
        return {}

def post(url, data):
    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass

# ========== SEND ==========
def send(chat, text, kb=None):
    data = {
        "chat_id": chat,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if kb:
        data["reply_markup"] = json.dumps(kb)
    post(BASE_URL + "sendMessage", data)

def typing(chat):
    post(BASE_URL + "sendChatAction", {
        "chat_id": chat,
        "action": "typing"
    })

# ========== DEV ==========
def dev():
    return {
        "inline_keyboard": [
            [{"text": "👨‍💻 Developer", "url": "https://t.me/cineinfo1"}],
            [{"text": "📢 Channel", "url": CHANNEL_LINK}]
        ]
    }

# ========== JOIN ==========
def check(chat, user):
    try:
        r = get(BASE_URL + f"getChatMember?chat_id={chat}&user_id={user}")
        return r["result"]["status"] in ["member","administrator","creator"]
    except:
        return False

def joined(user):
    return check(CHANNEL_USERNAME, user) and check(GROUP_USERNAME, user)

# ========== VERIFY UI ==========
def verify(chat, user, num):
    pending[user] = num
    kb = {
        "inline_keyboard": [
            [{"text": "📢 Join Channel", "url": CHANNEL_LINK}],
            [{"text": "👥 Join Group", "url": GROUP_LINK}],
            [{"text": "✅ Verify", "callback_data": f"v_{user}"}]
        ]
    }
    send(chat, "🔐 Please join channel & group then verify 👇", kb)

# ========== DATA ==========
def parse(d):
    if isinstance(d, list):
        return d
    if "data" in d:
        if isinstance(d["data"], list):
            return d["data"]
        elif isinstance(d["data"], dict):
            return [d["data"]]
    if "name" in d:
        return [d]
    return []

def fetch(num):
    d1 = parse(get(API1 + num))
    if d1:
        return d1
    return parse(get(API2 + num))

# ========== RESULT (OLD STYLE) ==========
def result(data, num):
    if not data:
        return f"❌ No data found for {num}"

    txt = f"✅ Found {len(data)} record(s) for {num}\n\n"

    for i, r in enumerate(data, 1):
        txt += f"📍 RESULT #{i}\n"
        txt += f"🆔 ID: {r.get('id','N/A')}\n"
        txt += f"👤 Name: {r.get('name','N/A')}\n"
        txt += f"👨‍💼 Father: {r.get('father_name','N/A')}\n"
        txt += f"📞 Mobile: {r.get('mobile', num)}\n"
        txt += f"📱 Alt: {r.get('alt_mobile','N/A')}\n"
        txt += f"🌐 Circle: {r.get('circle','N/A')}\n"
        txt += f"🏠 Address: {r.get('address','N/A')}\n"
        txt += "━━━━━━━━━━━━━━\n\n"

    return txt

# ========== MAIN ==========
def main():
    global last_update_id

    while True:
        updates = get(BASE_URL + "getUpdates")

        for u in updates.get("result", []):
            last_update_id = u["update_id"] + 1

            # CALLBACK
            if "callback_query" in u:
                q = u["callback_query"]
                user = q["from"]["id"]
                chat = q["message"]["chat"]["id"]

                if joined(user):
                    verified_users[user] = True
                    num = pending.get(user)

                    if num:
                        typing(chat)
                        send(chat, result(fetch(num), num), dev())
                else:
                    send(chat, "❌ Join first")
                continue

            if "message" not in u:
                continue

            msg = u["message"]
            chat = msg["chat"]["id"]
            user = msg["from"]["id"]
            text = msg.get("text","")

            if text.startswith("/start"):
                send(chat, "👋 Welcome\n\nUse:\n/num 9876543210")
                continue

            if text.startswith("/num"):
                p = text.split()
                if len(p) != 2:
                    send(chat, "❌ Use:\n/num 9876543210")
                    continue

                num = p[1]

                if user not in verified_users:
                    if joined(user):
                        verified_users[user] = True
                    else:
                        verify(chat, user, num)
                        continue

                typing(chat)
                send(chat, result(fetch(num), num), dev())

        time.sleep(1)

# ========== WEB ==========
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Running")

def server():
    HTTPServer(("0.0.0.0", int(os.getenv("PORT", 8080))), Handler).serve_forever()

# ========== RUN ==========
if __name__ == "__main__":
    threading.Thread(target=server).start()
    main()
