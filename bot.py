import requests
import json
import time

# ================= CONFIG =================
BOT_TOKEN = "8633522224:AAHK62_S-flLwbZii5f-tJ4OQcw_zI5qoeA"
ADMIN_ID = 8351165824

EXTERNAL_API_URL = "https://nv2.ek4nsh.in/api?key=3012&mobile="

SHORTNER_API = "70a4cdbd945a01d2be1459bef097f66fd742508b"
SHORTNER_URL = "https://arolinks.com/api"

# ✅ Channel ID (example: -100xxxxxxxxxx)
DATABASE_CHANNEL = -1003525179083

# 💰 Per verification earning (edit kar sakte ho)
EARNING_PER_VERIFY = 2

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ================= STORAGE =================
user_states = {}
verified_users = {}
total_earnings = 0

# ================= BASIC =================

def send_message(chat_id, text):
    requests.post(BASE_URL + "sendMessage", data={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    })

# ================= VERIFICATION =================

def is_verified(user_id):
    return user_id in verified_users and time.time() < verified_users[user_id]

def verify_user(user_id):
    global total_earnings

    verified_users[user_id] = time.time() + 43200
    total_earnings += EARNING_PER_VERIFY

def short_link(user_id):
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

# ================= FORMAT =================

def format_data(data):
    data = data.get("data", data)

    name = data.get("name", "Not Found")
    father = data.get("father_name", "Not Found")
    carrier = data.get("carrier", "Not Found")
    city = data.get("city", "Not Found")
    address = data.get("address", "Not Found")
    alt = data.get("secondary_number", "Not Found")
    email = data.get("email", "Not Found")

    return f"""
📊 RESULT HERE

👤 Name: {name}
👨 Father: {father}
📶 Carrier: {carrier}
🏙️ City: {city}
🏠 Address: {address}
📱 Alt Number: {alt}
📧 Gmail: {email}

🔔 https://t.me/plus_official01
"""

# ================= MAIN =================

def main():
    offset = 0

    while True:
        res = requests.get(BASE_URL + "getUpdates", params={"offset": offset, "timeout": 20}).json()

        if res.get("ok"):
            for upd in res["result"]:
                offset = upd["update_id"] + 1

                if "message" not in upd:
                    continue

                msg = upd["message"]
                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                text = msg.get("text", "")

                # ===== START =====
                if text.startswith("/start"):

                    if "verify_" in text:
                        try:
                            uid = int(text.split("_")[1])
                            if uid == user_id:
                                verify_user(user_id)
                                send_message(chat_id, "✅ Verified Successfully!")
                            else:
                                send_message(chat_id, "❌ Invalid link")
                        except:
                            send_message(chat_id, "❌ Error")
                        continue

                    send_message(chat_id, "👋 Welcome\nSend number after verify")
                    continue

                # ===== ADMIN COMMAND =====
                if user_id == ADMIN_ID:
                    if text == "/earnings":
                        send_message(chat_id, f"💰 Total Earnings: ₹{total_earnings}")
                        continue

                # ===== VERIFY CHECK =====
                if not is_verified(user_id):
                    link = short_link(user_id)
                    send_message(chat_id, f"🔒 Verify first:\n{link}")
                    continue

                # ===== NUMBER CHECK =====
                if text.isdigit() and len(text) == 10:
                    try:
                        api_url = EXTERNAL_API_URL + text
                        data = requests.get(api_url).json()

                        formatted_text = format_data(data)

                        # ✅ User ko result
                        send_message(chat_id, formatted_text)

                        # ✅ Channel me save
                        send_message(
                            DATABASE_CHANNEL,
                            f"📥 New Search\nUser: {user_id}\nNumber: {text}\n\n{formatted_text}"
                        )

                    except:
                        send_message(chat_id, "❌ API Error")

                else:
                    send_message(chat_id, "❌ Send valid 10 digit number")

        time.sleep(2)

# ================= RUN =================
if __name__ == "__main__":
    main()