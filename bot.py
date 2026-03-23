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

GROUP_ID = -1003525179083
GROUP_LINK = "https://t.me/+fEszI3aXSV4wYzE9"

DB_CHANNEL_ID = -1003525179083

NUMBER_API = "https://yash-code-with-ai.alphamovies.workers.dev/"
API_KEY = "7189814021"

SHORTNER_API_KEY = "70a4cdbd945a01d2be1459bef097f66fd742508b"
SHORTNER_WEBSITE = "arolinks.com"

DB_FILE = "database.json"

# ========== LOAD DB ==========
def load_db():
    if not os.path.exists(DB_FILE):
        return {
            "verified_users": {},
            "verify_hours": 12,
            "delete_time": 60
        }
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
        "parse_mode": "HTML"
    }).json()

    if res.get("result"):
        msg_id = res["result"]["message_id"]
        threading.Timer(db.get("delete_time",60), delete_message, args=(chat_id, msg_id)).start()

def send_buttons(chat_id, text):
    keyboard = {
        "inline_keyboard": [
            [{"text": "📢 Join Channel", "url": CHANNEL_LINK}],
            [{"text": "👥 Join Group", "url": GROUP_LINK}],
            [{"text": "✅ Verify", "callback_data": "verify"}]
        ]
    }

    requests.post(BASE_URL + "sendMessage", data={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(keyboard)
    })

def delete_message(chat_id, msg_id):
    requests.post(BASE_URL + "deleteMessage", data={
        "chat_id": chat_id,
        "message_id": msg_id
    })

# ========== LOG ==========
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

# ========== JOIN ==========
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

# ========== VERIFY ==========
def is_verified(user_id):
    uid = str(user_id)

    if is_joined(user_id):
        db["verified_users"][uid] = time.time()
        save_db()
        return True

    if uid in db["verified_users"]:
        if time.time() - db["verified_users"][uid] < db["verify_hours"] * 3600:
            return True

    return False

def verify_user(user_id):
    db["verified_users"][str(user_id)] = time.time()
    save_db()

# ========== SHORTNER ==========
def create_link(user_id):
    try:
        return requests.get(f"https://{SHORTNER_WEBSITE}/api", params={
            "api": SHORTNER_API_KEY,
            "url": f"https://t.me/numbertooinfo_bot?start=verify_{user_id}"
        }).json().get("shortenedUrl")
    except:
        return None

def send_verify(chat_id, user_id):
    link = create_link(user_id)

    send_buttons(chat_id, f"""🔐 <b>Verification Required 😊</b>

💙 Bot use karne ke liye verify complete karo

👇 Link:
{link}

✨ Ya verify button dabao
""")

# ========== RESULT (OLD STYLE 🔥) ==========
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

    text += f"📢 <a href='{CHANNEL_LINK}'>Join Channel</a>\n"
    text += f"🗑 Deleting in {db.get('delete_time',60)}s..."

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

                    # CALLBACK
                    if "callback_query" in update:
                        query = update["callback_query"]
                        user_id = query["from"]["id"]
                        chat_id = query["message"]["chat"]["id"]

                        if is_verified(user_id):
                            send_message(chat_id, "✅ Already Verified 😊")
                        else:
                            verify_user(user_id)
                            send_message(chat_id, "✅ Verified Successfully 😊")
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
                        send_message(chat_id, "👋 Welcome 😊\nUse /num 9876543210")
                        continue

                    # NUM
                    if text.startswith("/num"):
                        parts = text.split()

                        if len(parts) != 2:
                            send_message(chat_id, "❌ Use: /num 9876543210")
                            continue

                        number = parts[1]

                        if not is_verified(user_id):
                            send_verify(chat_id, user_id)
                            continue

                        data = get_info(number)

                        if data:
                            result = format_result(data, number)
                            send_message(chat_id, result)

                            # 🔥 SAVE TO CHANNEL
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
if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    main()
