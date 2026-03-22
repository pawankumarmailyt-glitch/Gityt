import requests
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# ========== CONFIG ==========
BOT_TOKEN = "8661261432:AAEvxdh7IWtt3j6z765_OphNtZZTsFsyiCw"

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

# 🔥 duplicate fix
last_update_id = 0

# ========== SEND ==========
def send_message(chat_id, text):
    res = requests.post(BASE_URL + "sendMessage", data={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }).json()

    if res.get("result"):
        msg_id = res["result"]["message_id"]
        threading.Timer(db.get("delete_time",60), delete_message, args=(chat_id, msg_id)).start()

def delete_message(chat_id, message_id):
    requests.post(BASE_URL + "deleteMessage", data={
        "chat_id": chat_id,
        "message_id": message_id
    })

# ========== USER ==========
def add_user(user_id):
    user_id = str(user_id)
    if user_id not in db["all_users"]:
        db["all_users"].append(user_id)
        save_db()

# ========== VERIFY ==========
def is_verified(user_id):
    user_id = str(user_id)
    if user_id in db["verified_users"]:
        if time.time() - db["verified_users"][user_id] < db.get("verify_hours",12)*3600:
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
            "url": f"https://t.me/numbertooinfo_bot?start=verify_{user_id}"
        }
        return requests.get(url, params=params).json().get("shortenedUrl")
    except:
        return None

def send_verify(chat_id, user_id):
    link = create_link(user_id)

    send_message(chat_id, f"""🔐 Verification Required 😊

👇 Verify Link:
{link}

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

    text += "\n━━━━━━━━━━━━━━━━━━━━\n\n"

    text += "🛠 Dev: <a href='https://t.me/'>@plus_official01</a>\n"
    text += "👑 Owner: <a href='https://t.me/'>@plus_official01</a>\n\n"

    text += f"🗑 Deleting in {db.get('delete_time',60)}s..."

    return text

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

/setverify 6 → Verify time  
/setdelete 60 → Delete time  
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
        send_message(chat_id, f"📊 Verified: {db['daily_verified']}")
        return True

    if text == "/resetverify":
        db["verified_users"] = {}
        save_db()
        send_message(chat_id, "✅ Reset done")
        return True

    if text.startswith("/setverify"):
        try:
            hours = int(text.split()[1])
            db["verify_hours"] = hours
            save_db()
            send_message(chat_id, f"✅ Verify: {hours}h")
        except:
            send_message(chat_id, "❌ Use: /setverify 6")
        return True

    if text.startswith("/setdelete"):
        try:
            sec = int(text.split()[1])
            db["delete_time"] = sec
            save_db()
            send_message(chat_id, f"✅ Delete: {sec}s")
        except:
            send_message(chat_id, "❌ Use: /setdelete 60")
        return True

    return False

# ========== MAIN ==========
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
                    user_id = msg["from"]["id"]
                    text = msg.get("text", "")

                    add_user(user_id)

                    # ADMIN
                    if handle_admin(chat_id, text):
                        continue

                    # START
                    if text.startswith("/start"):
                        if "verify_" in text:
                            verify_user(user_id)
                            send_message(chat_id, "✅ Verified 😊")
                            continue

                        send_message(chat_id, "👋 Welcome\nUse /num 9876543210")
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
                            send_message(chat_id, format_result(data, number))
                        else:
                            send_message(chat_id, "❌ No data")

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
