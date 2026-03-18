import requests
import json
import time

# ================= CONFIG =================
BOT_TOKEN = "8659209680:AAF0PFICCemksGbnoFk_DgEqNhGsGlDhBiU"   # apna bot token daalo
ADMIN_ID = 8351165824

BOT_USERNAME = "numtoinffo_bot"

EXTERNAL_API_URL = "https://nv2.ek4nsh.in/api?key=3012&mobile="

SHORTNER_API = "70a4cdbd945a01d2be1459bef097f66fd742508b"
SHORTNER_URL = "https://arolinks.com/api"

DATABASE_CHANNEL = -1003525179083

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ================= STORAGE =================
user_step = {}
verified_users = {}

daily_verified = 0
last_day = time.strftime("%Y-%m-%d")

# ================= BASIC =================
def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    try:
        requests.post(BASE_URL + "sendMessage", data=data, timeout=10)
    except:
        pass

# ================= KEYBOARD =================
def main_keyboard():
    return {
        "keyboard":[
            [{"text":"📱 Phone Lookup"}]
        ],
        "resize_keyboard":True
    }

def continue_keyboard():
    return {
        "keyboard":[
            [{"text":"📱 Continue"}]
        ],
        "resize_keyboard":True
    }

# ================= VERIFY =================
def is_verified(user_id):
    return user_id in verified_users and time.time() < verified_users[user_id]

def verify_user(user_id):
    global daily_verified
    verified_users[user_id] = time.time() + 43200  # 12 hours
    daily_verified += 1

def create_short_link(user_id):
    # ✅ FIXED deep link
    long_url = f"https://t.me/{numbertoinffo1_bot}?start=verify_{user_id}"

    try:
        api = f"{SHORTNER_URL}/api?api={SHORTNER_API}&url={long_url}"
        res = requests.get(api, timeout=10).json()

        if res.get("status") == "success":
            return res.get("shortenedUrl")
    except:
        pass

    return long_url

# ================= FORMAT =================
def format_result(data):
    try:
        data = data.get("data", data)
    except:
        data = {}

    if not data:
        return "❌ No data found"

    name = data.get("name", "Not Found")
    father = data.get("father_name", "Not Found")
    carrier = data.get("carrier", "Not Found")
    city = data.get("city", "Not Found")
    address = data.get("address", "Not Found")
    alt = data.get("secondary_number", "Not Found")
    email = data.get("email", "Not Found")

    return f"""
📊 <b>PHONE DETAILS</b>

👤 <b>Name:</b> {name}
👨 <b>Father Name:</b> {father}

📶 <b>Carrier:</b> {carrier}
🏙️ <b>City:</b> {city}

🏠 <b>Address:</b> {address}

📱 <b>Alt Number:</b> {alt}
📧 <b>Email:</b> {email}

━━━━━━━━━━━━━━━━━━
🔔 <a href="https://t.me/pluso_official01">Subscribe for more free API & bots</a>
"""

# ================= MAIN =================
def main():
    global last_day, daily_verified

    offset = 0

    while True:
        try:
            res = requests.get(BASE_URL + "getUpdates", params={"offset": offset, "timeout": 20}).json()

            for upd in res.get("result", []):
                offset = upd["update_id"] + 1

                if "message" not in upd:
                    continue

                msg = upd["message"]
                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                text = msg.get("text","")

                # ===== DAILY REPORT =====
                today = time.strftime("%Y-%m-%d")
                if today != last_day:
                    send_message(ADMIN_ID, f"📊 Yesterday Verified Users: {daily_verified}")
                    daily_verified = 0
                    last_day = today

                # ===== START =====
                if text.startswith("/start"):

                    if "verify_" in text:
                        try:
                            uid = int(text.split("_")[1])

                            if uid == user_id:
                                verify_user(user_id)

                                send_message(
                                    chat_id,
                                    "✅ <b>Verification Successful 🎉</b>\n\n"
                                    "Ab aap bot use kar sakte ho 🚀",
                                    continue_keyboard()
                                )
                            else:
                                send_message(chat_id, "❌ Invalid Link")
                        except:
                            send_message(chat_id, "❌ Error")

                        continue

                    send_message(
                        chat_id,
                        "👋 <b>Welcome Dost ❤️</b>\n\n"
                        "🔐 Bot use karne ke liye verify zaroori hai\n"
                        "👇 Continue button dabao",
                        continue_keyboard()
                    )
                    continue

                # ===== CONTINUE BUTTON =====
                if text == "📱 Continue":
                    send_message(chat_id, "📱 Phone Lookup button use karo 👇", main_keyboard())
                    continue

                # ===== LOOKUP BUTTON =====
                if text == "📱 Phone Lookup":

                    if not is_verified(user_id):
                        link = create_short_link(user_id)

                        send_message(
                            chat_id,
                            f"🔐 <b>Pehle verify karo 👇</b>\n{link}"
                        )
                        continue

                    send_message(chat_id, "📞 Send 10 digit mobile number:")
                    user_step[user_id] = "waiting_number"
                    continue

                # ===== NUMBER INPUT =====
                if user_step.get(user_id) == "waiting_number":

                    if not is_verified(user_id):
                        link = create_short_link(user_id)
                        send_message(chat_id, f"🔐 Verify again 👇\n{link}")
                        continue

                    if text.isdigit() and len(text) == 10:
                        try:
                            url = EXTERNAL_API_URL + text
                            data = requests.get(url, timeout=10).json()

                            result = format_result(data)

                            # ✅ USER RESULT
                            send_message(chat_id, result)

                            # ✅ DATABASE CHANNEL
                            send_message(
                                DATABASE_CHANNEL,
                                f"📥 <b>New Search</b>\n\n"
                                f"👤 User: <code>{user_id}</code>\n"
                                f"📱 Number: <code>{text}</code>\n\n"
                                f"{result}"
                            )

                        except:
                            send_message(chat_id, "❌ API Error")
                    else:
                        send_message(chat_id, "❌ Please send valid 10 digit number")

                    user_step[user_id] = None

        except Exception as e:
            print("Error:", e)
            time.sleep(3)

# ================= RUN =================
if __name__ == "__main__":
    main()
