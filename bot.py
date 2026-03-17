import requests
import json
import time

# ================= CONFIG =================
BOT_TOKEN = "70a4cdbd945a01d2be1459bef097f66fd742508b"
ADMIN_ID = 8351165824  # apna Telegram ID

# ✅ Number Info API
EXTERNAL_API_URL = "https://nv2.ek4nsh.in/api?key=3012&mobile="

# ✅ Arolinks Shortner
SHORTNER_API = "70a4cdbd945a01d2be1459bef097f66fd742508b"
SHORTNER_URL = "https://arolinks.com/api"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ================= STORAGE =================
user_states = {}
verified_users = {}
daily_stats = {}

# ================= BASIC FUNCTIONS =================

def send_message(chat_id, text, keyboard=None):
    url = BASE_URL + "sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if keyboard:
        payload["reply_markup"] = json.dumps(keyboard)

    requests.post(url, data=payload)


def get_updates(offset):
    url = BASE_URL + "getUpdates"
    params = {"timeout": 25, "offset": offset}
    return requests.get(url, params=params).json()


def main_keyboard():
    return {
        "keyboard": [["📱 Phone Lookup"]],
        "resize_keyboard": True
    }

# ================= VERIFICATION =================

def is_verified(user_id):
    return user_id in verified_users and time.time() < verified_users[user_id]


def verify_user(user_id):
    verified_users[user_id] = time.time() + 43200  # 12 hours

    today = time.strftime("%Y-%m-%d")
    if today not in daily_stats:
        daily_stats[today] = set()

    daily_stats[today].add(user_id)


def generate_short_link(user_id):
    long_url = f"https://t.me/?start=verify_{user_id}"

    try:
        api = f"{SHORTNER_URL}/api?api={SHORTNER_API}&url={long_url}"
        res = requests.get(api).json()

        if res.get("status") == "success":
            return res.get("shortenedUrl")
        else:
            return long_url
    except:
        return long_url

# ================= FORMAT RESULT =================

def format_result(data):
    data = data.get("data", data)

    name = data.get("name", "Not Found")
    father = data.get("father_name", "Not Found")
    carrier = data.get("carrier", "Not Found")
    city = data.get("city", "Not Found")
    address = data.get("address", "Not Found")
    alt = data.get("secondary_number", "Not Found")
    email = data.get("email", "Not Found")

    return f"""
╔══════════════════════╗
        📊 RESULT HERE
╚══════════════════════╝

👤 Name: {name}
👨‍👦 Father Name: {father}

📶 Carrier: {carrier}
🏙️ City: {city}

🏠 Address: {address}

📱 Second Number: {alt}
📧 Gmail: {email}

━━━━━━━━━━━━━━━━━━━━━━
🔔 Subscribe:
https://t.me/plus_official01
━━━━━━━━━━━━━━━━━━━━━━
"""

# ================= DAILY REPORT =================

def send_report():
    today = time.strftime("%Y-%m-%d")
    if today in daily_stats:
        count = len(daily_stats[today])
        send_message(ADMIN_ID, f"📊 Daily Verified Users: {count}")
        daily_stats[today] = set()

# ================= MAIN BOT =================

def main():
    offset = 0
    last_day = time.strftime("%d")

    while True:
        updates = get_updates(offset)

        if updates.get("ok"):
            for upd in updates["result"]:
                offset = upd["update_id"] + 1

                if "message" not in upd:
                    continue

                msg = upd["message"]
                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                text = msg.get("text", "")

                # ===== START =====
                if text.startswith("/start"):

                    # Verify लिंक
                    if "verify_" in text:
                        try:
                            uid = int(text.split("_")[1])
                            if uid == user_id:
                                verify_user(user_id)
                                send_message(chat_id, "✅ Verification Done!", main_keyboard())
                            else:
                                send_message(chat_id, "❌ Invalid Link")
                        except:
                            send_message(chat_id, "❌ Error")
                        continue

                    send_message(chat_id, "👋 Welcome\nClick below:", main_keyboard())
                    continue

                # ===== VERIFY CHECK =====
                if not is_verified(user_id):
                    link = generate_short_link(user_id)
                    send_message(chat_id, f"🔒 Verify first:\n{link}")
                    continue

                # ===== BUTTON =====
                if text == "📱 Phone Lookup":
                    user_states[user_id] = "WAIT"
                    send_message(chat_id, "📞 Send 10 digit number:")
                    continue

                # ===== NUMBER INPUT =====
                if user_states.get(user_id) == "WAIT":

                    if text.isdigit() and len(text) == 10:
                        try:
                            api_url = EXTERNAL_API_URL + text
                            res = requests.get(api_url).json()

                            send_message(chat_id, format_result(res))

                        except:
                            send_message(chat_id, "❌ API Error")

                    else:
                        send_message(chat_id, "❌ Invalid Number")

                    user_states[user_id] = None

        # ===== DAILY REPORT =====
        if time.strftime("%d") != last_day:
            send_report()
            last_day = time.strftime("%d")

        time.sleep(2)

# ================= RUN =================
if __name__ == "__main__":
    main()            formatted_text = format_data(res)
                            send_message(chat_id, formatted_text)

                        except:
                            send_message(chat_id, "❌ API Error")

                    else:
                        send_message(chat_id, "❌ Invalid number")

                    user_states[user_id] = None

        # ===== DAILY REPORT =====
        current_day = time.strftime("%d")
        if current_day != last_day:
            send_daily_report()
            last_day = current_day

        time.sleep(2)


# ================= RUN =================
if __name__ == "__main__":
    main()