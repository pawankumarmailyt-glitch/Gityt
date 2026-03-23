import requests
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# ========= CONFIG =========
BOT_TOKEN = "8661261432:AAEvxdh7IWtt3j6z765_OphNtZZTsFsyiCw"

CHANNEL_LINK = "https://t.me/inffo_01"
CHANNEL_USERNAME = "@inffo_01"

GROUP_ID = -1001234567890

DB_CHANNEL_ID = -1003525179083

NUMBER_API = "https://yash-code-with-ai.alphamovies.workers.dev/"
API_KEY = "7189814021"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
last_update_id = 0

# ========= SEND =========
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

# ========= JOIN CHECK =========
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

# ========= PREMIUM RESULT =========
def format_result(data, number):
    records = data.get("data", [])
    if not records:
        return "❌ <b>No data found</b>"

    text = f"✅ <b>Found {len(records)} record(s) for {number}</b>\n\n"

    for i, r in enumerate(records, 1):
        text += "━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📍 <b>RESULT #{i}</b>\n\n"
        text += f"🆔 <b>ID:</b> {r.get('id','N/A')}\n"
        text += f"👤 <b>Name:</b> {r.get('name','N/A')}\n"
        text += f"👨‍💼 <b>Father:</b> {r.get('father_name','N/A')}\n"
        text += f"📞 <b>Mobile:</b> <code>{r.get('mobile','N/A')}</code>\n"
        text += f"📱 <b>Alt:</b> {r.get('alt_mobile','N/A')}\n"
        text += f"🌐 <b>Circle:</b> {r.get('circle','N/A')}\n"
        text += f"🏠 <b>Address:</b>\n{r.get('address','N/A')}\n\n"

    text += "━━━━━━━━━━━━━━━━━━━━\n"
    text += f"📢 <a href='{CHANNEL_LINK}'>Join for more updates</a>\n\n"
    text += "🗑 <i>Deleting in 60 seconds...</i>"

    return text

# ========= API =========
def get_info(number):
    try:
        return requests.get(f"{NUMBER_API}?num={number}&key={API_KEY}").json()
    except:
        return None

# ========= LOG =========
def log_to_channel(user_id, username, number, result):
    log = f"""📊 <b>NEW LOOKUP</b>

👤 User: {user_id}
📛 Username: @{username if username else 'N/A'}

📞 Number: {number}

{result}
"""
    requests.post(BASE_URL + "sendMessage", data={
        "chat_id": DB_CHANNEL_ID,
        "text": log,
        "parse_mode": "HTML"
    })

# ========= MAIN =========
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
                        send_message(chat_id, """👋 <b>Welcome to Premium Number Lookup Bot</b> 💎

✨ Fast • Accurate • Secure

🔍 Use command:
<code>/num 9876543210</code>

💙 Enjoy premium experience!
""")
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

                        # GROUP JOIN CHECK
                        if chat_type in ["group","supergroup"]:
                            if not is_joined(user_id):
                                send_message(chat_id, f"❌ Please join first:\n{CHANNEL_LINK}")
                                continue

                        data = get_info(number)

                        if data:
                            result = format_result(data, number)
                            send_message(chat_id, result)
                            log_to_channel(user_id, username, number, result)
                        else:
                            send_message(chat_id, "❌ API Error")

            time.sleep(1.2)

        except Exception as e:
            print("Error:", e)
            time.sleep(3)

# ========= WEB =========
def run_server():
    HTTPServer(("0.0.0.0", 8080), BaseHTTPRequestHandler).serve_forever()

# ========= RUN =========
if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    main()
