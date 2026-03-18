import requests
import json
import time

# ================= CONFIG =================
BOT_TOKEN = "8659209680:AAF0PFICCemksGbnoFk_DgEqNhGsGlDhBiU"   # 👈 apna token daalo
ADMIN_ID = 8351165824

BOT_USERNAME = "numbertoinffo1_bot"

EXTERNAL_API_URL = "https://nv2.ek4nsh.in/api?key=3012&mobile="

SHORTNER_API = "70a4cdbd945a01d2be1459bef097f66fd742508b"
SHORTNER_URL = "https://arolinks.com/api"

DATABASE_CHANNEL = -1003525179083

BASE_URL = f"https://api.telegram.org/bot{8659209680:AAF0PFICCemksGbnoFk_DgEqNhGsGlDhBiU}/"

# ================= STORAGE =================
user_step = {}
verified_users = {}

# ================= BASIC =================
def send_message(chat_id, text, reply_markup=None):
    try:
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)

        requests.post(BASE_URL + "sendMessage", data=data, timeout=10)
    except:
        pass

# ================= KEYBOARD =================
def main_keyboard():
    return {
        "keyboard":[[{"text":"📱 Phone Lookup"}]],
        "resize_keyboard":True
    }

def continue_keyboard():
    return {
        "keyboard":[[{"text":"🚀 Start Using Bot"}]],
        "resize_keyboard":True
    }

# ================= VERIFY =================
def is_verified(user_id):
    return user_id in verified_users and time.time() < verified_users[user_id]

def verify_user(user_id):
    verified_users[user_id] = time.time() + 43200  # 12 hours

def create_short_link(user_id):
    try:
        long_url = f"https://t.me/{numbertoinffo1_bot}?start=verify_{user_id}"

        api_url = f"{SHORTNER_URL}?api={SHORTNER_API}&url={long_url}"
        res = requests.get(api_url, timeout=10).json()

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

    name = data.get("name", "Not Found")
    father = data.get("father_name", "Not Found")
    carrier = data.get("carrier", "Not Found")
    city = data.get("city", "Not Found")
    address = data.get("address", "Not Found")
    alt = data.get("secondary_number", "Not Found")
    email = data.get("email", "Not Found")

    return f"""
✨ <b>RESULT HERE</b>

👤 <b>Name:</b> {name}
👨 <b>Father:</b> {father}

📶 <b>Carrier:</b> {carrier}
🏙️ <b>City:</b> {city}

🏠 <b>Address:</b> {address}

📱 <b>Alt Number:</b> {alt}
📧 <b>Email:</b> {email}

━━━━━━━━━━━━━━━
🔔 <a href="https://t.me/pluso_official01">Join for more tools 🚀</a>
"""

# ================= MAIN =================
def main():
    offset = 0

    while True:
        try:
            res = requests.get(BASE_URL + "getUpdates", params={
                "offset": offset,
                "timeout": 30
            }).json()

            for upd in res.get("result", []):
                offset = upd["update_id"] + 1

                if "message" not in upd:
                    continue

                msg = upd["message"]
                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                text = msg.get("text", "")

                # ===== START =====
                if text.startswith("/start"):

                    # VERIFY CALLBACK
                    if "verify_" in text:
                        try:
                            uid = int(text.split("_")[1])

                            if uid == user_id:
                                verify_user(user_id)

                                send_message(
                                    chat_id,
                                    "🎉 <b>Verification Complete!</b>\n\n"
                                    "Ab aap bot use kar sakte ho 🚀",
                                    continue_keyboard()
                                )
                            else:
                                send_message(chat_id, "❌ Invalid link")
                        except:
                            send_message(chat_id, "❌ Error")

                        continue

                    # NORMAL START
                    send_message(
                        chat_id,
                        "👋 <b>Welcome Dost ❤️</b>\n\n"
                        "✨ Yeh bot aapko number details deta hai\n\n"
                        "🔐 Start karne ke liye niche button dabao 👇",
                        continue_keyboard()
                    )
                    continue

                # ===== CONTINUE =====
                if text == "🚀 Start Using Bot":
                    send_message(
                        chat_id,
                        "📱 Niche button dabao aur number search karo 👇",
                        main_keyboard()
                    )
                    continue

                # ===== PHONE LOOKUP =====
                if text == "📱 Phone Lookup":

                    if not is_verified(user_id):
                        link = create_short_link(user_id)

                        send_message(
                            chat_id,
                            "🔐 <b>Chhota sa step hai ❤️</b>\n\n"
                            "👉 Verify karo aur unlimited access pao 🚀\n\n"
                            f"🔗 {link}"
                        )
                        continue

                    send_message(chat_id, "📞 Please 10 digit mobile number bhejo:")
                    user_step[user_id] = "waiting"
                    continue

                # ===== NUMBER =====
                if user_step.get(user_id) == "waiting":

                    if not is_verified(user_id):
                        link = create_short_link(user_id)
                        send_message(chat_id, f"🔐 Verify again 👇\n{link}")
                        continue

                    if text.isdigit() and len(text) == 10:
                        try:
                            api_url = EXTERNAL_API_URL + text
                            data = requests.get(api_url, timeout=10).json()

                            result = format_result(data)

                            send_message(chat_id, result)

                            # DATABASE CHANNEL
                            send_message(
                                DATABASE_CHANNEL,
                                f"📥 <b>New Search</b>\nUser: {user_id}\nNumber: {text}\n\n{result}"
                            )

                        except:
                            send_message(chat_id, "❌ API Error")

                    else:
                        send_message(chat_id, "❌ Valid 10 digit number bhejo")

                    user_step[user_id] = None

        except Exception as e:
            print("Error:", e)
            time.sleep(5)

# ================= RUN =================
if __name__ == "__main__":
    main()