import requests
import time

# ================= CONFIG =================
BOT_TOKEN = "8633522224:AAHK62_S-flLwbZii5f-tJ4OQcw_zI5qoeA"
ADMIN_ID = 8351165824

EXTERNAL_API_URL = "https://nv2.ek4nsh.in/api?key=3012&mobile="

# SHORTNER
SHORTNER_API = "70a4cdbd945a01d2be1459bef097f66fd742508b"
SHORTNER_URL = "https://arolinks.com"

# ✅ BOT USERNAME (WITHOUT @)
BOT_USERNAME = "numtoinffo_bot"

DATABASE_CHANNEL = -1003525179083

EARNING_PER_VERIFY = 0.5

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ================= STORAGE =================
verified_users = {}
total_earnings = 0
total_verified = 0

# ================= BASIC =================
def send_message(chat_id, text):
    try:
        requests.post(BASE_URL + "sendMessage", data={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        })
    except:
        pass

# ================= VERIFICATION =================
def is_verified(user_id):
    return user_id in verified_users and time.time() < verified_users[user_id]

def verify_user(user_id):
    global total_earnings, total_verified
    verified_users[user_id] = time.time() + 43200
    total_earnings += EARNING_PER_VERIFY
    total_verified += 0.5

def short_link(user_id):
    # ✅ SAFE DEEP LINK (NO ERROR)
    bot_link = f"https://t.me/{numtoinffo_bot}?start=verify_{user_id}"

    try:
        api_url = f"{SHORTNER_URL}/api?api={SHORTNER_API}&url={bot_link}"
        res = requests.get(api_url).json()

        if res.get("status") == "success":
            return res.get("shortenedUrl")
        else:
            return bot_link

    except:
        return bot_link

# ================= FORMAT =================
def format_data(data):
    try:
        data = data.get("data", data)
    except:
        data = {}

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

⚙️ Bot Status: Running ✅
"""

# ================= MAIN =================
def main():
    offset = 0

    while True:
        try:
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

                        # VERIFY HANDLE
                        if "verify_" in text:
                            try:
                                uid = int(text.split("_")[1])

                                if uid == user_id:
                                    verify_user(user_id)
                                    send_message(chat_id, "✅ Verified Successfully!\n\n📱 Ab number bhejo")
                                else:
                                    send_message(chat_id, "❌ Invalid link")

                            except:
                                send_message(chat_id, "❌ Verification error")

                            continue

                        # WELCOME
                        verify_link = short_link(user_id)

                        send_message(chat_id, f"""
👋 Welcome to Premium Lookup Bot

🔐 Pehle verify karo
📱 Fir apna number bhejo

⚡ Fast • Secure • Premium Data

👇 Verify Here:
{verify_link}
""")
                        continue

                    # ===== ADMIN =====
                    if user_id == ADMIN_ID:
                        if text == "/dashboard":
                            send_message(chat_id, admin_dashboard())
                            continue

                        if text == "/earnings":
                            send_message(chat_id, f"💸 Earnings: ₹{total_earnings}")
                            continue

                    # ===== VERIFY CHECK =====
                    if not is_verified(user_id):
                        send_message(chat_id, f"🔒 Verify first:\n{short_link(user_id)}")
                        continue

                    # ===== NUMBER =====
                    if text.isdigit() and len(text) == 10:
                        try:
                            api_url = EXTERNAL_API_URL + text
                            data = requests.get(api_url).json()

                            result = format_data(data)

                            send_message(chat_id, result)

                            # SAVE DATA
                            send_message(
                                DATABASE_CHANNEL,
                                f"📥 New Search\nUser: {user_id}\nNumber: {text}\n{result}"
                            )

                        except:
                            send_message(chat_id, "❌ API Error")

                    else:
                        send_message(chat_id, "❌ Send valid 10 digit number")

        except Exception as e:
            print("Error:", e)

        time.sleep(2)

# ================= RUN =================
if __name__ == "__main__":
    main()
