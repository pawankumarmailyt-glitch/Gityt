import requests
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# ========== CONFIG ==========
BOT_TOKEN = "8659209680:AAF0PFICCemksGbnoFk_DgEqNhGsGlDhBiU"
ADMIN_ID = 8351165824
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
            "daily_verified": 0,
            "last_day": time.strftime("%Y-%m-%d"),
            "all_users": []
        }
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

db = load_db()

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
processed_updates = set()

# ========== SEND MESSAGE ==========
def send_message(chat_id, text, reply_to=None):
    url = BASE_URL + "sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
        "reply_markup": json.dumps({"remove_keyboard": True})
    }
    if reply_to:
        data["reply_to_message_id"] = reply_to

    res = requests.post(url, data=data).json()

    # AUTO DELETE AFTER 30s
    if res.get("result"):
        msg_id = res["result"]["message_id"]
        threading.Timer(30, delete_message, args=(chat_id, msg_id)).start()

# ========== DELETE ==========
def delete_message(chat_id, message_id):
    requests.post(BASE_URL + "deleteMessage", data={
        "chat_id": chat_id,
        "message_id": message_id
    })

# ========== USER TRACK ==========
def add_user(user_id):
    user_id = str(user_id)
    if user_id not in db["all_users"]:
        db["all_users"].append(user_id)
        save_db()

# ========== VERIFY ==========
def is_verified(user_id):
    user_id = str(user_id)
    if user_id in db["verified_users"]:
        if time.time() - db["verified_users"][user_id] < 12 * 3600:
            return True
    return False

def verify_user(user_id):
    user_id = str(user_id)
    db["verified_users"][user_id] = time.time()
    db["daily_verified"] += 1
    save_db()

# ========== SHORTNER ==========
def create_link(user_id):
    try:
        url = f"https://{SHORTNER_WEBSITE}/api"
        params = {
            "api": SHORTNER_API_KEY,
            "url": f"https://t.me/numbertoinffo1_bot?start=verify_{user_id}"
        }
        return requests.get(url, params=params).json().get("shortenedUrl")
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

# ========== RESULT FORMAT ==========
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

    text += "🛠 Dev: @plus_king1\n"
    text += "👑 Owner: @cine_info1\n\n"
    text += "📢 Subscribe: https://t.me/plus_official01\n\n"
    text += "🗑 Deleting in 30s..."

    return text

# ========== LOG TO CHANNEL ==========
def log_to_channel(user_id, username, number, result):
    log = f"""📊 NEW LOOKUP

👤 User: {user_id}
📛 Username: @{username if username else 'N/A'}

📞 Number: {number}

📄 Result:
{result}
"""
    requests.post(BASE_URL + "sendMessage", data={
        "chat_id": DB_CHANNEL_ID,
        "text": log
    })

# ========== ADMIN ==========
def handle_admin(chat_id, text):
    if chat_id != ADMIN_ID:
        return False

    if text.startswith("/broadcast"):
        msg = text.replace("/broadcast ", "")
        for user in db["all_users"]:
            send_message(user, msg)
        send_message(chat_id, "✅ Broadcast sent")
        return True

    if text == "/users":
        send_message(chat_id, f"👥 Total Users: {len(db['all_users'])}")
        return True

    if text == "/stats":
        send_message(chat_id, f"📊 Verified Today: {db['daily_verified']}")
        return True

    if text == "/resetverify":
        db["verified_users"] = {}
        save_db()
        send_message(chat_id, "✅ All users reset")
        return True

    return False

# ========== MAIN ==========
def main():
    offset = 0

    while True:
        try:
            updates = requests.get(BASE_URL + "getUpdates", params={"offset": offset}).json()

            if "result" in updates:
                for update in updates["result"]:

                    uid = update["update_id"]

                    if uid in processed_updates:
                        continue

                    processed_updates.add(uid)
                    offset = uid + 1

                    if "message" not in update:
                        continue

                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    user_id = msg["from"]["id"]
                    username = msg["from"].get("username", "")
                    text = msg.get("text", "")
                    msg_id = msg["message_id"]

                    add_user(user_id)

                    # ADMIN
                    if handle_admin(chat_id, text):
                        continue

                    # START
                    if text.startswith("/start"):
                        if "verify_" in text:
                            verify_user(user_id)
                            send_message(chat_id, "✅ Verified 😊", msg_id)
                            continue

                        send_message(chat_id, "👋 Welcome 😊\nUse /num", msg_id)
                        continue

                    # VERIFY
                    if text == "/verify":
                        send_verify(chat_id, user_id)
                        continue

                    # NUM COMMAND
                    if text.startswith("/num"):
                        parts = text.split()

                        if len(parts) != 2:
                            send_message(chat_id, "❌ Use: /num 9876543210", msg_id)
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
                            result = format_result(data, number)
                            send_message(chat_id, result, msg_id)

                            log_to_channel(user_id, username, number, result)

                        else:
                            send_message(chat_id, "❌ API error", msg_id)

            time.sleep(1)

        except Exception as e:
            print("Error:", e)
            time.sleep(3)

# ========== WEB ==========
def run_server():
    server = HTTPServer(("0.0.0.0", 8080), BaseHTTPRequestHandler)
    server.serve_forever()

# ========== RUN ==========
if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    main()
