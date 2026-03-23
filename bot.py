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

DB_CHANNEL_ID = -1003525179083

NUMBER_API = "https://yash-code-with-ai.alphamovies.workers.dev/"
API_KEY = "7189814021"

SHORTNER_API_KEY = "70a4cdbd945a01d2be1459bef097f66fd742508b"
SHORTNER_WEBSITE = "arolinks.com"

DB_FILE = "database.json"

# ========== LOAD DATABASE ==========
def load_db():
    if not os.path.exists(DB_FILE):
        return {
            "verified_users": {},
            "all_users": [],
            "verify_mode": "join",
            "delete_time": 60
        }
    return json.load(open(DB_FILE))

def save_db():
    json.dump(db, open(DB_FILE, "w"))

db = load_db()

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
last_update_id = 0

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
        threading.Timer(db.get("delete_time",60), delete_message, args=(chat_id, msg_id)).start()

def delete_message(chat_id, msg_id):
    try:
        requests.post(BASE_URL + "deleteMessage", data={
            "chat_id": chat_id,
            "message_id": msg_id
        })
    except:
        pass

# ========== USER ==========
def add_user(user_id):
    uid = str(user_id)
    if uid not in db["all_users"]:
        db["all_users"].append(uid)
        save_db()

# ========== JOIN CHECK ==========
def is_joined(user_id):
    try:
        res = requests.get(BASE_URL + "getChatMember", params={
            "chat_id": CHANNEL_USERNAME,
            "user_id": user_id
        }).json()
        return res["result"]["status"] in ["member","administrator","creator"]
    except:
        return False

# ========== VERIFY ==========
def is_verified(user_id, chat_type):
    mode = db.get("verify_mode","join")

    if mode == "off":
        return True

    if chat_type in ["group","supergroup"]:
        return is_joined(user_id)

    if mode == "join":
        return is_joined(user_id)

    if mode == "shortner":
        if is_joined(user_id):
            return True
        return str(user_id) in db["verified_users"]

    return False

def verify_user(user_id):
    db["verified_users"][str(user_id)] = True
    save_db()

# ========== SHORTNER ==========
def create_link(user_id):
    try:
        res = requests.get(f"https://{SHORTNER_WEBSITE}/api", params={
            "api": SHORTNER_API_KEY,
            "url": f"https://t.me/?start=verify_{user_id}"
        }).json()
        return res.get("shortenedUrl")
    except:
        return None

def send_verify(chat_id, user_id):
    mode = db.get("verify_mode")

    if mode == "join":
        send_message(chat_id, f"""🔐 <b>Join Required 😊</b>

👉 Please join our channel first:
{CHANNEL_LINK}

❤️ Then try again""")
        return

    if mode == "shortner":
        link = create_link(user_id)
        send_message(chat_id, f"""🔐 <b>Verification Required 😊</b>

👇 Complete this step:
{link}

1. Open link  
2. Complete task  
3. Come back  

❤️ Done!""")

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

    text = f"✅ <b>Found {len(records)} record(s) for {number}</b>\n\n"

    for i, r in enumerate(records, 1):
        text += f"📍 <b>RESULT #{i}</b>\n"
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

# ========== ADMIN ==========
def handle_admin(chat_id, text):
    if chat_id != ADMIN_ID:
        return False

    if text == "/admin":
        send_message(chat_id,
"""⚙️ <b>Admin Panel</b>

/verifyjoin → join only  
/verifyshortner → shortner  
/verifyoff → disable verify  

/setdelete 60 → delete time  
/users → total users  
""")
        return True

    if text == "/verifyjoin":
        db["verify_mode"] = "join"
        save_db()
        send_message(chat_id, "✅ Join verification ON")
        return True

    if text == "/verifyshortner":
        db["verify_mode"] = "shortner"
        save_db()
        send_message(chat_id, "✅ Shortner verification ON")
        return True

    if text == "/verifyoff":
        db["verify_mode"] = "off"
        save_db()
        send_message(chat_id, "✅ Verification OFF")
        return True

    if text.startswith("/setdelete"):
        try:
            sec = int(text.split()[1])
            db["delete_time"] = sec
            save_db()
            send_message(chat_id, f"✅ Delete time: {sec}s")
        except:
            send_message(chat_id, "❌ Use: /setdelete 60")
        return True

    if text == "/users":
        send_message(chat_id, f"👥 Users: {len(db['all_users'])}")
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
                    chat_type = msg["chat"]["type"]
                    user_id = msg["from"]["id"]
                    text = msg.get("text", "")

                    add_user(user_id)

                    if handle_admin(chat_id, text):
                        continue

                    if text.startswith("/start"):
                        send_message(chat_id,
"""👋 <b>Welcome 😊</b>

💎 Premium Number Lookup Bot

🔍 Use:
/num 9876543210

🚀 Fast • Accurate • Secure
""")
                        continue

                    if text.startswith("/num"):
                        parts = text.split()

                        if len(parts) != 2:
                            send_message(chat_id, "❌ Use: /num 9876543210")
                            continue

                        number = parts[1]

                        if not number.isdigit():
                            send_message(chat_id, "❌ Invalid number")
                            continue

                        if not is_verified(user_id, chat_type):
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
