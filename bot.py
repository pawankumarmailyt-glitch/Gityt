import requests
import time

# ================= CONFIG =================
BOT_TOKEN = "8633522224:AAHK62_S-flLwbZii5f-tJ4OQcw_zI5qoeA"
ADMIN_ID = 8351165824

# ✅ API
EXTERNAL_API_URL = "https://nv2.ek4nsh.in/api?key=3012&mobile="

# ✅ SHORTNER FIXED
SHORTNER_API = "70a4cdbd945a01d2be1459bef097f66fd742508b"
SHORTNER_URL = "https://arolinks.com"

# ✅ YOUR BOT USERNAME (WITHOUT @)
BOT_USERNAME = "numtoinffo_bot"

DATABASE_CHANNEL = -1003525179083

EARNING_PER_VERIFY = 0.90

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ================= STORAGE =================
verified_users = {}
total_earnings = 0
total_verified = 0

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
    global total_earnings, total_verified
    verified_users[user_id] = time.time() + 43200  # 12 hours
    total_earnings += EARNING_PER_VERIFY
    total_verified += 1

def short_link(user_id):
    # ✅ FIXED DEEP LINK
    long_url = f"https://t.me/{numtoinffo_bot}?start=verify_{user_id}"

    try:
        api = f"{SHORTNER_URL}/api?api={SHORTNER_API}&url={long_url}"
        res = requests.get(api).json()

        print("Shortner Response:", res)

        if res.get("status") == "success":
            return res.get("shortenedUrl")
        else:
            return long_url

    except Exception as e:
        print("Shortner Error:", e)
        return long_url

# ================= FORMAT =================

def format_data(data):
    data = data.get("data", data)

    return f"""
📊 RESULT HERE

👤 Name: {data.get("name","Not Found")}
👨 Father: {data.get("father_name","Not Found")}
📶 Carrier: {data.get("carrier","Not Found")}
🏙️ City: {data.get("city","Not Found")}
🏠 Address: {data.get("address","Not Found")}
📱 Alt Number: {data.get("secondary_number","Not Found")}
📧 Gmail: {data.get("email","Not Found")}

━━━━━━━━━━━━━━━━━━
🔔 https://t.me/plus_official01
━━━━━━━━━━━━━━━━━━
"""

# ================= DASHBOARD =================

def admin_dashboard():
    return f"""
📊 ADMIN DASHBOARD

👥 Total Verified Users: {total_verified}
💸 Total Earnings: ₹{total_earnings}

⚙️ Status: Running ✅
"""

# ================= MAIN =================

def main():
    offset = 0

    while True:
        res = requests.get(BASE_URL + "getUpdates", params={"offset": offset}).json()

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

                    # ✅ VERIFY HANDLER
                    if "verify_" in text:
                        try:
                            uid = int(text.split("_")[1])

                            if uid == user_id:
                                verify_user(user_id)
                                send_message(chat_id, "✅ Verification Successful!\n\n📱 Ab apna 10 digit number bhejo")
                            else:
                                send_message(chat_id, "❌ Invalid verification link")

                        except:
                            send_message(chat_id, "❌ Verification error")

                        continue

                    # 🔥 NEW WELCOME UI
                    send_message(chat_id, f"""
👋 Welcome to Premium Lookup Bot

🔐 Use karne ke liye verify zaroori hai
📱 Verify ke baad number bhejo

⚡ Fast • Secure • Premium Data

👇 Click karke verify karo:
{short_link(user_id)}
""")
                    continue

                # ===== ADMIN =====
                if user_id == ADMIN_ID:
                    if text == "/earnings":
                        send_message(chat_id, f"💸 Total Earnings: ₹{total_earnings}")
                        continue

                    if text == "/dashboard":
                        send_message(chat_id, admin_dashboard())
                        continue

                # ===== VERIFY CHECK =====
                if not is_verified(user_id):
                    send_message(chat_id, f"🔒 Please verify first:\n{short_link(user_id)}")
                    continue

                # ===== NUMBER INPUT =====
                if text.isdigit() and len(text) == 10:
                    try:
                        api_url = EXTERNAL_API_URL + text
                        data = requests.get(api_url).json()

                        result = format_data(data)

                        send_message(chat_id, result)

                        # ✅ Save to channel
                        send_message(
                            DATABASE_CHANNEL,
                            f"📥 New Search\nUser: {user_id}\nNumber: {text}\n{result}"
                        )

                    except:
                        send_message(chat_id, "❌ API Error")

                else:
                    send_message(chat_id, "❌ Please send valid 10 digit mobile number")

        time.sleep(2)

# ================= RUN =================
if __name__ == "__main__":
    main()
