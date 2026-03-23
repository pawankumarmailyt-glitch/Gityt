import requests
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# ========== CONFIG ==========
BOT_TOKEN = "8661261432:AAEvxdh7IWtt3j6z765_OphNtZZTsFsyiCw"

ADMIN_ID = 8351165824

CHANNEL_LINK = "https://t.me/inffo_01"
GROUP_LINK = "https://t.me/+fEszI3aXSV4wYzE9"
CHANNEL_USERNAME = "@inffo_01"

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
            "all_users": [],
            "verify_hours": 12,
            "delete_time": 60,
            "verify_enabled": True
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
        "parse_mode": "HTML",
        "disable_web_page_preview": False
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

# ========== USER ==========
def add_user(user_id):
    uid = str(user_id)
    if uid not in db["all_users"]:
        db["all_users"].append(uid)
        save_db()

# ========== FORCE JOIN ==========
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
def is_verified(user_id):
    if not db.get("verify_enabled", True):
        return True

    uid = str(user_id)
    if uid in db["verified_users"]:
        if time.time() - db["verified_users"][uid] < db["verify_hours"]*3600:
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

💙 Thoda support karo aur verify complete karo

👇 Link open karo:
{link}

✨ Ya direct verify button dabao

❤️ Thank you!
""")

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
    text += f"📢 <a href='{CHANNEL_LINK}'>Join Channel</a>\n"
    text += f"🗑 Deleting in {db.get('delete_time',60)}s..."

    return text

# ========== ADMIN ==========
def handle_admin(chat_id, text):
    if chat_id != ADMIN_ID:
        return False

    if text == "/admin":
        send_message(chat_id,
"""⚙️ Admin Panel

/verifyon → Enable verify  
/verifyoff → Disable verify  
/setdelete 60 → Delete time  
""")
        return True

    if text == "/verifyoff":
        db["verify_enabled"] = False
        save_db()
        send_message(chat_id, "✅ Verification OFF")
        return True

    if text == "/verifyon":
        db["verify_enabled"] = True
        save_db()
        send_message(chat_id, "✅ Verification ON")
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

                    # CALLBACK BUTTON
                    if "callback_query" in update:
                        query = update["callback_query"]
                        user_id = query["from"]["id"]
                        chat_id = query["message"]["chat"]["id"]

                        if not is_joined(user_id):
                            send_buttons(chat_id, "❌ Pehle join karo 😅")
                        else:
                            verify_user(user_id)
                            send_message(chat_id, "✅ Verified Successfully 😊")
                        continue

                    if "message" not in update:
                        continue

                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    user_id = msg["from"]["id"]
                    text = msg.get("text", "")

                    add_user(user_id)

                    if handle_admin(chat_id, text):
                        continue

                    # FORCE JOIN
                    if not is_joined(user_id):
                        send_buttons(chat_id, """🥺 <b>Oops! Join karna padega...</b>

💙 Pehle channel & group join karo

👇 Buttons use karo

❤️ Fir verify dabao
""")
                        continue

                    # START
                    if text.startswith("/start"):
                        if "verify_" in text:
                            verify_user(user_id)
                            send_message(chat_id, "✅ Verified 😊")
                            continue

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
                            send_message(chat_id, format_result(data, number))
                        else:
                            send_message(chat_id, "❌ No data")

            time.sleep(1.2)

        except Exception as e:
            print(e)
            time.sleep(3)

# ========== API ==========
def get_info(number):
    try:
        return requests.get(f"{NUMBER_API}?num={number}&key={API_KEY}").json()
    except:
        return None

# ========== WEB ==========
def run_server():
    HTTPServer(("0.0.0.0", 8080), BaseHTTPRequestHandler).serve_forever()

# ========== RUN ==========
if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    main()
