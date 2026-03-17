import requests
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ================= CONFIG =================
BOT_TOKEN = "8633522224:AAHK62_S-flLwbZii5f-tJ4OQcw_zI5qoeA"
BOT_USERNAME = "numtoinffo_bot"

ADMIN_ID = 8351165824

# ✅ CHANNELS (ADDED)
CHANNEL_1 = "@plus_official01"
CHANNEL_2 = "@cinestream01"

CHANNEL_LINK_1 = "https://t.me/plus_official01"
CHANNEL_LINK_2 = "https://t.me/cinestream01"

DATABASE_CHANNEL = -1003525179083

# API
EXTERNAL_API_URL = "https://nv2.ek4nsh.in/api?key=3012&mobile="

# SHORTNER
SHORTNER_API = "70a4cdbd945a01d2be1459bef097f66fd742508b"
SHORTNER_URL = "https://arolinks.com"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ================= STORAGE =================
verified_users = {}

# ================= WEB SERVER =================
def run_web():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot Running")

    server = HTTPServer(("0.0.0.0", 10000), Handler)
    server.serve_forever()

# ================= BASIC =================
def send_message(chat_id, text, buttons=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if buttons:
        data["reply_markup"] = buttons

    requests.post(BASE_URL + "sendMessage", json=data)

# ================= JOIN CHECK =================
def check_join(user_id):
    try:
        r1 = requests.get(BASE_URL + "getChatMember", params={
            "chat_id": CHANNEL_1,
            "user_id": user_id
        }).json()

        r2 = requests.get(BASE_URL + "getChatMember", params={
            "chat_id": CHANNEL_2,
            "user_id": user_id
        }).json()

        s1 = r1["result"]["status"]
        s2 = r2["result"]["status"]

        return s1 in ["member","administrator","creator"] and s2 in ["member","administrator","creator"]
    except:
        return False

# ================= VERIFY =================
def is_verified(user_id):
    return user_id in verified_users and time.time() < verified_users[user_id]

def verify_user(user_id):
    verified_users[user_id] = time.time() + 43200  # 12 hours

def short_link(user_id):
    try:
        link = f"https://t.me/{numtoinffo_bot}?start=verify_{user_id}"
        api = f"{SHORTNER_URL}/api?api={SHORTNER_API}&url={link}"
        res = requests.get(api).json()

        if res.get("status") == "success":
            return res["shortenedUrl"]
        return link
    except:
        return link

# ================= FORMAT =================
def format_data(data):
    try:
        data = data.get("data", data)
    except:
        data = {}

    return f"""
📊 RESULT HERE

👤 Name: {data.get("name","Not Found")}
👨 Father: {data.get("father_name","Not Found")}
📶 Carrier: {data.get("carrier","Not Found")}
🏙️ City: {data.get("city","Not Found")}
🏠 Address: {data.get("address","Not Found")}
📱 Second Number: {data.get("secondary_number","Not Found")}
📧 Gmail: {data.get("email","Not Found")}

━━━━━━━━━━━━━━━━━━
🔔 https://t.me/plus_official01
━━━━━━━━━━━━━━━━━━
"""

# ================= HELP =================
def help_text():
    return """
📖 HOW TO USE BOT

1️⃣ /start dabao  
2️⃣ Dono channel join karo  
3️⃣ Verify link par click karo  
4️⃣ Wapas bot me aao  
5️⃣ 10 digit mobile number bhejo  

📊 Tumhe premium result milega

⚠️ Note:
• Har 12 ghante me verify karna hoga  
• Galat number mat bhejo  

🔔 Updates: https://t.me/plus_official01
"""

# ================= BOT =================
def run_bot():
    offset = 0

    while True:
        try:
            res = requests.get(BASE_URL + "getUpdates", params={"offset": offset}).json()

            for upd in res.get("result", []):
                offset = upd["update_id"] + 1

                if "message" not in upd:
                    continue

                msg = upd["message"]
                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                text = msg.get("text", "")

                # ===== HELP =====
                if text == "/help":
                    send_message(chat_id, help_text())
                    continue

                # ===== START =====
                if text.startswith("/start"):

                    if "verify_" in text:
                        verify_user(user_id)
                        send_message(chat_id, "✅ Verification Successful!\n📱 Ab number bhejo")
                        continue

                    # FORCE JOIN
                    if not check_join(user_id):
                        buttons = {
                            "inline_keyboard": [
                                [{"text": "📢 Join Channel 1", "url": CHANNEL_LINK_1}],
                                [{"text": "📢 Join Channel 2", "url": CHANNEL_LINK_2}]
                            ]
                        }

                        send_message(chat_id, "❌ Pehle dono channels join karo", buttons)
                        continue

                    send_message(chat_id, f"🔐 Verify here:\n{short_link(user_id)}")
                    continue

                # VERIFY CHECK
                if not is_verified(user_id):
                    send_message(chat_id, f"🔐 Verify first:\n{short_link(user_id)}")
                    continue

                # NUMBER INPUT
                if text.isdigit() and len(text) == 10:
                    try:
                        data = requests.get(EXTERNAL_API_URL + text).json()
                        result = format_data(data)

                        send_message(chat_id, result)

                        # SAVE TO CHANNEL
                        send_message(
                            DATABASE_CHANNEL,
                            f"📥 New Search\nUser: {user_id}\nNumber: {text}\n{result}"
                        )

                    except:
                        send_message(chat_id, "❌ API Error")

                else:
                    send_message(chat_id, "❌ Valid 10 digit number bhejo")

        except Exception as e:
            print("Error:", e)

        time.sleep(2)

# ================= RUN =================
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
