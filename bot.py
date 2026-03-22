import requests
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ========== CONFIG ==========
BOT_TOKEN = "8659209680:AAF0PFICCemksGbnoFk_DgEqNhGsGlDhBiU"   # <-- apna bot token yaha daalo
ADMIN_ID = 8351165824  # <-- apna Telegram user ID

# APIs
NUMBER_API = "https://yash-code-with-ai.alphamovies.workers.dev/"
API_KEY = "7189814021"

SHORTNER_API_KEY = "70a4cdbd945a01d2be1459bef097f66fd742508b"
SHORTNER_WEBSITE = "arolinks.com"

# Branding
DEV = "@"
OWNER = "@"
CHANNEL = "https://t.me/plus_official01"

# ========== STORAGE ==========
verified_users = {}
daily_verified = 0
last_day = time.strftime("%Y-%m-%d")

# ========== TELEGRAM ==========
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

def send_message(chat_id, text, reply_to=None):
    url = BASE_URL + "sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    if reply_to:
        data["reply_to_message_id"] = reply_to
    requests.post(url, data=data)

def get_updates(offset):
    url = BASE_URL + "getUpdates"
    params = {"timeout": 100, "offset": offset}
    return requests.get(url, params=params).json()

# ========== VERIFY ==========
def is_verified(user_id):
    if user_id in verified_users:
        if time.time() - verified_users[user_id] < 12 * 3600:
            return True
    return False

def verify_user(user_id):
    global daily_verified
    verified_users[user_id] = time.time()
    daily_verified += 1

# ========== SHORTNER ==========
def create_link(user_id):
    try:
        long_url = f"https://t.me/numbertoinffo1_bot?start=verify_{user_id}"
        url = f"https://{SHORTNER_WEBSITE}/api"
        params = {"api": SHORTNER_API_KEY, "url": long_url}
        res = requests.get(url, params=params).json()
        return res.get("shortenedUrl")
    except:
        return None

# ========== VERIFY MESSAGE ==========
def send_verify(chat_id, user_id):
    link = create_link(user_id)

    msg = f"""🔐 Hey 😊  
Bot use karne ke liye ek chhota sa step complete karna hoga.

👇 Verify link:
{link}

📌 How to verify:
1. Link open karo  
2. Shortner task complete karo  
3. Bot me wapas aao  

❤️ Bas ho gaya!
"""
    send_message(chat_id, msg)

# ========== API ==========
def get_info(number):
    try:
        url = f"{NUMBER_API}?num={number}&key={API_KEY}"
        return requests.get(url).json()
    except:
        return None

# ========== FORMAT ==========
def format_result(data, number):
    try:
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

        text += f"🛠 Dev: {DEV}\n"
        text += f"👑 Owner: {OWNER}\n\n"
        text += f"📢 Subscribe: {CHANNEL}"

        return f"<pre>{text}</pre>"
    except:
        return "❌ Error formatting"

# ========== DAILY REPORT ==========
def daily_report():
    global daily_verified, last_day
    today = time.strftime("%Y-%m-%d")

    if today != last_day:
        send_message(ADMIN_ID, f"📊 Daily Report\n\n✅ Verified: {daily_verified}")
        daily_verified = 0
        last_day = today

# ========== WEB SERVER ==========
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Running")

def run_server():
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    server.serve_forever()

# ========== MAIN ==========
def main():
    offset = 0

    while True:
        try:
            daily_report()
            updates = get_updates(offset)

            if "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1

                    if "message" not in update:
                        continue

                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    user_id = msg["from"]["id"]
                    text = msg.get("text", "")
                    msg_id = msg["message_id"]

                    # START
                    if text.startswith("/start"):
                        if "verify_" in text:
                            verify_user(user_id)
                            send_message(chat_id, "✅ Verified 😊", msg_id)
                            continue

                        send_message(chat_id, "👋 Welcome 😊\nUse /help", msg_id)
                        continue

                    # HELP
                    if text == "/help":
                        send_message(chat_id,
                        "📌 Commands:\n"
                        "/num 9876543210\n"
                        "/verify\n"
                        "/help", msg_id)
                        continue

                    # VERIFY
                    if text == "/verify":
                        send_verify(chat_id, user_id)
                        continue

                    # NUM COMMAND
                    if text.startswith("/num"):
                        parts = text.split()

                        if len(parts) != 2:
                            send_message(chat_id, "❌ Use:\n/num 9876543210", msg_id)
                            continue

                        number = parts[1]

                        if not number.isdigit() or len(number) != 10:
                            send_message(chat_id, "❌ Invalid number", msg_id)
                            continue

                        if not is_verified(user_id):
                            send_verify(chat_id, user_id)
                            continue

                        data = get_info(number)

                        if data:
                            send_message(chat_id, format_result(data, number), msg_id)
                        else:
                            send_message(chat_id, "❌ API error", msg_id)

            time.sleep(0.8)

        except Exception as e:
            print("Error:", e)
            time.sleep(3)

# ========== RUN ==========
if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    main()
