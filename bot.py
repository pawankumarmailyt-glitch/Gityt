import requests
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# ========== CONFIG ==========
BOT_TOKEN = ""

ADMIN_ID = 8351165824

CHANNEL_USERNAME = "@inffo_01"
CHANNEL_LINK = "https://t.me/inffo_01"

GROUP_USERNAME = "@your_group_username"
GROUP_LINK = "https://t.me/+fEszI3aXSV4wYzE9"

DB_CHANNEL_ID = -1003525179083

NUMBER_API = "https://yash-code-with-ai.alphamovies.workers.dev/"
API_KEY = "7189814021"

DB_FILE = "database.json"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
last_update_id = 0

# ========== DB ==========
def load_db():
    if not os.path.exists(DB_FILE):
        return {
            "verified_users": {},
            "pending": {},
            "all_users": []
        }
    return json.load(open(DB_FILE))

def save_db():
    json.dump(db, open(DB_FILE, "w"))

db = load_db()

# ========== SEND ==========
def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)

    res = requests.post(BASE_URL + "sendMessage", data=data).json()

    # auto delete after 60 sec
    if res.get("result"):
        msg_id = res["result"]["message_id"]
        threading.Timer(60, delete_message, args=(chat_id, msg_id)).start()

    return res

def delete_message(chat_id, msg_id):
    try:
        requests.post(BASE_URL + "deleteMessage", data={
            "chat_id": chat_id,
            "message_id": msg_id
        })
    except:
        pass

# ========== EDIT ==========
def edit_message(chat_id, msg_id, text):
    requests.post(BASE_URL + "editMessageText", data={
        "chat_id": chat_id,
        "message_id": msg_id,
        "text": text,
        "parse_mode": "HTML"
    })

# ========== USER ==========
def add_user(user_id):
    uid = str(user_id)
    if uid not in db["all_users"]:
        db["all_users"].append(uid)
        save_db()

# ========== JOIN ==========
def check_join(chat, user_id):
    try:
        res = requests.get(BASE_URL + "getChatMember", params={
            "chat_id": chat,
            "user_id": user_id
        }).json()
        return res["result"]["status"] in ["member","administrator","creator"]
    except:
        return False

def is_joined(user_id):
    return check_join(CHANNEL_USERNAME, user_id) and check_join(GROUP_USERNAME, user_id)

# ========== VERIFY ==========
def is_verified(user_id):
    return str(user_id) in db["verified_users"]

def verify_user(user_id):
    db["verified_users"][str(user_id)] = time.time()
    save_db()

# ========== FORCE JOIN UI ==========
def send_verify_ui(chat_id, user_id, number):
    keyboard = {
        "inline_keyboard": [
            [{"text": "📢 Join Channel", "url": CHANNEL_LINK}],
            [{"text": "👥 Join Group", "url": GROUP_LINK}],
            [{"text": "✅ Verify", "callback_data": f"verify_{user_id}"}]
        ]
    }

    db["pending"][str(user_id)] = number
    save_db()

    send_message(chat_id, """🔐 <b>Access Required 😊</b>

💙 Pehle channel & group join karo ❤️

👇 Fir Verify dabao""", keyboard)

# ========== API ==========
def get_info(number):
    try:
        return requests.get(f"{NUMBER_API}?num={number}&key={API_KEY}").json()
    except:
        return None

# ========== RESULT ==========
def format_result(data, number):
    records = data.get("data", [])
    if not records:
        return f"❌ No data found for {number}"

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

    text += f"📢 <a href='{CHANNEL_LINK}'>Join Channel</a>"

    return text

# ========== LOG ==========
def log_to_channel(user_id, number, result):
    requests.post(BASE_URL + "sendMessage", data={
        "chat_id": DB_CHANNEL_ID,
        "text": f"""📊 NEW DATA

👤 {user_id}
📞 {number}

📄 Result:
{result}
""",
        "parse_mode": "HTML"
    })

# ========== MAIN ==========
def main():
    global last_update_id

    while True:
        try:
            updates = requests.get(BASE_URL + "getUpdates", params={"offset": last_update_id+1}).json()

            for upd in updates.get("result", []):

                last_update_id = upd["update_id"]

                # CALLBACK VERIFY
                if "callback_query" in upd:
                    q = upd["callback_query"]
                    user_id = q["from"]["id"]
                    chat_id = q["message"]["chat"]["id"]
                    msg_id = q["message"]["message_id"]

                    if is_joined(user_id):
                        verify_user(user_id)

                        # remove button
                        edit_message(chat_id, msg_id, "✅ Verified Successfully 🎉")

                        # auto result
                        number = db["pending"].get(str(user_id))
                        if number:
                            data = get_info(number)
                            result = format_result(data, number)
                            send_message(chat_id, result)
                            log_to_channel(user_id, number, result)
                    else:
                        send_message(chat_id, "❌ Pehle join karo")

                    continue

                if "message" not in upd:
                    continue

                msg = upd["message"]
                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                text = msg.get("text", "")

                add_user(user_id)

                # AUTO VERIFY DETECT
                if is_joined(user_id) and not is_verified(user_id):
                    verify_user(user_id)

                # START
                if text.startswith("/start"):
                    send_message(chat_id, """👋 <b>Welcome 😊</b>

💎 Premium Number Lookup Bot

🔍 Use:
<code>/num 9876543210</code>
""")
                    continue

                # NUM
                if text.startswith("/num"):
                    parts = text.split()

                    if len(parts) != 2:
                        send_message(chat_id, "❌ Use: /num 9876543210")
                        continue

                    number = parts[1]

                    if not is_verified(user_id):
                        send_verify_ui(chat_id, user_id, number)
                        continue

                    data = get_info(number)
                    result = format_result(data, number)

                    send_message(chat_id, result)
                    log_to_channel(user_id, number, result)

            time.sleep(1.2)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(3)

# ========== RUN ==========
if __name__ == "__main__":
    main()
