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

VERIFY_HOURS = 12
AUTO_DELETE_TIME = 60

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
            "all_users": [],
            "verify_hours": VERIFY_HOURS,
            "delete_time": AUTO_DELETE_TIME
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
def send_message(chat_id, text):
    res = requests.post(BASE_URL + "sendMessage", data={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }).json()

    if res.get("result"):
        msg_id = res["result"]["message_id"]
        delete_time = db.get("delete_time", AUTO_DELETE_TIME)
        threading.Timer(delete_time, delete_message, args=(chat_id, msg_id)).start()

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
        hours = db.get("verify_hours", VERIFY_HOURS)
        if time.time() - db["verified_users"][user_id] < hours * 3600:
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

def send_verify(chat_id, user_id):
    link = create_link(user_id)

    send_message(chat_id, f"""🔐 <b>Verification Required 😊</b>

Bot use karne ke liye ek chhota sa step complete karna hoga.

👇 Verify link:
{link}

📌 Steps:
1. Link open karo  
2. Task complete karo  
3. Bot me wapas aao  

❤️ Done!
""")

# ========== API ==========
def get_info(number):
    try:
        res = requests.get(f"{NUMBER_API}?num={number}&key={API_KEY}").json()
        if not isinstance(res, dict) or "data" not in res:
            return None
        return res
    except:
        return None

# ========== OLD RESULT FORMAT ==========
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
    text += f"🗑 Deleting in {db.get('delete_time',60)}s..."

    return text

# ========== LOG ==========
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

    if text == "/admin":
        send_message(chat_id,
"""⚙️ Admin Panel

/broadcast msg → Send all users  
/users → Total users  
/stats → Daily verified  
/resetverify → Reset verify  

/setverify 6 → Verify time (hours)  
/setdelete 60 → Auto delete (seconds)
""")
        return True

    if text.startswith("/broadcast"):
        msg = text.replace("/broadcast ", "")
        for user in db["all_users"]:
            send_message(user, msg)
        send_message(chat_id, "✅ Broadcast sent")
        return True

    if text == "/users":
        send_message(chat_id, f"👥 Users: {len(db['all_users'])}")
        return True

    if text == "/stats":
        send_message(chat_id, f"📊 Verified Today: {db['daily_verified']}")
        return True

    if text == "/resetverify":
        db["verified_users"] = {}
        save_db()
        send_message(chat_id, "✅ All users reset")
        return True

    if text.startswith("/setverify"):
        try:
            hours = int(text.split()[1])
            db["verify_hours"] = hours
            save_db()
            send_message(chat_id, f"✅ Verify time set to {hours} hours")
        except:
            send_message(chat_id, "❌ Use: /setverify 6")
        return True

    if text.startswith("/setdelete"):
        try:
            sec = int(text.split()[1])
            db["delete_time"] = sec
            save_db()
            send_message(chat_id, f"✅ Delete time set to {sec} sec")
        except:
            send_message(chat_id, "❌ Use: /setdelete 60")
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

                    add_user(user_id)

                    if handle_admin(chat_id, text):
                        continue

                    if text.startswith("/start"):
                        if "verify_" in text:
                            verify_user(user_id)
                            send_message(chat_id, "✅ Verified 😊")
                            continue

                        send_message(chat_id,
"""👋 Hello 😊

Welcome to Phone Lookup Bot 📱

Use:
/num 9876543210

🔐 Verify required before use
""")
                        continue

                    if text == "/verify":
                        send_verify(chat_id, user_id)
                        continue

                    if text.startswith("/num"):
                        parts = text.split()

                        if len(parts) != 2:
                            send_message(chat_id, "❌ Use: /num 9876543210")
                            continue

                        number = parts[1]

                        if not number.isdigit() or len(number) != 10:
                            send_message(chat_id, "❌ Invalid number")
                            continue

                        if not is_verified(user_id):
                            send_verify(chat_id, user_id)
                            continue

                        data = get_info(number)

                        if data:
                            result = format_result(data, number)
                            send_message(chat_id, result)
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
