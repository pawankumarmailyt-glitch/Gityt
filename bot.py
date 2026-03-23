import requests
import json
import time
import os

# ========== CONFIG ==========
BOT_TOKEN = "8661261432:AAEvxdh7IWtt3j6z765_OphNtZZTsFsyiCw"

CHANNEL_USERNAME = "@inffo_01"
CHANNEL_LINK = "https://t.me/inffo_01"

GROUP_USERNAME = "@cineinfo1"
GROUP_LINK = "https://t.me/+fEszI3aXSV4wYzE9"

DB_CHANNEL_ID = -1003525179083

API1 = "https://yash-code-with-ai.alphamovies.workers.dev/"
API1_KEY = "7189814021"

API2 = "https://nv2.ek4nsh.in/api"
API2_KEY = "3012"

DB_FILE = "database.json"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
last_update_id = 0

# ========== DATABASE ==========
def load_db():
    if not os.path.exists(DB_FILE):
        return {"verified_users": [], "pending": {}}
    return json.load(open(DB_FILE))

def save_db():
    json.dump(db, open(DB_FILE, "w"))

db = load_db()

# ========== SEND ==========
def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)

    return requests.post(BASE_URL + "sendMessage", data=data).json()

# ========== EDIT ==========
def edit_message(chat_id, msg_id, text):
    requests.post(BASE_URL + "editMessageText", data={
        "chat_id": chat_id,
        "message_id": msg_id,
        "text": text,
        "parse_mode": "HTML"
    })

# ========== JOIN CHECK ==========
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

# ========== FORCE JOIN UI ==========
def force_join_ui(chat_id, user_id, number):
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

💙 Bot use karne ke liye channel aur group join karo

👇 Join karke Verify dabao""", keyboard)

# ========== API ==========
def fetch_api1(number):
    try:
        r = requests.get(f"{API1}?num={number}&key={API1_KEY}", timeout=5).json()
        return r.get("data")
    except:
        return None

def fetch_api2(number):
    try:
        r = requests.get(f"{API2}?key={API2_KEY}&mobile={number}", timeout=5).json()
        return r.get("data")
    except:
        return None

def get_data(number):
    data = fetch_api1(number)
    if not data:
        data = fetch_api2(number)
    return data

# ========== RESULT (OLD STYLE) ==========
def format_result(data, number):
    if not data:
        return f"❌ No data found for {number}"

    text = f"✅ Found {len(data)} record(s) for {number}:\n\n"

    for i, r in enumerate(data, 1):
        text += f"📍 RESULT #{i}\n"
        text += f"🆔 ID: {r.get('id','N/A')}\n"
        text += f"👤 Name: {r.get('name','N/A')}\n"
        text += f"👨‍💼 Father: {r.get('father_name','N/A')}\n"
        text += f"📞 Mobile: {r.get('mobile','N/A')}\n"
        text += f"📱 Alt: {r.get('alt_mobile','N/A')}\n"
        text += f"🌐 Circle: {r.get('circle','N/A')}\n"
        text += f"🏠 Address: {r.get('address','N/A')}\n"
        text += "━━━━━━━━━━━━━━━━━━━━\n\n"

    text += "🛠 Dev: <a href='https://t.me/inffo_01'>@inffo_01</a>\n"
    text += "👑 Owner: <a href='https://t.me/inffo_01'>@inffo_01</a>\n\n"
    text += "📢 <a href='https://t.me/inffo_01'>Join Channel</a>"

    return text

# ========== LOG ==========
def log_to_channel(user_id, username, number, result):
    requests.post(BASE_URL + "sendMessage", data={
        "chat_id": DB_CHANNEL_ID,
        "text": f"""📊 NEW LOOKUP

👤 {user_id}
📛 @{username if username else 'N/A'}

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
            updates = requests.get(BASE_URL + "getUpdates", params={"offset": last_update_id + 1}).json()

            for upd in updates.get("result", []):

                last_update_id = upd["update_id"]

                # CALLBACK (VERIFY BUTTON)
                if "callback_query" in upd:
                    q = upd["callback_query"]
                    user_id = q["from"]["id"]
                    chat_id = q["message"]["chat"]["id"]
                    msg_id = q["message"]["message_id"]

                    if is_joined(user_id):
                        if user_id not in db["verified_users"]:
                            db["verified_users"].append(user_id)
                            save_db()

                        # remove button
                        edit_message(chat_id, msg_id, "✅ Verified Successfully 🎉")

                        # auto result
                        number = db["pending"].get(str(user_id))
                        if number:
                            data = get_data(number)
                            result = format_result(data, number)
                            send_message(chat_id, result)
                    else:
                        send_message(chat_id, "❌ पहले join करो")

                    continue

                if "message" not in upd:
                    continue

                msg = upd["message"]
                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                username = msg["from"].get("username", "")
                text = msg.get("text", "")

                # START
                if text.startswith("/start"):
                    send_message(chat_id, """👋 <b>Welcome 😊</b>

💎 Premium Number Lookup Bot

🔍 Use:
<code>/num 9876543210</code>

🚀 Fast • Secure • Accurate
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

                    if user_id not in db["verified_users"]:
                        force_join_ui(chat_id, user_id, number)
                        continue

                    data = get_data(number)
                    result = format_result(data, number)

                    send_message(chat_id, result)
                    log_to_channel(user_id, username, number, result)

            time.sleep(1.2)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(3)

# ========== RUN ==========
if __name__ == "__main__":
    main()
