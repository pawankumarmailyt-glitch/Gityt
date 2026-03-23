import requests
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ========== CONFIG ==========
BOT_TOKEN = "8661261432:AAEvxdh7IWtt3j6z765_OphNtZZTsFsyiCw"

CHANNEL1_USERNAME = "@inffo_01"
CHANNEL1_LINK = "https://t.me/inffo_01"

CHANNEL2_USERNAME = "@inffo_02"
CHANNEL2_LINK = "https://t.me/inffo_02"

GROUP_USERNAME = "@your_group_username"
GROUP_LINK = "https://t.me/+fEszI3aXSV4wYzE9"

NUMBER_API = "https://yash-code-with-ai.alphamovies.workers.dev/"
API_KEY = "7189814021"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
last_update_id = 0

verified_users = {}

# ========== SEND ==========
def send_message(chat_id, text):
    requests.post(BASE_URL + "sendMessage", data={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    })

# ========== FORCE JOIN UI ==========
def send_force_join(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "📢 Join Channel 1", "url": CHANNEL1_LINK}],
            [{"text": "📢 Join Channel 2", "url": CHANNEL2_LINK}],
            [{"text": "👥 Join Group", "url": GROUP_LINK}],
            [{"text": "✅ Verify", "callback_data": "verify"}]
        ]
    }

    requests.post(BASE_URL + "sendMessage", data={
        "chat_id": chat_id,
        "text": """🔐 <b>Access Required 😊</b>

💙 Bot use karne ke liye sab channels aur group join karna hoga

👇 Join karo aur phir Verify button dabao""",
        "parse_mode": "HTML",
        "reply_markup": json.dumps(keyboard)
    })

# ========== CHECK JOIN ==========
def check_member(chat_id, user_id):
    try:
        res = requests.get(BASE_URL + "getChatMember", params={
            "chat_id": chat_id,
            "user_id": user_id
        }).json()
        return res["result"]["status"] in ["member","administrator","creator"]
    except:
        return False

def is_joined_all(user_id):
    return (
        check_member(CHANNEL1_USERNAME, user_id) and
        check_member(CHANNEL2_USERNAME, user_id) and
        check_member(GROUP_USERNAME, user_id)
    )

# ========== RESULT ==========
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

    text += f"📢 <a href='{CHANNEL1_LINK}'>Join Channel</a>\n"
    text += "🗑 Deleting in 60s..."

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
            updates = requests.get(BASE_URL + "getUpdates", params={"offset": last_update_id+1}).json()

            if "result" in updates:
                for update in updates["result"]:

                    last_update_id = update["update_id"]

                    # CALLBACK VERIFY
                    if "callback_query" in update:
                        query = update["callback_query"]
                        user_id = query["from"]["id"]
                        chat_id = query["message"]["chat"]["id"]

                        if is_joined_all(user_id):
                            verified_users[user_id] = True
                            send_message(chat_id, "✅ Verified Successfully 🎉")
                        else:
                            send_message(chat_id, "❌ Please join all channels & group first")

                        continue

                    if "message" not in update:
                        continue

                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    user_id = msg["from"]["id"]
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

                        if user_id not in verified_users:
                            send_force_join(chat_id)
                            continue

                        data = get_info(number)

                        if data:
                            send_message(chat_id, format_result(data, number))
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
if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    main()
